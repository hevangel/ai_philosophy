"""One-off: bind the two accepted hole-proposing chapters to the new taxonomy
slugs (allusion -> u439 ch17, hypocrisy -> u440 ch24), per the finalization
protocol in the popcult-index skill."""
import json
from pathlib import Path

BASE = Path(r"B:\ai_philosophy\scratchpad\popcult_index").resolve()
BINDINGS = {
    "u439": {17: "allusion"},
    "u440": {24: "hypocrisy"},
}

for unit, binds in BINDINGS.items():
    p = BASE / "notes" / f"{unit}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    for c in d["chapters"]:
        if c["n"] in binds and binds[c["n"]] not in c["concepts"]:
            c["concepts"].append(binds[c["n"]])
            print(f"{unit} ch{c['n']}: appended {binds[c['n']]} -> {c['concepts']}")
    for h in d.get("holes", []):
        if h.get("ch") in binds:
            h["accepted"] = True
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("done")
