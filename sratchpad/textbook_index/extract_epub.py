"""Re-extract every EPUB into per-chapter markdown (one file per spine doc).

Textbook-corpus variant of the popcult extractor: ROOT points at
data/philosophy_textbooks; manifest lands in sratchpad/textbook_index/.
Overwrites the markdown/ extraction cache so that spine docs and chapter
files correspond 1:1, then verification against the EPUB is exact.
"""
import json
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import epub_lib

ROOT = Path(r"B:\ai_philosophy\data\philosophy_textbooks").resolve()
EPUB_DIR = ROOT / "epub"
MD_DIR = ROOT / "markdown"
MANIFEST_PATH = Path(r"B:\ai_philosophy\sratchpad\textbook_index\corpus_manifest.json").resolve()

CH_RE = re.compile(r"^ch(\d+)")
BLOCK_RE = re.compile(r"<(/?)(h[1-6]|p|div|li|blockquote|tr)[^>]*>", re.I)
INLINE_EM = re.compile(r"<(em|i)[^>]*>(.*?)</\1>", re.I | re.S)
INLINE_ST = re.compile(r"<(strong|b)[^>]*>(.*?)</\1>", re.I | re.S)
TAG_RE = re.compile(r"<[^>]+>")
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)
HEAD_RE = re.compile(r"<h[1-3][^>]*>(.*?)</h[1-3]>", re.I | re.S)


def checked_path(base, rel):
    p = (base / rel).resolve()
    b = base.resolve()
    import os
    if os.path.commonpath([str(p), str(b)]) != str(b):
        raise ValueError("resolved path outside allowed root: %s" % p)
    return p


def safe_stem(stem):
    if not stem or stem in (os_curdir(), os_pardir()):
        raise ValueError("unsafe book stem: %r" % stem)
    for mark in (chr(92), "/", ":"):
        if mark in stem:
            raise ValueError("unsafe book stem: %r" % stem)
    return stem


def os_curdir():
    import os
    return os.curdir


def os_pardir():
    import os
    return os.pardir


def sanitize_title(t, max_len=110):
    t = epub_lib.html_unescape(t or "").strip()
    t = re.sub(r"\s+", " ", t)
    for ch in ':"/?*<>|' + chr(92):
        t = t.replace(ch, " ")
    t = re.sub(r"\s+", " ", t).strip().strip(".")
    return t[:max_len].rstrip()


def inline_to_text(html):
    html = INLINE_EM.sub(lambda m: " *" + TAG_RE.sub("", m.group(2)) + "* ", html)
    html = INLINE_ST.sub(lambda m: " **" + TAG_RE.sub("", m.group(2)) + "** ", html)
    text = epub_lib.html_unescape(TAG_RE.sub(" ", html))
    return re.sub(r"\s+", " ", text).strip()


def body_to_markdown(raw_body):
    """Convert inner-body HTML to plain markdown-ish text."""
    body = re.sub(r"<!--.*?-->", " ", raw_body, flags=re.S)
    body = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", " ", body, flags=re.S | re.I)
    body = re.sub(r"<br[^>]*>", "\n\n", body, flags=re.I)
    out = []
    buf = []

    def flush():
        if buf:
            text = inline_to_text("".join(buf))
            buf.clear()
            if text:
                out.append(text)

    level = 0
    quote = 0
    for mt in BLOCK_RE.finditer(body):
        closing, tag = mt.group(1), mt.group(2).lower()
        if closing:
            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                flush()
                if out:
                    out[-1] = "#" * min(int(tag[1]), 4) + " " + out[-1]
            elif tag in ("p", "div", "li", "tr", "td"):
                flush()
            elif tag == "blockquote":
                flush()
                quote = max(0, quote - 1)
        else:
            if tag in ("p", "div", "li", "tr", "td"):
                flush()
            elif tag == "blockquote":
                flush()
                quote += 1
        # capture text between this tag and the next
        start = mt.end()
        nxt = BLOCK_RE.search(body, start)
        buf.append(body[start:nxt.start()] if nxt else body[start:])
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and not closing:
            level = int(tag[1])
    flush()
    if quote:
        out = ["\n\n".join("> " + ln for ln in blk.split("\n\n")) if blk else blk
               for blk in out]
    text = "\n\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def doc_title(zf, opf_dir, href, toc_titles):
    base = href.rsplit("/", 1)[-1]
    if base in toc_titles and toc_titles[base]:
        return toc_titles[base]
    try:
        html = zf.read(opf_dir + href).decode("utf-8", "replace")
    except Exception:
        return base.rsplit(".", 1)[0]
    m = TITLE_RE.search(html) or HEAD_RE.search(html)
    if m:
        t = epub_lib.html_unescape(re.sub(r"<[^>]+>", " ", m.group(1))).strip()
        t = re.sub(r"\s+", " ", t)
        if t and not t.lower().startswith("untitled"):
            return t
    return base.rsplit(".", 1)[0]


def extract_book(epub_path, md_root):
    stem = safe_stem(epub_path.name[:-5])
    zf = zipfile.ZipFile(str(epub_path))
    opf_dir, manifest, spine = epub_lib.load_opf(zf)
    toc_titles = epub_lib.load_toc_titles(zf, opf_dir, manifest)
    book_dir = checked_path(md_root, stem)
    book_dir.mkdir(parents=True, exist_ok=True)
    # clear stale extraction files
    for old in book_dir.iterdir():
        if CH_RE.match(old.name) and old.name.lower().endswith(".md"):
            old.unlink()
    chapters = []
    n = 0
    for m in spine:
        is_html = ("html" in m["media-type"]
                   or m["href"].lower().endswith((".xhtml", ".html", ".htm")))
        if not is_html:
            continue
        info = epub_lib.doc_text(zf, opf_dir, m["href"])
        if info is None:
            continue
        n += 1
        title = sanitize_title(doc_title(zf, opf_dir, m["href"], toc_titles))
        fname = "ch%02d - %s.md" % (n, title or ("section-%d" % n))
        body_md = body_to_markdown(info["raw"])
        header = "# %s\n\n*Source: %s — chapter %d*\n\n" % (title or "Section %d" % n,
                                                            stem, n)
        fpath = checked_path(book_dir, fname)
        fpath.write_text(header + body_md + "\n", encoding="utf-8")
        chapters.append({"n": n, "file": fname, "title": title,
                         "toc_title": toc_titles.get(m["href"].rsplit("/", 1)[-1], ""),
                         "words": info["words"]})
    zf.close()
    return {"book": stem, "chapters": chapters,
            "total_words": sum(c["words"] for c in chapters)}


def main():
    epubs = sorted(p for p in EPUB_DIR.iterdir() if p.name.lower().endswith(".epub"))
    corpus = []
    for i, ep in enumerate(epubs):
        try:
            entry = extract_book(ep, MD_DIR)
            corpus.append({"book": entry["book"], "n_chapters": len(entry["chapters"]),
                           "total_words": entry["total_words"]})
            if (i + 1) % 25 == 0 or i + 1 == len(epubs):
                print("extracted %d/%d" % (i + 1, len(epubs)))
        except Exception as e:
            print("ERROR %s: %r" % (ep.name, e))
    MANIFEST_PATH.write_text(json.dumps(corpus, indent=1, ensure_ascii=False), encoding="utf-8")
    print("books extracted: %d  total chapters: %d" % (
        len(corpus), sum(c["n_chapters"] for c in corpus)))


if __name__ == "__main__":
    main()
