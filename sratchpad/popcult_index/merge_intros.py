"""Merge per-batch intro fragments into intros.json.

Reads every intros/*.json fragment (each a flat {key: paragraph} object where
key is a concept slug OR "phil:<philosopher-slug>") and merges them into a
single sratchpad/popcult_index/intros.json consumed by render_docs.py.

Validates keys against taxonomy.json: a concept key must be a real concept
slug; a "phil:" key must strip to a real philosopher slug. Unknown keys are
reported and dropped. Re-runnable: later fragments overwrite earlier values
for the same key. Prints coverage vs the full taxonomy.
"""
import json
from pathlib import Path

BASE = Path(r"B:\ai_philosophy\sratchpad\popcult_index").resolve()
FRAG_DIR = BASE / "intros"
OUT = BASE / "intros.json"


def main():
    tax = json.loads((BASE / "taxonomy.json").read_text(encoding="utf-8"))
    concepts = set(tax["concepts"])
    philosophers = set(tax["philosophers"])

    merged = {}
    if OUT.exists():
        merged = json.loads(OUT.read_text(encoding="utf-8"))

    dropped = []
    frag_files = sorted(FRAG_DIR.glob("*.json")) if FRAG_DIR.exists() else []
    for fp in frag_files:
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception as e:
            print("SKIP %s (bad json: %s)" % (fp.name, e))
            continue
        for k, v in data.items():
            if not isinstance(v, str) or not v.strip():
                dropped.append((fp.name, k, "empty"))
                continue
            if k.startswith("phil:"):
                if k[5:] not in philosophers:
                    dropped.append((fp.name, k, "unknown philosopher"))
                    continue
            else:
                if k not in concepts:
                    dropped.append((fp.name, k, "unknown concept"))
                    continue
            merged[k] = v.strip()

    OUT.write_text(json.dumps(merged, ensure_ascii=False, indent=1),
                   encoding="utf-8")

    have_con = sum(1 for k in merged if not k.startswith("phil:"))
    have_phil = sum(1 for k in merged if k.startswith("phil:"))
    print("fragments merged: %d file(s)" % len(frag_files))
    print("concept intros:     %d / %d" % (have_con, len(concepts)))
    print("philosopher intros: %d / %d" % (have_phil, len(philosophers)))
    if dropped:
        print("dropped %d bad key(s):" % len(dropped))
        for f, k, why in dropped[:20]:
            print("  %s: %s (%s)" % (f, k, why))
    # list still-missing
    miss_con = sorted(concepts - {k for k in merged if not k.startswith("phil:")})
    miss_phil = sorted(p for p in philosophers if ("phil:" + p) not in merged)
    print("missing concepts: %d" % len(miss_con))
    print("missing philosophers: %d" % len(miss_phil))


if __name__ == "__main__":
    main()
