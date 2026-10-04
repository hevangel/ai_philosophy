"""Merge reading-agent notes into a single index structure.

Reads notes/*.json + units/*.json + full_manifest.json + taxonomy.json,
writes merged_index.json with:
  chapters: {book: [{n, title, file, kind, philosophers, concepts, relation, done}]}
  concept_chapters: {slug: [{book, n, title, relation, philosophers}]}
  philosopher_usage: {slug: {"concepts": {slug: count}, "chapters": count}}
  holes: [{...hole, book, unit}]
  progress: coverage stats
"""
import json
from pathlib import Path

BASE = Path(r"B:\ai_philosophy\sratchpad\popcult_index").resolve()
NOTES = BASE / "notes"
UNITS = BASE / "units"
OUT = BASE / "merged_index.json"

tax = json.loads((BASE / "taxonomy.json").read_text(encoding="utf-8"))
manifest = json.loads((BASE / "full_manifest.json").read_text(encoding="utf-8"))

titles = {}
for m in manifest:
    for c in m["chapters"]:
        titles[(m["book"], c["n"])] = c["title"]
all_chapters = {}
for m in manifest:
    all_chapters[m["book"]] = {
        c["n"]: {"n": c["n"], "title": c["title"], "file": c["file"],
                 "words": c["words"], "kind": "chapter", "philosophers": [],
                 "concepts": [], "relation": "", "done": False}
        for c in m["chapters"]}

concept_chapters = {}
philosopher_usage = {}
holes = []
n_units_done = 0

for npath in sorted(NOTES.glob("u*.json")):
    uid = npath.stem
    upath = UNITS / npath.name
    if not upath.exists():
        continue
    unit = json.loads(upath.read_text(encoding="utf-8"))
    note = json.loads(npath.read_text(encoding="utf-8"))
    n_units_done += 1
    book = unit["book"]
    for ch in note.get("chapters", []):
        n = ch.get("n")
        rec = all_chapters.get(book, {}).get(n)
        if rec is None:
            continue
        rec["kind"] = ch.get("kind", "chapter")
        rec["philosophers"] = ch.get("philosophers", [])
        rec["concepts"] = ch.get("concepts", [])
        rec["relation"] = (ch.get("relation") or "").strip()
        rec["done"] = True
    for h in note.get("holes", []):
        h2 = dict(h)
        h2["book"] = book
        h2["unit"] = uid
        holes.append(h2)

n_done = n_mapped = 0
for book, chs in all_chapters.items():
    for n, rec in chs.items():
        if not rec["done"]:
            continue
        n_done += 1
        if rec["concepts"] or rec["philosophers"]:
            n_mapped += 1
        for cslug in rec["concepts"]:
            concept_chapters.setdefault(cslug, []).append({
                "book": book, "n": n, "title": rec["title"],
                "relation": rec["relation"],
                "philosophers": rec["philosophers"]})
        for pslug in rec["philosophers"]:
            u = philosopher_usage.setdefault(pslug, {"concepts": {}, "chapters": 0})
            u["chapters"] += 1
            for cslug in rec["concepts"]:
                u["concepts"][cslug] = u["concepts"].get(cslug, 0) + 1

total_ch = sum(len(v) for v in all_chapters.values())
progress = {
    "units_total": len(list(UNITS.glob("u*.json"))),
    "units_done": n_units_done,
    "books_in_units": len(all_chapters),
    "chapters_total": total_ch,
    "chapters_read": n_done,
    "chapters_mapped": n_mapped,
    "holes_total": len(holes),
    "concepts_used": len(concept_chapters),
    "philosophers_used": len(philosopher_usage),
}
out = {
    "chapters": all_chapters,
    "concept_chapters": concept_chapters,
    "philosopher_usage": philosopher_usage,
    "holes": holes,
    "progress": progress,
    "taxonomy_meta": {"domains": tax["domains"],
                      "philosophers": {k: v["n"] for k, v in tax["philosophers"].items()},
                      "concepts": {k: v["n"] for k, v in tax["concepts"].items()},
                      "concept_dom": {k: v["dom"] for k, v in tax["concepts"].items()},
                      "concept_phil": {k: v["p"] for k, v in tax["concepts"].items()},
                      "phil_dom": {k: v["dom"] for k, v in tax["philosophers"].items()}},
}
OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps(progress, indent=1))
