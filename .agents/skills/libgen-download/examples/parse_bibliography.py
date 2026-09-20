"""EXAMPLE: how the example book list was built from a bibliography markdown.

Parsed `sratchpad/philosophy_and_popular_culture_master_bibliography-1.md`
(a numbered, sectioned bibliography of the philosophy-and-popular-culture
series) into `philosophy_pop_culture.books.json`: one record per book with
num / group / title / subtitle / full_title / author. Adapt the section_map
and the numbered-entry regex to your own bibliography format.

Output schema expected by the download scripts (scripts/batch_download.py,
scripts/chunk_loop.py, scripts/local_match.py):

  [{"num": 1, "group": "Open Court",
    "title": "Seinfeld and Philosophy",
    "subtitle": "A Book about Everything and Nothing",
    "full_title": "Seinfeld and Philosophy: A Book about Everything and Nothing",
    "author": ""}, ...]

`num` must be unique (it keys the download state and the extracted
book_NNNN.<ext> filenames); title/subtitle drive search and match scoring.
"""
import json
import re
from pathlib import Path

MD = Path(r"B:\ai_philosophy\sratchpad\philosophy_and_popular_culture_master_bibliography-1.md")
OUT = Path(__file__).with_name("philosophy_pop_culture.books.json")

text = MD.read_text(encoding="utf-8")

# Section headers -> group names
section_map = {
    "I. Open Court": "Open Court",
    "II. Wiley": "Wiley-Blackwell",
    "III. University Press of Kentucky": "Kentucky",
    "IV. Lexington": "Lexington",
    "V. Open Universe": "Open Universe",
    "VI. Missing": "Older Wiley",
    "VII. Great Authors": "Great Authors",
    "VIII. Wiley": "Philosophy for Everyone",
    "IX. McFarland": "McFarland",
    "X. Independent": "Independent",
    "XI. Meta-books": "Meta",
}

current_group = None
books = []

for line in text.splitlines():
    line = line.strip()
    for key, group in section_map.items():
        if line.startswith("# ") and key in line:
            current_group = group
            break

    m = re.match(r"^(\d+)\.\s+\*\*(.+?)\*\*\s*(.*)$", line)
    if not m:
        continue

    num = int(m.group(1))
    bold = m.group(2)
    rest = m.group(3).strip()  # e.g. "— Richard Hanley" for independent entries

    bold = re.sub(r"^\[Vol\.\s*\d+\]\s*", "", bold)

    parts = bold.split(":")
    if len(parts) > 2:
        # subtitles may themselves contain colons (e.g. "Avatar: The Last
        # Airbender and Philosophy: Wisdom from Aang to Zuko") — split at the
        # last colon so the main title keeps its internal colon
        main = ":".join(parts[:-1]).strip()
        sub = parts[-1].strip()
    elif len(parts) == 2:
        main, sub = parts[0].strip(), parts[1].strip()
    else:
        main, sub = bold.strip(), ""

    author = ""
    if rest.startswith("—"):
        author = rest.lstrip("—").strip()
    elif " — " in rest:
        author = rest.split("—", 1)[1].strip()

    books.append({
        "num": num,
        "group": current_group,
        "title": main,
        "subtitle": sub,
        "full_title": f"{main}: {sub}" if sub else main,
        "author": author,
    })

books.sort(key=lambda b: b["num"])
OUT.write_text(json.dumps(books, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Parsed {len(books)} books -> {OUT}")
print("Groups:", {g: sum(1 for b in books if b["group"] == g) for g in sorted({b["group"] for b in books}, key=str)})
