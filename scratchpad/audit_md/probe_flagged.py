"""Probe the flagged books' epubs: TOC-expected chapter count vs spine doc
granularity, plus metadata title (duplicate detection)."""
import re
import sys
from pathlib import Path

POP = Path(r"B:\ai_philosophy\scratchpad\popcult_index").resolve()
sys.path.insert(0, str(POP))
import epub_lib

ROOT = Path(r"B:\ai_philosophy\data\philosophy_pop_culture").resolve()
EPUB_DIR = ROOT / "epub"

FLAGGED = [
    "025", "050", "203", "208", "222", "224", "236",
    "241", "242", "243", "251", "284", "301", "308",
]
CH_LABEL = re.compile(r"^\d{1,2}\s*[-–.:'\u2019\u2013]")


def main():
    for p in sorted(EPUB_DIR.iterdir()):
        if not p.name.lower().endswith(".epub"):
            continue
        num = p.name[:3]
        if num not in FLAGGED:
            continue
        try:
            docs = epub_lib.book_stats(p)
        except Exception as e:
            print(num, "UNREADABLE", repr(e)[:80])
            continue
        # metadata title
        title = ""
        try:
            import zipfile
            zf = zipfile.ZipFile(str(p))
            opf_dir, manifest, spine = epub_lib.load_opf(zf)
            for m in manifest.values():
                if m["media-type"] == "application/oebps-package+xml":
                    raw = zf.read(opf_dir + m["href"]).decode("utf-8", "replace")
                    t = re.search(r"<dc:title[^>]*>([^<]+)<", raw)
                    if t:
                        title = t.group(1)
                    break
        except Exception:
            pass
        nch_labels = sum(1 for d in docs if CH_LABEL.match(d["title"] or ""))
        big = sorted(docs, key=lambda d: -d["words"])[:5]
        print(f"{num} | dc:title={title[:60]!r}")
        print(f"    spine_html={len(docs)} toc_numbered_labels={nch_labels} "
              f"total_words={sum(d['words'] for d in docs)}")
        for d in big:
            print(f"      {d['words']:>7}w  {d['base'][-30:]:32} {str(d['title'])[:55]}")


if __name__ == "__main__":
    main()
