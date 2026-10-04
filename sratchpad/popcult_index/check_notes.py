"""Validate notes/*.json against units and taxonomy.

Usage: py -3 check_notes.py [--ids u000,u001,... | --all]
Prints per-unit problems and a summary. Missing files are listed separately.
"""
import json
import sys
from pathlib import Path

BASE = Path(r"B:\ai_philosophy\sratchpad\popcult_index").resolve()
NOTES = BASE / "notes"
UNITS = BASE / "units"
TAX_PATH = BASE / "taxonomy.json"

tax = json.loads(TAX_PATH.read_text(encoding="utf-8"))
PHIL = set(tax["philosophers"])
CON = set(tax["concepts"])


def check(uid):
    out = {"unit": uid, "problems": [], "n_ch": 0, "n_mapped": 0, "n_holes": 0,
           "bad_slugs": []}
    upath = UNITS / (uid + ".json")
    npath = NOTES / (uid + ".json")
    if not npath.exists():
        out["problems"].append("missing")
        return out
    try:
        note = json.loads(npath.read_text(encoding="utf-8"))
    except Exception as e:
        out["problems"].append("invalid json: %s" % e)
        return out
    unit = json.loads(upath.read_text(encoding="utf-8"))
    want = {c["n"] for c in unit["chapters"]}
    got = {}
    for ch in note.get("chapters", []):
        n = ch.get("n")
        if n in got:
            out["problems"].append("duplicate ch %s" % n)
        got[n] = ch
        slugs = list(ch.get("philosophers", [])) + list(ch.get("concepts", []))
        for s in slugs:
            if s not in PHIL and s not in CON:
                out["bad_slugs"].append((n, s))
        if slugs:
            out["n_mapped"] += 1
        if ch.get("kind") == "chapter" and not (ch.get("relation") or "").strip():
            out["problems"].append("ch %s empty relation" % n)
    out["n_ch"] = len(got)
    out["n_holes"] = len(note.get("holes", []))
    missing = want - set(got)
    extra = set(got) - want
    if missing:
        out["problems"].append("missing chapters: %s" % sorted(missing)[:10])
    if extra:
        out["problems"].append("extra chapters: %s" % sorted(extra)[:10])
    if out["bad_slugs"]:
        out["problems"].append("unknown slugs: %s" % (out["bad_slugs"][:8],))
    return out


def main():
    ids = None
    if "--ids" in sys.argv:
        ids = sys.argv[sys.argv.index("--ids") + 1].split(",")
    else:
        ids = sorted(p.stem for p in NOTES.glob("*.json"))
    n_bad = 0
    tot_ch = tot_map = tot_holes = 0
    for uid in ids:
        r = check(uid)
        tot_ch += r["n_ch"]
        tot_map += r["n_mapped"]
        tot_holes += r["n_holes"]
        if r["problems"]:
            n_bad += 1
            print("BAD %s: %s" % (uid, "; ".join(str(p) for p in r["problems"])))
    print("checked %d notes: %d bad | chapters %d mapped %d holes %d"
          % (len(ids), n_bad, tot_ch, tot_map, tot_holes))


if __name__ == "__main__":
    main()
