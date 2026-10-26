"""Batch re-extract repaired books from their (re-downloaded) epubs and rebuild
their manifest entries + reading units, reusing the books' existing unit ids in
order (allocating fresh uNNN ids past u450 only if a book now needs more units).

Usage: py -3 rebuild_units_batch.py 50 208 242
"""
import json
import re
import sys
from pathlib import Path

POP = Path(r"B:\ai_philosophy\scratchpad\popcult_index").resolve()
sys.path.insert(0, str(POP))
import epub_lib

def load_toc_titles_first(zf, opf_dir, manifest):
    """epub_lib.load_toc_titles with ncx keep-FIRST-label-per-basename (this
    epub family's sub-section navPoints share the chapter file's basename and
    would otherwise overwrite the chapter title)."""
    titles = {}
    ncx_id = next((iid for iid, m in manifest.items()
                   if m["media-type"] == "application/x-dtbncx+xml"), None)
    if ncx_id:
        try:
            root = epub_lib.safe_fromstring(zf.read(opf_dir + manifest[ncx_id]["href"]))
            NS = epub_lib.NS
            for np in root.iter("{%s}navPoint" % NS["ncx"]):
                label = None
                for nl in np.iter("{%s}text" % NS["ncx"]):
                    label = nl.text
                    break
                content = np.find("{%s}content" % NS["ncx"])
                if content is not None and label:
                    src = content.get("src", "").split("#")[0]
                    key = epub_lib.url_unquote(src).rsplit("/", 1)[-1]
                    if key and key not in titles:
                        titles[key] = label.strip()
        except Exception:
            pass
    for k, v in _orig_load_toc_titles(zf, opf_dir, manifest).items():
        titles.setdefault(k, v)
    return titles

_orig_load_toc_titles = epub_lib.load_toc_titles
epub_lib.load_toc_titles = load_toc_titles_first
import extract_epub

ROOT = Path(r"B:\ai_philosophy\data\philosophy_pop_culture").resolve()
EPUB_DIR = ROOT / "epub"
MD_ROOT = ROOT / "markdown"
BASE = Path(r"B:\ai_philosophy\scratchpad\popcult_index").resolve()
MANIFEST = BASE / "full_manifest.json"

CH_RE = re.compile(r"^ch(\d+) - (.*?)\.md$", re.I)
WORD_RE = re.compile(r"[A-Za-z\u00C0-\u024F']+")
MAX_UNIT_WORDS = 90000
MAX_UNIT_CHAPS = 42


def chapter_words(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    body = re.sub(r"^#[^\n]*\n(?:\s*\n)*\*Source:[^\n]*\n(?:\s*\n)*", "", text, count=1)
    return len(WORD_RE.findall(body))


def main():
    argv = [a for a in sys.argv[1:]]
    from_md = "--from-md" in argv
    nums = [int(a) for a in argv if a.isdigit()]
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    # next fresh unit id
    used = {int(p.stem[1:]) for p in (BASE / "units").glob("u*.json")}
    next_new = max(used) + 1

    for num in nums:
        epubs = [p for p in EPUB_DIR.iterdir()
                 if p.name.startswith(f"{num:03d} - ") and p.name.lower().endswith(".epub")]
        ep = epubs[0] if epubs else None
        if ep is None and not from_md:
            print(f"#{num:03d}: no epub found")
            continue
        if from_md:
            mds = [p for p in MD_ROOT.iterdir() if p.is_dir() and p.name.startswith(f"{num:03d} - ")]
            if not mds:
                print(f"#{num:03d}: no markdown folder found")
                continue
            book = mds[0].name
        else:
            entry = extract_epub.extract_book(ep, MD_ROOT)
            book = entry["book"]
        chapters = []
        for f in (MD_ROOT / book).iterdir():
            m = CH_RE.match(f.name)
            if m:
                chapters.append({"n": int(m.group(1)), "file": f.name,
                                 "title": m.group(2), "words": chapter_words(f)})
        chapters.sort(key=lambda c: c["n"])
        idx = next((i for i, b in enumerate(manifest) if b["book"] == book), None)
        if idx is None:
            print(f"#{num:03d}: book not in manifest ({book[:50]})")
            continue
        manifest[idx] = {"book": book, "chapters": chapters}

        # old units for this book, in part order
        old_ids = []
        for p in sorted((BASE / "units").glob("u*.json")):
            u = json.loads(p.read_text(encoding="utf-8"))
            if u.get("book") == book:
                old_ids.append(p.stem)
                (BASE / "units" / p.name).unlink()
                (BASE / "notes" / p.name).unlink(missing_ok=True)
        content = [c for c in chapters if c["words"] >= 200]
        cw = sum(c["words"] for c in content)
        n_parts = max(1, -(-cw // MAX_UNIT_WORDS), -(-len(content) // MAX_UNIT_CHAPS))
        ids = (old_ids + [f"u{n}" for n in range(next_new, next_new + n_parts - len(old_ids))])
        next_new += max(0, n_parts - len(old_ids))
        print(f"#{num:03d} {book[:55]}: {len(chapters)} chapters, {len(content)} content, "
              f"{cw} cw -> {n_parts} unit(s) {ids}")

        bounds = [0]
        acc = 0
        k = 1
        for i, c in enumerate(content):
            acc += c["words"]
            if k < n_parts and acc >= cw * k / n_parts:
                bounds.append(i + 1)
                k += 1
        bounds.append(len(content))
        for i in range(n_parts):
            lo = content[bounds[i]]["n"]
            hi = 10 ** 6 if i == n_parts - 1 else content[bounds[i + 1] - 1]["n"]
            if i == 0:
                lo = chapters[0]["n"]
            unit_chs = [c for c in chapters if lo <= c["n"] <= hi]
            unit = {
                "unit": ids[i],
                "book": book,
                "part": "%d/%d" % (i + 1, n_parts) if n_parts > 1 else "1/1",
                "path": str(MD_ROOT / book),
                "range": [lo, hi] if n_parts > 1 else None,
                "chapters": [{"n": c["n"], "file": c["file"], "words": c["words"]}
                             for c in unit_chs],
                "content": [c["n"] for c in content if lo <= c["n"] <= hi],
            }
            (BASE / "units" / f"{ids[i]}.json").write_text(
                json.dumps(unit, ensure_ascii=False, indent=1), encoding="utf-8")

    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print("manifest updated")


if __name__ == "__main__":
    main()
