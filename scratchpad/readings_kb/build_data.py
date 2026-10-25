#!/usr/bin/env python3
"""Build knowledge-base/readings-kb/data.json from the readings-kb markdown.

Parses the 53 problem entries (locked 8-section template), the 26 book maps,
the Carneades lecture register, index.md (one-line notes, pilot flags, book
catalogue table), and DATA_QUALITY.md into a single JSON file the /readings
explorer fetches. Re-run after editing any of those markdown sources.

Output is deterministic; written via pathlib for the Mimosa hook.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent  # scratchpad/readings_kb/ -> repo root
KB = ROOT / "knowledge-base" / "readings-kb"
OUT = KB / "data.json"

PREMISE_RE = re.compile(r"^- (P\d+|∴\s*C|C)\.\s*(.+)$")
ARG_HEAD_RE = re.compile(r"^\*\*(.+?)\*\*\s*\((?:source|sources):\s*(.+?)\)\s*:?\s*(.*)$", re.S)
LABELED_RE = re.compile(r"^\*\*(.+?)\*\*\s*[—–]\s*(.*)$", re.S)
YT_RE = re.compile(r"\[([^\]]+)\]\(https://www\.youtube\.com/watch\?v=([\w-]+)\)")
LECTURE_ROW_RE = re.compile(r"^\| `([A-Za-z0-9_-]{11}) - (.*?)\.md` \| (.+) \|$")
ENTRY_REF_RE = re.compile(r"(entries/[^\s|]+?\.md)\s*(★)?")
BOOK_NUM_RE = re.compile(r"book (\d{3})")


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def read(p):
    return p.read_text(encoding="utf-8")


def split_sections(text, level="##"):
    """Split markdown into ordered [(heading|None, body)] by `level` headings."""
    pat = re.compile(r"^" + re.escape(level) + r" (.+)$", re.M)
    matches = list(pat.finditer(text))
    out = []
    pre = text[: matches[0].start()] if matches else text
    if pre.strip():
        out.append((None, pre.strip()))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.append((m.group(1).strip(), text[m.end() : end].strip()))
    return out


def chunks(body):
    """Split markdown body into paragraph / bullet-run chunks, in document
    order (a lead-in paragraph with no blank line before its bullet list
    splits at the paragraph/bullet boundary)."""
    out = []
    for block in re.split(r"\n\s*\n", body.strip()):
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        para, cur = [], []

        def flush():
            if para:
                out.append({"kind": "p", "text": " ".join(x.strip() for x in para)})
                para.clear()
            if cur:
                out.append({"kind": "bullets", "items": cur[:]})
                cur.clear()

        for ln in lines:
            if not ln.lstrip().startswith("- "):
                flush()
                para.append(ln)
            else:
                if para:
                    flush()
                cur.append(ln.strip()[2:])
        flush()
    return out


# ---------------------------------------------------------------- subfields

SUBFIELDS = [
    ("epistemology", "Epistemology", "ε", 210,
     "What we can know, and how: skeptical scenarios, induction, perception, testimony, memory, a priori knowledge."),
    ("logic-and-critical-thinking", "Logic & Critical Thinking", "λ", 262,
     "Arguments and their traps: validity, semantic analysis, fallacies, closed systems, self-reference and formal limits."),
    ("metaphysics", "Metaphysics", "μ", 292,
     "What kinds of things there are: natural kinds, essences, rigidity, the necessary a posteriori, causal necessity."),
    ("ethics-and-metaethics", "Ethics & Metaethics", "η", 350,
     "What makes actions right and values real: moral objectivity, the forms of moral theory, motivation, luck."),
    ("political-philosophy", "Political Philosophy", "π", 25,
     "The state, justice, and collective choice: the harm principle, distributive justice, the minimal state, voting."),
    ("philosophy-of-religion", "Philosophy of Religion", "θ", 45,
     "The classical theistic arguments and their opponents: evil, cosmological and ontological arguments, faith, diversity."),
    ("philosophy-of-language", "Philosophy of Language", "γ", 185,
     "Meaning and reference: definite descriptions, rigid designators, indexicals, pragmatic failure, acquisition."),
    ("philosophy-of-science-and-history", "Philosophy of Science & History", "φ", 150,
     "What selection-for explains, and whether historical explanation is explanation at all."),
    ("history-of-philosophy-and-general", "History of Philosophy & General", "χ", 100,
     "Landmark positions from the tradition's own texts: Sartre, Camus, Nietzsche, the postmodernism debate."),
    ("philosophy-of-law", "Philosophy of Law", "δ", 205,
     "Not built: folder 039 holds a different book, and the corpus's single law lecture cannot carry a subfield."),
]
UNBUILT = {"philosophy-of-law"}


# ---------------------------------------------------------------- entries

def parse_entry(path, title_lookup, note_map):
    text = read(path)
    lines = text.splitlines()
    title = lines[0].lstrip("# ").strip()
    slug = path.stem
    aka = ""
    sub_display = ""
    if len(lines) > 1:
        meta = lines[1].strip().strip("*")
        m = re.match(r"Subfield:\s*([^·]+?)\s*(?:·\s*Also known as:\s*(.*))?$", meta)
        if m:
            sub_display = m.group(1).strip()
            aka = (m.group(2) or "").strip()

    sections = {}
    for head, body in split_sections(text, "##"):
        if head:
            sections[head] = body

    videos = [{"id": vid, "title": t} for t, vid in YT_RE.findall(sections.get("The 90-second version", ""))]

    positions = []
    for m in re.finditer(r"^### (.+)$", sections.get("Positions", ""), re.M):
        start = m.end()
        nxt = re.search(r"^### ", sections["Positions"][start:], re.M)
        body = sections["Positions"][start : start + nxt.start()] if nxt else sections["Positions"][start:]
        positions.append({"name": m.group(1).strip(), "blocks": parse_blocks(body.strip())})

    thought = []
    for item in bullets_of(sections.get("Thought experiments", "")):
        bm = re.match(r"\*\*(.+?)\*\*\s*(.*)$", item, re.S)
        if bm:
            thought.append({"name": bm.group(1).strip(), "text": bm.group(2).strip()})
        else:
            thought.append({"name": None, "text": item})

    ladder = []
    for item in bullets_of(sections.get("Source ladder", "")):
        lm = re.match(r"^([A-Z][^:]{0,40}):\s*(.*)$", item, re.S)
        if lm:
            ladder.append({"label": lm.group(1).strip(), "text": lm.group(2).strip()})
        else:
            ladder.append({"label": None, "text": item})

    connections = []
    for item in bullets_of(sections.get("Connections", "")):
        cm = re.match(r"^\[([^\]]+)\]\(([^)]+?\.md)\)\s*[—–]?\s*(.*)$", item, re.S)
        rec = {"slug": None, "title": None, "text": item}
        if cm:
            cslug = title_lookup.get(norm(Path(cm.group(2)).stem.replace("-", " ")))
            if cslug:
                rec["slug"] = cslug
                rec["title"] = cm.group(1)
        connections.append(rec)

    sources_md = sections.get("Sources read for this entry", "")
    book_nums = sorted(set(BOOK_NUM_RE.findall(sources_md)))

    extra = [
        {"heading": h, "md": body}
        for h, body in split_sections(text, "##")
        if h and h not in {
            "The question", "The 90-second version", "Positions", "Thought experiments",
            "Source ladder", "Where the debate stands", "Connections", "Sources read for this entry",
        }
    ]

    note = note_map.get(slug, {})
    return {
        "slug": slug,
        "subfield": path.parent.name,
        "title": title,
        "aka": aka,
        "sub_display": sub_display,
        "note": note.get("note", ""),
        "pilot": note.get("pilot", False),
        "question": sections.get("The question", ""),
        "ninety": sections.get("The 90-second version", ""),
        "videos": videos,
        "positions": positions,
        "thought": thought,
        "ladder": ladder,
        "verdict": sections.get("Where the debate stands", ""),
        "connections": connections,
        "sources": bullets_of(sources_md),
        "extra": extra,
        "book_nums": book_nums,
    }


def parse_blocks(body):
    out = chunks(body)
    blocks = []
    i = 0
    while i < len(out):
        ch = out[i]
        if ch["kind"] == "bullets":
            premise_items = [PREMISE_RE.match("- " + it) for it in ch["items"]]
            hits = sum(1 for m in premise_items if m)
            if ch["items"] and hits >= max(2, len(ch["items"]) - 1) and hits * 2 >= len(ch["items"]):
                steps = []
                for it, m in zip(ch["items"], premise_items):
                    if m:
                        steps.append({"tag": re.sub(r"\s+", " ", m.group(1)), "text": m.group(2)})
                # attach to a preceding arg-head paragraph if unused
                prev = blocks[-1] if blocks else None
                if prev and prev.get("type") == "p" and prev.pop("pending_arg", False):
                    blocks[-1] = {
                        "type": "arg", "label": prev.get("label"), "source": prev.get("source"),
                        "text": prev.get("text"), "steps": steps,
                    }
                else:
                    blocks.append({"type": "arg", "label": None, "source": None, "text": None, "steps": steps})
            else:
                blocks.append({"type": "ul", "items": ch["items"]})
            i += 1
            continue
        # paragraph
        text = ch["text"]
        m = ARG_HEAD_RE.match(text)
        if m:
            nxt = out[i + 1] if i + 1 < len(out) else None
            will_arg = bool(
                nxt and nxt["kind"] == "bullets"
                and sum(1 for it in nxt["items"] if PREMISE_RE.match("- " + it)) >= max(2, len(nxt["items"]) - 1)
            )
            if will_arg:
                blocks.append({"type": "p", "label": m.group(1).strip(), "source": m.group(2).strip(),
                               "text": m.group(3).strip(), "pending_arg": True})
                i += 1
                continue
            blocks.append({"type": "p", "label": m.group(1).strip(), "source": m.group(2).strip(),
                           "text": m.group(3).strip()})
            i += 1
            continue
        m = LABELED_RE.match(text)
        if m:
            blocks.append({"type": "p", "label": m.group(1).strip(), "source": None, "text": m.group(2).strip()})
            i += 1
            continue
        blocks.append({"type": "p", "label": None, "source": None, "text": text})
        i += 1
    for b in blocks:
        b.pop("pending_arg", None)
    return blocks


def bullets_of(body):
    return [m.group(1).strip() for m in re.finditer(r"^- (.*)$", body or "", re.M)]


# ---------------------------------------------------------------- books

def parse_book(path, title_lookup):
    text = read(path)
    lines = text.splitlines()
    title = lines[0].lstrip("# ").strip()
    title = re.sub(r"^Book map\s*[—–-]+\s*", "", title)
    num_m = re.search(r"\b(\d{3})\b", title)
    num = num_m.group(1) if num_m else "???"

    layer = ""
    for ln in lines[1:5]:
        s = ln.strip()
        if not s:
            continue
        if s.startswith("*") and s.endswith("*"):
            layer = s.strip("*")
        break

    secs = split_sections(text, "##")
    coverage = ""
    groups = []
    for head, body in secs:
        if head and head.lower().startswith("coverage"):
            coverage = body if not coverage else coverage + "\n\n" + body
            continue
        prose = []
        chapters = []
        for ch in chunks(body):
            if ch["kind"] == "bullets":
                for item in ch["items"]:
                    chapters.append(parse_chapter(item, title_lookup))
            else:
                ptext = ch["text"]
                # the layer line and the extraction note are rendered from
                # their own fields; don't repeat them as group prose
                if re.match(r"^Book layer\b", ptext.strip().lstrip("*")) or \
                   re.match(r"^\*\*Extraction note", ptext.strip()):
                    continue
                prose.append(ptext)
        groups.append({"heading": head, "prose": prose, "chapters": chapters})

    flag_text = title + " " + layer + " " + " ".join(g["prose"][0] if g["prose"] else "" for g in groups[:1])
    flags = {
        "mislabelled": bool(re.search(r"MISLABELLED|different book|⚠", title + " " + layer)),
        "reconstruction": bool(re.search(r"RECONSTRUCTION|reconstruction|reconstructed", title + " " + layer + " " + (coverage or ""))),
        "stubs": bool(re.search(r"stub", text[:4000])),
        "no_text": bool(re.search(r"NO BOOK TEXT|no chapter text at all|zero of", title + " " + text[:4000])),
    }

    extraction = ""
    for para in re.split(r"\n\s*\n", text):
        if para.lstrip().startswith("**Extraction note"):
            extraction = re.sub(r"\s*\n\s*", " ", para).strip()
            break

    fed = []
    for g in groups:
        for c in g["chapters"]:
            for s in c["entries"]:
                if s not in fed:
                    fed.append(s)

    return {
        "id": path.stem,
        "num": num,
        "title": title,
        "layer": layer,
        "extraction": extraction,
        "flags": flags,
        "groups": groups,
        "coverage": coverage,
        "fed": fed,
    }


def parse_chapter(item, title_lookup):
    bm = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", item, re.S)
    title, rest = (bm.group(1).strip(), bm.group(2).strip()) if bm else (None, item)
    entries, unresolved, star = [], [], "★" in rest
    m = re.search(r"→\s*(.*)", rest)
    if m:
        # the entry references are the italic runs between the arrow and the
        # first sentence end; later italics in the note are mere emphasis
        refs = re.split(r"(?<=\S)\.\s", m.group(1), maxsplit=1)[0]
        for t in re.findall(r"\*([^*]+)\*", refs):
            slug = resolve_title(t, title_lookup)
            if slug and slug not in entries:
                entries.append(slug)
            elif not slug and t not in unresolved:
                unresolved.append(t.strip())
    return {"title": title, "note": rest, "entries": entries, "unresolved": unresolved, "star": star}


def resolve_title(t, title_lookup):
    key = norm(t)
    if not key:
        return None
    if key in title_lookup:
        return title_lookup[key]
    for k, slug in title_lookup.items():
        if key.startswith(k) or k.startswith(key):
            return slug
    for k, slug in title_lookup.items():
        if key in k or k in key:
            return slug
    return None


# ---------------------------------------------------------------- lectures

def parse_lectures(path):
    lectures = {}
    for line in read(path).splitlines():
        m = LECTURE_ROW_RE.match(line.strip())
        if not m:
            continue
        vid, title, assignment = m.group(1), m.group(2).strip(), m.group(3).strip()
        rec = {"id": vid, "title": title, "status": "unassigned", "note": "", "refs": []}
        if assignment.startswith("—") or assignment.lower().startswith("unassigned"):
            pass
        elif assignment.lower().startswith("unusable"):
            rec["status"] = "unusable"
            rec["note"] = re.sub(r"^unusable\s*[—–-]+\s*", "", assignment, flags=re.I)
        else:
            rec["status"] = "assigned"
            for em in ENTRY_REF_RE.finditer(assignment):
                slug = Path(em.group(1)).stem
                star = bool(em.group(2))
                for r in rec["refs"]:
                    if r["slug"] == slug:
                        r["star"] = r["star"] or star
                        break
                else:
                    rec["refs"].append({"slug": slug, "star": star})
        lectures[vid] = rec
    return lectures


# ---------------------------------------------------------------- index.md + DATA_QUALITY

def parse_index():
    # the one-line problem notes, pilot flags, and book catalogue annotations
    # were authored in the original index.md; the published index.md is now a
    # short pointer page, so the full tables live in index-full.md beside this
    # script and are the build input for those fields
    src = Path(__file__).resolve().parent / "index-full.md"
    if not src.exists():
        src = KB / "index.md"
    text = read(src)
    notes, title_by_slug = {}, {}
    for m in re.finditer(r"^- \[([^\]]+)\]\((entries/[^)]+\.md)\)\s*(?:—\s*(.*))?$", text, re.M):
        slug = Path(m.group(2)).stem
        title_by_slug[slug] = m.group(1).strip()
        note = (m.group(3) or "").strip()
        pilot = bool(re.search(r"\*\(pilot\)\*\s*$", note))
        note = re.sub(r"\s*\*\(pilot\)\*\s*$", "", note).strip(" —–")
        notes[slug] = {"note": note, "pilot": pilot}
    catalog = {}
    for m in re.finditer(r"^\|\s*(\d{3})\s*\|(.*?)\|\s*\[[^\]]*\]\((book-maps/[^)]+\.md)\)\s*\|$", text, re.M):
        catalog[Path(m.group(3)).stem] = m.group(2).strip()
    sm = re.search(r"^## Known shortfalls.*?$\n(.*)", text, re.M | re.S)
    shortfalls = sm.group(1).strip() if sm else ""
    return notes, title_by_slug, catalog, shortfalls


def parse_quality():
    text = read(KB / "DATA_QUALITY.md")
    secs = split_sections(text, "##")
    intro = secs[0][1] if secs and secs[0][0] is None else ""
    return {
        "intro": intro,
        "sections": [{"heading": h, "md": b} for h, b in secs if h],
    }


# ---------------------------------------------------------------- main

def main():
    notes, bullet_titles, catalog, shortfalls = parse_index()

    title_lookup = {}
    entry_paths = sorted(KB.glob("entries/*/*.md"))
    for p in entry_paths:
        slug = p.stem
        title_lookup[norm(p.stem.replace("-", " "))] = slug
        h1 = read(p).splitlines()[0].lstrip("# ").strip()
        title_lookup[norm(h1)] = slug
        if slug in bullet_titles:
            title_lookup[norm(bullet_titles[slug])] = slug

    entries = {}
    sub_entries = {}
    for p in entry_paths:
        e = parse_entry(p, title_lookup, notes)
        entries[e["slug"]] = e
        sub_entries.setdefault(e["subfield"], []).append(e["slug"])

    books = {}
    for p in sorted(KB.glob("book-maps/*.md")):
        b = parse_book(p, title_lookup)
        b["catalog"] = catalog.get(p.stem, "")
        books[b["id"]] = b

    # entry <-> book cross-links
    num_to_ids = {}
    for b in books.values():
        num_to_ids.setdefault(b["num"], []).append(b["id"])
    for e in entries.values():
        ids = []
        for n in e["book_nums"]:
            for bid in num_to_ids.get(n, []):
                if bid not in ids:
                    ids.append(bid)
        e["books"] = ids

    lectures = parse_lectures(KB / "lectures-index.md")
    for vid, lec in lectures.items():
        for r in lec["refs"]:
            if r["slug"] in entries:
                entries[r["slug"]].setdefault("lectures", [])
                if vid not in entries[r["slug"]]["lectures"]:
                    entries[r["slug"]]["lectures"].append(vid)
                if r["star"]:
                    entries[r["slug"]].setdefault("frontdoor", [])
                    if vid not in entries[r["slug"]]["frontdoor"]:
                        entries[r["slug"]]["frontdoor"].append(vid)
    for e in entries.values():
        e.setdefault("lectures", [])
        e.setdefault("frontdoor", [])
        # front-door videos from the 90-second section may not be starred in the register
        for v in e["videos"]:
            if v["id"] in lectures and v["id"] not in e["frontdoor"]:
                e["frontdoor"].append(v["id"])
        e["lectures"].sort()
        e["frontdoor"].sort()

    assigned = sum(1 for l in lectures.values() if l["status"] == "assigned")
    frontdoor = sum(1 for l in lectures.values() if any(r["star"] for r in l["refs"]))
    unassigned = sum(1 for l in lectures.values() if l["status"] == "unassigned")
    unusable = sum(1 for l in lectures.values() if l["status"] == "unusable")

    subfields = []
    for sid, name, glyph, hue, blurb in SUBFIELDS:
        subfields.append({
            "id": sid, "name": name, "glyph": glyph, "hue": hue, "blurb": blurb,
            "unbuilt": sid in UNBUILT,
            "entries": sorted(sub_entries.get(sid, [])),
        })

    data = {
        "version": 1,
        "generated": "2026-10-21",
        "stats": {
            "entries": len(entries),
            "subfields": sum(1 for s in subfields if not s["unbuilt"]),
            "books": len(books),
            "lectures_total": len(lectures),
            "lectures_assigned": assigned,
            "lectures_frontdoor": frontdoor,
            "lectures_unassigned": unassigned,
            "lectures_unusable": unusable,
        },
        "subfields": subfields,
        "entries": entries,
        "books": books,
        "lectures": lectures,
        "quality": parse_quality(),
        "shortfalls": shortfalls,
    }

    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"entries={len(entries)} books={len(books)} lectures={len(lectures)} "
          f"(assigned={assigned}, frontdoor={frontdoor}, unassigned={unassigned}, unusable={unusable})")
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")

    # sanity: report unresolved entry-title references in book maps
    misses = []
    for b in books.values():
        for g in b["groups"]:
            for c in g["chapters"]:
                for t in c["unresolved"]:
                    misses.append((b["num"], t))
    if misses:
        print("UNRESOLVED chapter→entry references:")
        for num, t in misses:
            print(f"  [{num}] {t}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
