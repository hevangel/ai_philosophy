"""Bind all accepted hole-proposing chapters (from the 9 re-read units) to
their new taxonomy slugs, per the finalization protocol."""
import json
from pathlib import Path

BASE = Path(r"B:\ai_philosophy\scratchpad\popcult_index").resolve()
UNITS = ["u081", "u082", "u297", "u325", "u326", "u358", "u359", "u363", "u450"]

for uid in UNITS:
    p = BASE / "notes" / f"{uid}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    bound = 0
    for h in d.get("holes", []):
        slug = h.get("suggested_slug", "")
        ch = h.get("ch")
        for c in d["chapters"]:
            if c["n"] == ch:
                key = "philosophers" if h.get("type") == "philosopher" else "concepts"
                if slug not in c[key]:
                    c[key].append(slug)
                    bound += 1
        h["accepted"] = True
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{uid}: bound {bound} slugs")
