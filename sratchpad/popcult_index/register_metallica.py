"""One-off: register the extracted Metallica book in full_manifest.json + units/u438.json."""
import json
from pathlib import Path

BOOK = "183 - Metallica and Philosophy - A Crash Course in Brain Surgery"
BASE = Path(r"B:\ai_philosophy\sratchpad\popcult_index").resolve()
MD_ROOT = Path(r"B:\ai_philosophy\philosophy_pop_culture\markdown").resolve()
folder = MD_ROOT / BOOK

chapters = []
for f in sorted(folder.glob("ch*.md")):
    txt = f.read_text(encoding="utf-8")
    title = txt.split("\n")[0].lstrip("# ").strip()
    n = int(f.name[2:4])
    chapters.append({"n": n, "file": f.name, "title": title,
                     "words": len(txt.split())})

mp = BASE / "full_manifest.json"
m = json.loads(mp.read_text(encoding="utf-8"))
m = [b for b in m if b["book"] != BOOK]
m.append({"book": BOOK, "chapters": chapters})
m.sort(key=lambda b: b["book"])
mp.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")

content = [c["n"] for c in chapters if c["words"] >= 200]
unit = {"unit": "u438", "book": BOOK, "part": "1/1",
        "path": str(folder), "range": None,
        "chapters": [{"n": c["n"], "file": c["file"], "words": c["words"]}
                     for c in chapters],
        "content": content}
(BASE / "units" / "u438.json").write_text(
    json.dumps(unit, ensure_ascii=False, indent=1), encoding="utf-8")
print("manifest books:", len(m), "| u438 chapters:", len(chapters),
      "| content:", content)
