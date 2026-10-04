"""Repair flagged notes deterministically.

1. Remap known-bad concept slugs to their correct taxonomy slug (or drop when
   there is no faithful match). Drops are logged.
2. Fill MISSING chapters that are NOT content-essays: add a minimal entry
   classified front/notes by the unit manifest's word count + filename, with
   [] slugs and "" relation (which the validator accepts for non-'chapter').
3. A missing chapter that IS a content-essay (listed in the unit "content"
   array) cannot be faithfully stubbed - it is reported as NEEDS_READ and left
   for a targeted re-read, never invented.

Re-runnable and idempotent. Writes each fixed note back in place; prints a log.
"""
import json
from pathlib import Path

BASE = Path(r"B:\ai_philosophy\sratchpad\popcult_index").resolve()
NOTES = BASE / "notes"
UNITS = BASE / "units"

# concept-slug remaps: bad -> good taxonomy slug, or None to DROP the slug
REMAP = {
    "fairness": "justice-as-fairness",
    "personhood": "personal-identity",
    "simulation": "simulation-hypothesis",
    "natural-law": "aquinas-natural-law",
    "collective-unconscious": "jung-collective-unconscious",
    "egoism": "moral-egoism",
    "alienation": "marx-alienation",
    "narrative-identity": "personal-identity",
    "ethics-of-truth": None,      # no faithful taxonomy match -> drop
    "political-social": None,     # a DOMAIN, not a concept -> drop
}

tax = json.loads((BASE / "taxonomy.json").read_text(encoding="utf-8"))
PHIL = set(tax["philosophers"])
CON = set(tax["concepts"])


def classify(fname, words):
    f = (fname or "").lower()
    if any(k in f for k in ("cover", "title", "toc", "contents", "copyright",
                            "divider", "half", "blank", "front")):
        return "front"
    if any(k in f for k in ("index", "notes", "biblio", "acknow", "contrib",
                            "about", "credits")):
        return "notes"
    return "front" if (words or 0) < 200 else None  # None => essay, can't stub


def repair(uid, log):
    npath = NOTES / (uid + ".json")
    upath = UNITS / (uid + ".json")
    if not npath.exists():
        return
    note = json.loads(npath.read_text(encoding="utf-8"))
    unit = json.loads(upath.read_text(encoding="utf-8"))
    umeta = {c["n"]: c for c in unit["chapters"]}
    content_essays = set(unit.get("content", []))
    changed = False

    # 1. slug remaps
    for ch in note.get("chapters", []):
        for field in ("concepts", "philosophers"):
            new = []
            for s in ch.get(field, []):
                if s in PHIL or s in CON:
                    new.append(s)
                elif s in REMAP:
                    tgt = REMAP[s]
                    if tgt and tgt not in new:
                        new.append(tgt)
                        log.append("%s ch%s: %s -> %s" % (uid, ch.get("n"), s, tgt))
                    elif tgt is None:
                        log.append("%s ch%s: dropped %s" % (uid, ch.get("n"), s))
                    changed = True
                else:
                    # unknown & not in remap: leave for manual/hole, but drop
                    log.append("%s ch%s: UNMAPPED %s (dropped)" % (uid, ch.get("n"), s))
                    changed = True
            if new != ch.get(field, []):
                ch[field] = new

    # 2/3. missing chapters
    have = {c.get("n") for c in note.get("chapters", [])}
    want = set(umeta)
    for n in sorted(want - have):
        cm = umeta[n]
        if n in content_essays:
            log.append("%s ch%s: NEEDS_READ (content essay missing)" % (uid, n))
            continue
        kind = classify(cm.get("file"), cm.get("words"))
        if kind is None:
            log.append("%s ch%s: NEEDS_READ (essay by wordcount)" % (uid, n))
            continue
        note["chapters"].append({"n": n, "file": cm.get("file"), "kind": kind,
                                 "philosophers": [], "concepts": [], "relation": ""})
        changed = True
        log.append("%s ch%s: filled as %s" % (uid, n, kind))

    if changed:
        note["chapters"].sort(key=lambda c: c.get("n", 0))
        npath.write_text(json.dumps(note, ensure_ascii=False, indent=1),
                         encoding="utf-8")


def main():
    bad = ["u294", "u295", "u300", "u318", "u334", "u337", "u338", "u345",
           "u355", "u360", "u361", "u362", "u396", "u404", "u408", "u409",
           "u415", "u416", "u423", "u424"]
    log = []
    for uid in bad:
        repair(uid, log)
    for line in log:
        print(line)
    print("repaired %d notes; %d log lines" % (len(bad), len(log)))


if __name__ == "__main__":
    main()
