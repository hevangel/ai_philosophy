"""One-off: re-extract ONLY book 002 from its (re-downloaded) epub.

Reuses scratchpad/popcult_index/extract_epub.py's extract_book() so the
markdown format matches the rest of the corpus exactly. Prints the chapter
list for inspection.
"""
import json
import sys
from pathlib import Path

POP = Path(r"B:\ai_philosophy\scratchpad\popcult_index").resolve()
sys.path.insert(0, str(POP))
import epub_lib
import extract_epub

# This epub's NCX lists sub-section navPoints that share the chapter file's
# basename; epub_lib.load_toc_titles lets them overwrite the chapter title.
# Keep the FIRST label per basename instead (the chapter-level one).
def load_toc_titles_first(zf, opf_dir, manifest):
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

EPUB = Path(r"B:\ai_philosophy\philosophy_pop_culture\epub\002 - The Simpsons and Philosophy - The D'oh! of Homer.epub").resolve()
MD_ROOT = Path(r"B:\ai_philosophy\philosophy_pop_culture\markdown").resolve()

entry = extract_epub.extract_book(EPUB, MD_ROOT)
print("book:", entry["book"])
print("chapters:", len(entry["chapters"]), "| total words:", entry["total_words"])
for c in entry["chapters"]:
    print(f"  {c['n']:>2} {c['words']:>6}w  {c['file'][:80]}")
