"""Build full per-chapter manifest + balanced reading work units.

Reads every extracted chapter file once, emits:
  full_manifest.json  [{book, chapters: [{n, file, title, words}]}]
  work_units.json     [{unit, book, part, parts, path, chapters: [{n, file, words}]}]
Books with too much content are split into balanced parts (chapter ranges).
The image-only book (071) is excluded from reading units.
"""
import json
import re
from pathlib import Path

MD_DIR = Path(r"B:\ai_philosophy\philosophy_pop_culture\markdown").resolve()
OUT_DIR = Path(r"B:\ai_philosophy\sratchpad\popcult_index").resolve()

CH_RE = re.compile(r"^ch(\d+) - (.*?)\.md$", re.I)
WORD_RE = re.compile(r"[A-Za-z\u00C0-\u024F']+")

MAX_UNIT_WORDS = 90000
MAX_UNIT_CHAPS = 42
EXCLUDED = {"071 - The Catcher in the Rye and Philosophy - A Book for Bastards, Morons, and Madmen"}


def chapter_words(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    body = re.sub(r"^#[^\n]*\n(?:\s*\n)*\*Source:[^\n]*\n(?:\s*\n)*", "", text, count=1)
    return len(WORD_RE.findall(body))


def main():
    manifest = []
    units = []
    for book_dir in sorted(MD_DIR.iterdir()):
        if not book_dir.is_dir() or book_dir.name in EXCLUDED:
            continue
        chapters = []
        for f in book_dir.iterdir():
            m = CH_RE.match(f.name)
            if m:
                chapters.append({"n": int(m.group(1)), "file": f.name,
                                 "title": m.group(2), "words": chapter_words(f)})
        chapters.sort(key=lambda c: c["n"])
        manifest.append({"book": book_dir.name, "chapters": chapters})
        content = [c for c in chapters if c["words"] >= 200]
        cw = sum(c["words"] for c in content)
        n_parts = max(1, -(-cw // MAX_UNIT_WORDS), -(-len(content) // MAX_UNIT_CHAPS))
        # balanced consecutive cuts: place k-th cut at the chapter boundary
        # nearest to k*cw/n_parts cumulative words
        bounds = [0]
        acc = 0
        k = 1
        for i, c in enumerate(content):
            acc += c["words"]
            if k < n_parts and acc >= cw * k / n_parts:
                bounds.append(i + 1)
                k += 1
        bounds.append(len(content))
        ranges = []
        for i in range(n_parts):
            lo = content[bounds[i]]["n"]
            hi = content[bounds[i + 1] - 1]["n"] if i + 1 < len(bounds) else 10 ** 6
            if i == n_parts - 1:
                hi = 10 ** 6
            ranges.append((lo, hi))
        for i, (lo, hi) in enumerate(ranges):
            unit_chs = [c for c in chapters
                        if c["n"] >= lo and (c["n"] <= hi or n_parts == 1)]
            units.append({
                "unit": "u%03d" % len(units),
                "book": book_dir.name,
                "part": "%d/%d" % (i + 1, n_parts) if n_parts > 1 else "1/1",
                "path": str(book_dir),
                "range": [lo, hi] if n_parts > 1 else None,
                "chapters": [{"n": c["n"], "file": c["file"], "words": c["words"]}
                             for c in unit_chs],
            })
    (OUT_DIR / "full_manifest.json").write_text(json.dumps(manifest, indent=1),
                                                encoding="utf-8")
    (OUT_DIR / "work_units.json").write_text(json.dumps(units, indent=1),
                                             encoding="utf-8")
    total_ch = sum(len(m["chapters"]) for m in manifest)
    content_ch = sum(1 for m in manifest for c in m["chapters"] if c["words"] >= 200)
    print("books: %d  chapters: %d  content chapters(>=200w): %d  units: %d"
          % (len(manifest), total_ch, content_ch, len(units)))
    big = [u for u in units if sum(c["words"] for c in u["chapters"]) > 110000]
    print("units over 110k words:", len(big))
    for u in big[:5]:
        print("  ", u["unit"], u["book"][:50], sum(c["words"] for c in u["chapters"]))


if __name__ == "__main__":
    main()
