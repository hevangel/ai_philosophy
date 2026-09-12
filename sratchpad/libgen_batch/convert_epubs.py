"""Convert philosophy/pop-culture epubs to per-chapter markdown files.

Reads every *.epub in philosophy_pop_culture/, splits by the book's own TOC
(nav/ncx) so each essay/chapter becomes one markdown file:

  markdown/<book dir>/chNN - <chapter title>.md

plus a _meta.json per book (chapter list, spine order) for the analysis step.
"""
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag, ProcessingInstruction
from ebooklib import epub, ITEM_DOCUMENT

BLOCK = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote",
         "li", "td", "section", "article", "figcaption", "ul", "ol", "table", "tr"}

SRC = Path(r"B:\ai_philosophy\philosophy_pop_culture")
OUT_ROOT = SRC / "markdown"


def clean_title(t: str) -> str:
    t = re.sub(r"\s+", " ", t or "").strip()
    return NAME_OK.sub("_", t).strip(" ._")[:80] or "untitled"


NAME_OK = re.compile(r"[^A-Za-z0-9 ()&',!.\-]")


def html_to_markdown(soup: BeautifulSoup) -> str:
    out: list[str] = []

    def para(node):
        txt = node.get_text(" ", strip=True)
        if txt:
            out.append(txt + "\n")

    def walk(node):
        if isinstance(node, Tag) and node.name is None:
            return
        if not isinstance(node, Tag):
            return
        name = (node.name or "").lower()
        if name in ("style", "script", "head"):
            return
        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            txt = node.get_text(" ", strip=True)
            if txt:
                out.append("\n" + "#" * min(int(name[1]) + 1, 6) + " " + txt + "\n")
            return
        if name == "p":
            para(node)
            return
        if name == "blockquote":
            txt = node.get_text(" ", strip=True)
            if txt:
                out.append("\n> " + txt + "\n")
            return
        if name == "li":
            txt = node.get_text(" ", strip=True)
            if txt:
                out.append("- " + txt + "\n")
            return
        if name in ("div", "section", "article", "td", "figcaption"):
            has_block_child = any(
                isinstance(c, Tag) and (c.name or "").lower() in BLOCK
                for c in node.children)
            if has_block_child:
                for c in node.children:
                    walk(c)
            else:
                para(node)
            return
        for child in node.children:
            walk(child)

    # strip processing instructions (page-number markers like <?dp n="18" ...?>)
    for pi in list(soup.find_all(string=lambda s: isinstance(s, ProcessingInstruction))):
        pi.extract()
    body = soup.body or soup
    walk(body)
    return "\n".join(out).strip()


def get_toc_entries(book):
    """Return ordered [(href_base, title)] from nav or ncx."""
    entries = []
    try:
        for item in book.toc:
            if isinstance(item, tuple):
                section, children = item
                entries.append((section.href.split("#")[0], section.title or ""))
                for ch in children:
                    entries.append((ch.href.split("#")[0], ch.title or ""))
            elif hasattr(item, "href"):
                entries.append((item.href.split("#")[0], item.title or ""))
    except Exception:
        pass
    return entries


def convert_book(epub_path: Path) -> Path | None:
    try:
        book = epub.read_epub(str(epub_path), options={"ignore_ncx": False})
    except Exception as e:
        print(f"  [FAIL] read {epub_path.name}: {type(e).__name__}: {str(e)[:80]}", flush=True)
        return None

    book_dir = OUT_ROOT / epub_path.stem
    book_dir.mkdir(parents=True, exist_ok=True)

    # map href_base -> document item
    docs = {}
    for item in book.get_items_of_type(ITEM_DOCUMENT):
        href = item.get_name().split("/")[-1]
        docs[href] = item

    toc = get_toc_entries(book)
    # order chapters by spine for stable numbering
    spine_ids = [sid for sid, _ in book.spine if isinstance(sid, str)]
    id_to_href = {}
    for item in book.get_items_of_type(ITEM_DOCUMENT):
        id_to_href[item.get_id()] = item.get_name().split("/")[-1]

    ordered = []
    seen = set()
    toc_map = {}
    for href, title in toc:
        if href and href in docs and href not in toc_map:
            toc_map[href] = title

    for sid in spine_ids:
        href = id_to_href.get(sid)
        if href and href in docs and href not in seen:
            seen.add(href)
            ordered.append((href, toc_map.get(href, "")))

    meta = {"book": epub_path.stem, "chapters": []}
    n = 0
    for href, toc_title in ordered:
        item = docs[href]
        try:
            soup = BeautifulSoup(item.get_content().decode("utf-8", "ignore"), "lxml")
        except Exception:
            continue
        # chapter title: TOC title wins, else first heading
        head = soup.find(["h1", "h2", "h3"])
        title = toc_title or (head.get_text(" ", strip=True) if head else href)
        text = html_to_markdown(soup)
        if len(text) < 400:  # cover/blank/sep pages
            continue
        n += 1
        ch_file = book_dir / (f"ch{n:02d} - {clean_title(title)}.md")
        header = (f"# {title}\n\n"
                  f"*Source: {epub_path.stem} — chapter {n}*\n\n")
        ch_file.write_text(header + text, encoding="utf-8")
        meta["chapters"].append({"n": n, "title": title, "file": ch_file.name,
                                 "words": len(text.split())})

    meta_path = book_dir / "_meta.json"
    meta_path.write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"  [OK] {epub_path.stem}: {len(meta['chapters'])} chapters", flush=True)
    return book_dir


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    epubs = sorted(SRC.glob("*.epub"))
    print(f"converting {len(epubs)} epubs...", flush=True)
    ok = 0
    for i, p in enumerate(epubs):
        if (OUT_ROOT / p.stem / "_meta.json").exists():
            ok += 1
            continue  # already converted (resumable)
        print(f"[{i+1}/{len(epubs)}] {p.stem}", flush=True)
        if convert_book(p):
            ok += 1
    print(f"done: {ok}/{len(epubs)} books converted", flush=True)


if __name__ == "__main__":
    main()
