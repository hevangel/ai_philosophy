"""One-off: rebuild book 002's manifest entry and reading units after the
re-extraction from the clean epub.

- Recomputes 002's chapter list from markdown/ (same rules as
  scratchpad/popcult_index/build_work_units.py).
- Replaces 002's entry in full_manifest.json (keeping its position).
- Deletes the blob-era units u439/u440 and their notes.
- Rebuilds u439/u440 as balanced units over the new chapters (same split
  rule: <=90k content words / <=42 content chapters), with the same schema
  as the existing units (unit, book, part, path, range, chapters, content).
"""
import json
import re
from pathlib import Path

MD_BOOK = Path(r"B:\ai_philosophy\philosophy_pop_culture\markdown\002 - The Simpsons and Philosophy - The D'oh! of Homer").resolve()
BASE = Path(r"B:\ai_philosophy\scratchpad\popcult_index").resolve()
MANIFEST = BASE / "full_manifest.json"
U439 = BASE / "units" / "u439.json"
U440 = BASE / "units" / "u440.json"
N439 = BASE / "notes" / "u439.json"
N440 = BASE / "notes" / "u440.json"
UNIT_PATHS = {"u439": U439, "u440": U440}

BOOK = MD_BOOK.name
CH_RE = re.compile(r"^ch(\d+) - (.*?)\.md$", re.I)
WORD_RE = re.compile(r"[A-Za-z\u00C0-\u024F']+")
MAX_UNIT_WORDS = 90000
MAX_UNIT_CHAPS = 42


def chapter_words(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    body = re.sub(r"^#[^\n]*\n(?:\s*\n)*\*Source:[^\n]*\n(?:\s*\n)*", "", text, count=1)
    return len(WORD_RE.findall(body))


chapters = []
for f in MD_BOOK.iterdir():
    m = CH_RE.match(f.name)
    if m:
        chapters.append({"n": int(m.group(1)), "file": f.name,
                         "title": m.group(2), "words": chapter_words(f)})
chapters.sort(key=lambda c: c["n"])
content = [c for c in chapters if c["words"] >= 200]
cw = sum(c["words"] for c in content)
n_parts = max(1, -(-cw // MAX_UNIT_WORDS), -(-len(content) // MAX_UNIT_CHAPS))
print(f"chapters: {len(chapters)} | content(>=200w): {len(content)} | content words: {cw} | parts: {n_parts}")
assert n_parts == 2, "expected the book to split into exactly 2 units"

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
idx = next(i for i, b in enumerate(manifest) if b["book"] == BOOK)
manifest[idx] = {"book": BOOK, "chapters": chapters}
MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
print("full_manifest.json updated (002 entry replaced)")

for old in (N439, N440):
    if old.exists():
        old.unlink()
        print("deleted stale note:", old.name)

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
    hi = 10 ** 6 if i == n_parts - 1 else content[bounds[i + 1] - 1]["n"]
    ranges.append((lo, hi))

unit_ids = ["u439", "u440"]
for i, (lo, hi) in enumerate(ranges):
    unit_chs = [c for c in chapters if c["n"] >= lo and (c["n"] <= hi or n_parts == 1)]
    unit = {
        "unit": unit_ids[i],
        "book": BOOK,
        "part": "%d/%d" % (i + 1, n_parts) if n_parts > 1 else "1/1",
        "path": str(MD_BOOK),
        "range": [lo, hi] if n_parts > 1 else None,
        "chapters": [{"n": c["n"], "file": c["file"], "words": c["words"]}
                     for c in unit_chs],
        "content": [c["n"] for c in content if lo <= c["n"] and (c["n"] <= hi or n_parts == 1)],
    }
    UNIT_PATHS[unit_ids[i]].write_text(json.dumps(unit, ensure_ascii=False, indent=1),
                                       encoding="utf-8")
    print(f"wrote {unit_ids[i]}: part {unit['part']}, range {lo}-{hi}, "
          f"{len(unit['chapters'])} chapters, {len(unit['content'])} content")
