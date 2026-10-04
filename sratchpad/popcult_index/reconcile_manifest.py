"""Reconcile full_manifest.json to the work units.

The manifest's 464 extra chapters are all <200-word spine stubs (covers, title
pages, 'Unknown' docs) that no unit ever covered; every real essay is unitized
and read. Rebuild the manifest from the units so the index covers exactly what
was read.
"""
import json
from pathlib import Path

BASE = Path(r"B:\ai_philosophy\sratchpad\popcult_index").resolve()
units = {}
for p in sorted((BASE / "units").glob("u*.json")):
    u = json.loads(p.read_text(encoding="utf-8"))
    b = units.setdefault(u["book"], {})
    for c in u["chapters"]:
        b[c["n"]] = c

mp = BASE / "full_manifest.json"
m = json.loads(mp.read_text(encoding="utf-8"))
new = []
for book in m:
    if book["book"] not in units:
        print("WARN book with no units:", book["book"])
        continue
    keep = []
    for c in book["chapters"]:
        u = units[book["book"]].get(c["n"])
        if u is not None and u["file"] == c["file"]:
            keep.append(c)
    new.append({"book": book["book"], "chapters": keep})
dropped = sum(len(b["chapters"]) for b in m) - sum(len(b["chapters"]) for b in new)
mp.write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding="utf-8")
print("books:", len(new), "| chapters kept:",
      sum(len(b["chapters"]) for b in new), "| dropped:", dropped)
