"""Build intro-generation batches from taxonomy.json.

Emits sratchpad/popcult_index/intro_batches/batch_NN.json input files, each a
list of items to write a short intro for. An item is either:
  {"key": "<concept-slug>", "name": "...", "kind": "concept",
   "philosopher": "<name or ''>", "domain": "<domain name>"}
or
  {"key": "phil:<philosopher-slug>", "name": "...", "kind": "philosopher",
   "dates": "...", "domain": "<domain name>"}

Only items still missing from intros.json are emitted, so re-running after a
partial pass produces batches for the remainder only.
"""
import json
from pathlib import Path

BASE = Path(r"B:\ai_philosophy\sratchpad\popcult_index").resolve()
BATCH_DIR = BASE / "intro_batches"
PER_BATCH = 15


def main():
    tax = json.loads((BASE / "taxonomy.json").read_text(encoding="utf-8"))
    dom_name = {k: v["n"] for k, v in tax["domains"].items()}
    phil_name = {k: v["n"] for k, v in tax["philosophers"].items()}

    existing = {}
    ip = BASE / "intros.json"
    if ip.exists():
        existing = json.loads(ip.read_text(encoding="utf-8"))

    items = []
    # philosophers first (fewer, anchor the concepts)
    for slug, p in tax["philosophers"].items():
        key = "phil:" + slug
        if key in existing:
            continue
        items.append({"key": key, "name": p["n"], "kind": "philosopher",
                      "dates": p.get("d", ""),
                      "domain": dom_name.get(p.get("dom", ""), p.get("dom", ""))})
    for slug, c in tax["concepts"].items():
        if slug in existing:
            continue
        items.append({"key": slug, "name": c["n"], "kind": "concept",
                      "philosopher": phil_name.get(c.get("p", ""), ""),
                      "domain": dom_name.get(c.get("dom", ""), c.get("dom", ""))})

    BATCH_DIR.mkdir(exist_ok=True)
    # clear old batch files
    for old in BATCH_DIR.glob("batch_*.json"):
        old.unlink()

    n = 0
    for i in range(0, len(items), PER_BATCH):
        chunk = items[i:i + PER_BATCH]
        n += 1
        (BATCH_DIR / ("batch_%02d.json" % n)).write_text(
            json.dumps(chunk, ensure_ascii=False, indent=1), encoding="utf-8")
    print("items to write: %d  ->  %d batch file(s) of <=%d in %s"
          % (len(items), n, PER_BATCH, BATCH_DIR))


if __name__ == "__main__":
    main()
