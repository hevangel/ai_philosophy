"""Build the master philosopher/concept -> book/chapter index map."""
import json
from collections import defaultdict
from pathlib import Path

BATCH = Path(r"B:\ai_philosophy\sratchpad\libgen_batch")
AN_ROOT = Path(r"B:\ai_philosophy\philosophy_pop_culture\analysis")

records = json.loads((BATCH / "chapter_index.json").read_text(encoding="utf-8"))

# philosopher -> book -> [(ch, title, count)]
ph_map = defaultdict(lambda: defaultdict(list))
co_map = defaultdict(lambda: defaultdict(list))
for rec in records:
    for name, cnt in rec["philosophers"].items():
        ph_map[name][rec["book_num"]].append((rec["ch"], rec["title"], cnt))
    for name, cnt in rec["concepts"].items():
        co_map[name][rec["book_num"]].append((rec["ch"], rec["title"], cnt))

# book num -> title & dir
book_titles = {}
for rec in records:
    book_titles[rec["book_num"]] = rec["book"]

TOP = 40
agg = json.loads((BATCH / "aggregate.json").read_text(encoding="utf-8"))
top_ph = [e["name"] for e in agg["philosopher_breadth"][:TOP]]
top_co = [e["name"] for e in agg["concept_breadth"][:TOP]
          if e["name"] not in ("ethics (general)", "death & mortality",
                               "justice", "metaphysics", "political philosophy",
                               "epistemology", "aesthetics")][:TOP]

lines = ["# Philosophy & Pop Culture — Philosopher/Concept → Chapter Index Map", "",
         f"Corpus: {len(book_titles)} books, {len(records)} essays/chapters.",
         "Counts in parentheses are keyword mentions in that book's chapters.",
         "Chapter-level detail lives in `philosophy_pop_culture/analysis/<book>/index.md`.", ""]


def section(title, mapping, book_titles, kind):
    lines.append(f"## {title}")
    lines.append("")
    for name in mapping:
        books = mapping[name]
        total_ch = sum(len(v) for v in books.values())
        lines.append(f"### {name} — {len(books)} books, {total_ch} chapters")
        lines.append("")
        for num in sorted(books, key=lambda n: -len(books[n])):
            chs = books[num]
            chlist = ", ".join(f"ch{n} ({c})" for n, t, c in sorted(chs)[:8])
            more = f" +{len(chs) - 8} more" if len(chs) > 8 else ""
            lines.append(f"- **{book_titles.get(num, num)}** — {chlist}{more}")
        lines.append("")


section("Philosophers", ph_map, book_titles, "ph")
section("Concepts & Ideas", co_map, book_titles, "co")

out = AN_ROOT / "philosopher_chapter_map.md"
out.write_text("\n".join(lines), encoding="utf-8")
print(f"wrote {out} ({len(lines)} lines)")
