"""Split blob-era markdown files into per-essay files for books whose EPUB
spine merges whole parts into single documents (audit-flagged books with no
cleaner mirror edition).

Strategies per book:
  224, 243: split each oversized blob at h1 headings whose section ends with a
            "Notes" heading (each real essay carries its own Notes section).
  301, 284: split blobs at body lines matching hand-curated TOC titles
            (transcribed from the books' own Contents pages); dense clusters
            of matches (the Contents block itself) are excluded.

Run without --apply to print the proposed split map only.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(r"B:\ai_philosophy\data\philosophy_pop_culture\markdown").resolve()
REPORT = Path(r"B:\ai_philosophy\scratchpad\audit_md\split_map.json").resolve()

CH_RE = re.compile(r"^ch(\d+) - (.*?)\.md$", re.I)
WORD_RE = re.compile(r"[A-Za-z\u00C0-\u024F']+")

# 301 Comics as Philosophy (ed. Jeff McLaughlin) — Contents page, ch03.
TITLES_301 = [
    "Introduction",
    "What If? DC’s Crisis and Leibnizian Possible Worlds",
    "Describing and Discarding “Comics” as an Impotent Act of Philosophical Rigor",
    "“No Harm in Horror”",
    "Truth Be Told",
    "Plato, Spider-Man and the Meaning of Life",
    "Modernity, Race, and the American Superhero",
    "Deconstructing the Hero",
    "Jean-Paul Sartre Meets Enid Coleslaw",
    "Making the Abstract Concrete",
    "The Good Government According to Tintin",
    "Drawn into 9/11, But Where Have all the Superheroes Gone?",
]
# 284 College Sex – Philosophy for Everyone (eds. Bruce & Stewart) — Contents.
TITLES_284 = [
    "Foreword",
    "Campus Orientation: An Introduction to College Sex",
    "Sex and Socratic Experimentation",
    "The Straight Sex Experiment",
    "The Virtual Bra Clasp",
    "Smeared Makeup and Stiletto Heels",
    "Relations at a Distance",
    "What’s Love Got to Do with It?",
    "Friends with Benefits: A Precarious Negotiation",
    "The Philosophy of Friends with Benefits",
    "A Horny Dilemma",
    "Philosophers and the Not So Platonic Student-Teacher Relationship",
    "Thinking About Thinking About Sex",
    "Exploring the Association Between Love and Sex",
    "Sex for a College Education",
    "Meaningful Sex and Moral Respect",
    "Can Girls Go Wild With Self-Respect?",
    "Mutual Respect and Sexual Morality",
    "Bad Faith or True Desire?",
]

STRATEGIES = {"224": "h1_notes", "243": "h1_notes", "301": "contents", "284": "contents"}
TITLES = {"301": TITLES_301, "284": TITLES_284}
BLOB_MIN_WORDS = 15000


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def words_of(text):
    return len(WORD_RE.findall(text))


def book_dir(num):
    d = [p for p in ROOT.iterdir() if p.is_dir() and p.name.startswith(num + " - ")]
    return d[0] if d else None


def md_files(bd):
    out = []
    for f in sorted(bd.iterdir()):
        m = CH_RE.match(f.name)
        if m:
            out.append((int(m.group(1)), f))
    out.sort(key=lambda t: t[0])
    return out


def safe_title(t):
    t = re.sub(r"[*_#]", "", t).strip()
    t = re.sub(r"[\r\n]+", " ", t)
    for ch in ':"/?*<>|':
        t = t.replace(ch, " ")
    return re.sub(r"\s+", " ", t).strip().strip(".")[:110].rstrip()


def split_h1_notes(text):
    lines = text.splitlines()
    h1_idx = [i for i, ln in enumerate(lines) if re.match(r"^# [^#]", ln)]
    if not h1_idx:
        return None
    essays = []
    for j, start in enumerate(h1_idx):
        end = h1_idx[j + 1] if j + 1 < len(h1_idx) else len(lines)
        section = lines[start:end]
        h2s = [ln for ln in section if re.match(r"^## ", ln)]
        has_notes = any(norm(h2[3:]) == "notes" for h2 in h2s)
        title = re.sub(r"^#+ ", "", section[0]).strip()
        if has_notes and norm(title) != "notes":
            essays.append({"title": title, "lines": section})
        elif essays:
            essays[-1]["lines"].extend(section)
        else:
            essays.append({"title": None, "lines": section})
    return essays


def find_boundaries(lines, titles):
    """Match titles (space-less normalized, substring over a 2-line window)
    to body line indexes; drop dense clusters (>=4 matches within 30 lines =
    the Contents block)."""
    hits = []
    norms = [norm(ln) for ln in lines]
    for t in titles:
        nt = norm(t)
        if len(nt) < 8:
            continue
        probe = nt[:20]
        for i in range(len(lines)):
            window = norms[i] + (norms[i + 1] if i + 1 < len(norms) else "")
            if probe in window:
                hits.append((i, t))
                break
    hits.sort()
    kept = []
    skip_ranges = []
    a = 0
    while a < len(hits):
        b = a
        cluster = [hits[a]]
        while b + 1 < len(hits) and hits[b + 1][0] - cluster[-1][0] <= 30:
            b += 1
            cluster.append(hits[b])
        if len(cluster) >= 4:
            skip_ranges.append((cluster[0][0], cluster[-1][0]))
        a = b + 1
    for idx, t in hits:
        if any(lo <= idx <= hi for lo, hi in skip_ranges):
            continue
        kept.append((idx, t))
    return kept


def plan(num):
    bd = book_dir(num)
    if bd is None:
        return None
    strategy = STRATEGIES[num]
    plan_out = {"book": bd.name, "strategy": strategy, "splits": []}
    if strategy == "h1_notes":
        for n, f in md_files(bd):
            text = f.read_text(encoding="utf-8", errors="replace")
            if words_of(text) < BLOB_MIN_WORDS:
                continue
            essays = split_h1_notes(text)
            if not essays:
                plan_out["splits"].append({"file": f.name, "error": "no h1+notes structure"})
                continue
            plan_out["splits"].append({
                "file": f.name,
                "essays": [{"title": e["title"] or "(lead)", "words": words_of("\n".join(e["lines"]))}
                           for e in essays],
            })
    else:
        titles = TITLES[num]
        for n, f in md_files(bd):
            text = f.read_text(encoding="utf-8", errors="replace")
            if words_of(text) < BLOB_MIN_WORDS:
                continue
            lines = text.splitlines()
            hits = find_boundaries(lines, titles)
            entries = []
            for k, (i, t) in enumerate(hits):
                end = hits[k + 1][0] if k + 1 < len(hits) else len(lines)
                entries.append({"line": i, "title": t, "words": words_of("\n".join(lines[i:end]))})
            lead = words_of("\n".join(lines[:hits[0][0]])) if hits else words_of(text)
            plan_out["splits"].append({"file": f.name, "lead_words": lead, "essays": entries})
    return plan_out


def apply_split(num):
    bd = book_dir(num)
    strategy = STRATEGIES[num]
    pieces = []  # [(kind, title, lines)] in reading order; kind: keep|essay|front
    for n, f in md_files(bd):
        text = f.read_text(encoding="utf-8", errors="replace")
        if words_of(text) < BLOB_MIN_WORDS:
            pieces.append({"kind": "keep", "title": CH_RE.match(f.name).group(2),
                           "lines": text.splitlines(), "src": f})
            continue
        lines = text.splitlines()
        if strategy == "h1_notes":
            essays = split_h1_notes(text)
            lead = []
            for e in essays:
                if e["title"] is None:
                    lead.extend(e["lines"])
                else:
                    pieces.append({"kind": "essay", "title": e["title"],
                                   "lines": lead + e["lines"], "src": f})
                    lead = []
        else:
            hits = find_boundaries(lines, TITLES[num])
            if not hits:
                pieces.append({"kind": "keep", "title": CH_RE.match(f.name).group(2),
                               "lines": lines, "src": f})
                continue
            pieces.append({"kind": "front", "title": "Front Matter",
                           "lines": lines[:hits[0][0]], "src": f})
            for k, (i, t) in enumerate(hits):
                end = hits[k + 1][0] if k + 1 < len(hits) else len(lines)
                pieces.append({"kind": "essay", "title": t, "lines": lines[i:end], "src": f})
    # two-phase renumber: write all pieces under temp names, delete the old
    # blob sources, then rename temps to their final chNN names
    staged = []
    n = 0
    for p in pieces:
        n += 1
        title = safe_title(p["title"]) or "section-%d" % n
        body = "\n".join(p["lines"]).strip()
        if p["kind"] == "keep":
            new_text = body + "\n"
        else:
            header = "# %s\n\n*Source: %s*\n\n" % (title, bd.name)
            new_text = header + body + "\n"
        tmp = bd / ("split_tmp_%03d.md" % n)
        tmp.write_text(new_text, encoding="utf-8")
        staged.append((tmp, "ch%02d - %s.md" % (n, title), p))
    for _, final, p in staged:
        if p.get("src") is not None:
            p["src"].unlink(missing_ok=True)
    for tmp, final, p in staged:
        tmp.rename(bd / final)
    return len(staged)


def main():
    apply = "--apply" in sys.argv
    nums = [a for a in sys.argv[1:] if a.isdigit()]
    report = {}
    for num in nums:
        if apply:
            count = apply_split(num)
            report[num] = {"applied": True, "files": count}
            print(f"{num}: applied, {count} files after split")
        else:
            report[num] = plan(num)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    if not apply:
        for num, r in report.items():
            print("=" * 90)
            print(num, r["book"] if r else "NOT FOUND")
            if not r:
                continue
            for s in r["splits"]:
                if "error" in s:
                    print("  !!", s.get("file"), s["error"])
                    continue
                print("  blob:", s.get("file"),
                      f"(lead {s.get('lead_words')}w)" if "lead_words" in s else "")
                for e in s.get("essays", []):
                    print("     ->", e.get("words"), "w |", e.get("title", "")[:70])
        print("\n(dry run — re-run with --apply to write files)")


if __name__ == "__main__":
    main()
