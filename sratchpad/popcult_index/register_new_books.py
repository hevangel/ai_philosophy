"""Register the 6 newly recovered books in full_manifest.json + corpus_manifest.json
and create reading units (register_metallica.py pattern, build_work_units.py
splitting conventions).

Books: 002, 110 (epub); 161, 194, 206, 235 (pdf). Units u439+ — one per book,
split into balanced parts when content exceeds MAX_UNIT_WORDS, so no reading
agent faces more than ~60k words.
"""
import json
import re
from pathlib import Path

BASE = Path(r"B:\ai_philosophy\sratchpad\popcult_index").resolve()
MD_ROOT = Path(r"B:\ai_philosophy\philosophy_pop_culture\markdown").resolve()

MAX_UNIT_WORDS = 60000

BOOKS = [
    "002 - The Simpsons and Philosophy - The D'oh! of Homer",
    "110 - Hamilton and Philosophy - Revolutionary Thinking",
    "161 - Family Guy and Philosophy - A Cure for the Petarded",
    "194 - Taylor Swift and Philosophy - Essays from the Tortured Philosophers Department",
    "206 - The Witcher and Philosophy - Toss a Coin to Your Philosopher",
    "235 - The Philosophy of TV Noir",
]

mp = BASE / "full_manifest.json"
manifest = json.loads(mp.read_text(encoding="utf-8"))
manifest = [b for b in manifest if b["book"] not in BOOKS]

cp = BASE / "corpus_manifest.json"
cmanifest = json.loads(cp.read_text(encoding="utf-8"))
cmanifest = [b for b in cmanifest if b["book"] not in BOOKS]

# wipe any units previously created for these books (re-runs)
for p in BASE.glob("units/u4*.json"):
    u = json.loads(p.read_text(encoding="utf-8"))
    if u["book"] in BOOKS:
        p.unlink()

next_unit = 439
for book in BOOKS:
    folder = MD_ROOT / book
    chapters = []
    for f in sorted(folder.glob("ch*.md")):
        txt = f.read_text(encoding="utf-8")
        title = txt.split("\n")[0].lstrip("# ").strip()
        n = int(f.name[2:4])
        chapters.append({"n": n, "file": f.name, "title": title,
                         "words": len(txt.split())})
    chapters.sort(key=lambda c: c["n"])
    manifest.append({"book": book, "chapters": chapters})
    cmanifest.append({"book": book, "n_chapters": len(chapters),
                      "total_words": sum(c["words"] for c in chapters)})
    content = [c for c in chapters if c["words"] >= 200]
    cw = sum(c["words"] for c in content)
    n_parts = max(1, -(-cw // MAX_UNIT_WORDS))
    bounds = [1]  # keep leading front matter in part 1
    acc = 0
    k = 1
    for i, c in enumerate(content):
        acc += c["words"]
        if k < n_parts and acc >= cw * k / n_parts:
            bounds.append(c["n"])
            k += 1
    for i in range(n_parts):
        lo = bounds[i]
        hi = (bounds[i + 1] - 1) if i + 1 < len(bounds) else 10 ** 6
        unit_chs = [c for c in chapters if c["n"] >= lo and c["n"] <= hi]
        unit = {"unit": "u%d" % next_unit, "book": book,
                "part": "%d/%d" % (i + 1, n_parts) if n_parts > 1 else "1/1",
                "path": str(folder),
                "range": [lo, hi] if n_parts > 1 else None,
                "chapters": [{"n": c["n"], "file": c["file"], "words": c["words"]}
                             for c in unit_chs],
                "content": [c["n"] for c in unit_chs if c["words"] >= 200]}
        (BASE / "units" / ("u%d.json" % next_unit)).write_text(
            json.dumps(unit, ensure_ascii=False, indent=1), encoding="utf-8")
        print("u%d  %-46s part %s  chs=%2d content=%2d words=%6d"
              % (next_unit, book[:44], unit["part"], len(unit_chs),
                 len(unit["content"]), sum(c["words"] for c in content) // n_parts))
        next_unit += 1

manifest.sort(key=lambda b: b["book"])
mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
cmanifest.sort(key=lambda b: b["book"])
cp.write_text(json.dumps(cmanifest, ensure_ascii=False, indent=1), encoding="utf-8")
print("full_manifest books:", len(manifest), "| corpus_manifest books:", len(cmanifest))
