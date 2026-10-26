"""Dump, for the blob books: (a) front-matter files that look like Contents
pages, (b) every heading (h1-h3) in every content markdown file with word
offsets — so the split matcher can be designed against real formats."""
import re
from pathlib import Path

ROOT = Path(r"B:\ai_philosophy\data\philosophy_pop_culture\markdown").resolve()
BOOKS = ["025", "224", "243", "251", "284", "301"]
CH_RE = re.compile(r"^ch(\d+) - (.*?)\.md$", re.I)
WORD_RE = re.compile(r"[A-Za-z\u00C0-\u024F']+")


def headings(md_text):
    out = []
    pos = 0
    for line in md_text.splitlines():
        m = re.match(r"^(#{1,4}) (.+)$", line)
        if m:
            words = len(WORD_RE.findall(md_text[pos:]))
            out.append((len(m.group(1)), m.group(2).strip()[:75], words))
        pos += len(line) + 1
    return out


for num in BOOKS:
    dirs = [d for d in ROOT.iterdir() if d.is_dir() and d.name.startswith(num + " - ")]
    if not dirs:
        continue
    print("=" * 100)
    print(dirs[0].name)
    for f in sorted(dirs[0].iterdir()):
        m = CH_RE.match(f.name)
        if not m:
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        words = len(WORD_RE.findall(text))
        hs = headings(text)
        content_heads = [h for h in hs if h[1] and words > 5000]
        print(f"\n-- {f.name[:70]}  ({words}w, {len(hs)} headings)")
        if words < 4000:
            print("   [front/back matter] first lines:")
            for ln in text.splitlines()[3:14]:
                if ln.strip():
                    print("     |", ln.strip()[:80])
        else:
            for lvl, t, rem in hs:
                if lvl <= 3:
                    print(f"   h{lvl} (then {rem:>6}w): {t}")
