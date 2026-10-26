"""Validate course_lectures/<cid>.json files against courses.json + taxonomy.json."""
import json
from pathlib import Path

BASE = Path(r"B:\ai_philosophy\scratchpad\popcult_index")
COURSES_PATH = BASE / "courses.json"
TAXONOMY_PATH = BASE / "taxonomy.json"
LECTURES_DIR = BASE / "course_lectures"


def main() -> None:
    taxonomy = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
    courses = json.loads(COURSES_PATH.read_text(encoding="utf-8"))
    ids = [c["id"] for c in courses]
    bad = []
    total = 0
    for cid in ids:
        path = LECTURES_DIR / (cid + ".json")
        if not path.exists():
            print(cid + ": MISSING (no file yet)")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            bad.append(cid + ": invalid JSON (" + str(exc) + ")")
            continue
        if payload.get("course") != cid:
            bad.append(cid + ": course field mismatch")
        seen = set()
        for item in payload.get("lectures", []):
            n = item.get("n")
            if not isinstance(n, int) or n < 1:
                bad.append(cid + ": bad n " + repr(n))
                continue
            if n in seen:
                bad.append(cid + ": duplicate n " + str(n))
            seen.add(n)
            kind = item.get("kind", "lecture")
            if kind not in ("lecture", "other"):
                bad.append(cid + " lecture " + str(n) + ": bad kind " + repr(kind))
            if kind == "lecture" and not str(item.get("summary", "")).strip():
                bad.append(cid + " lecture " + str(n) + ": empty summary")
            for slug in item.get("concepts", []):
                if slug not in taxonomy["concepts"]:
                    bad.append(cid + " lecture " + str(n) + ": unknown concept slug " + repr(slug))
            for slug in item.get("philosophers", []):
                if slug not in taxonomy["philosophers"]:
                    bad.append(cid + " lecture " + str(n) + ": unknown philosopher slug " + repr(slug))
            total += 1
    print(str(total) + " lectures checked; " + str(len(bad)) + " problems")
    for line in bad:
        print("  " + line)


if __name__ == "__main__":
    main()
