"""Render the Philosophy-Pop Culture Reverse Index into knowledge-base markdown.

Reads sratchpad/popcult_index/merged_index.json (+ optional intros.json),
writes knowledge-base/popcult-index/*.md: hub, one doc per domain, and
chunked by-book companion docs. Partial coverage is rendered with explicit
stats so in-progress builds are never misleading.
"""
import json
import re
from pathlib import Path

BASE = Path(r"B:\ai_philosophy\sratchpad\popcult_index").resolve()
REPO = Path(r"B:\ai_philosophy").resolve()
OUT_DIR = REPO / "knowledge-base" / "popcult-index"

CHUNK_BULLETS = 1500


def out_path(name):
    p = (OUT_DIR / name).resolve()
    b = OUT_DIR.resolve()
    import os
    if os.path.commonpath([str(p), str(b)]) != str(b):
        raise ValueError("render path outside output dir")
    return p


def load_inputs():
    merged = json.loads((BASE / "merged_index.json").read_text(encoding="utf-8"))
    tax = json.loads((BASE / "taxonomy.json").read_text(encoding="utf-8"))
    intros = {}
    ipath = BASE / "intros.json"
    if ipath.exists():
        intros = json.loads(ipath.read_text(encoding="utf-8"))
    book_intros = {}
    bpath = BASE / "book_intros.json"
    if bpath.exists():
        book_intros = json.loads(bpath.read_text(encoding="utf-8"))
    return merged, intros, tax, book_intros


def book_display(book):
    return re.sub(r"^\d+\s*-\s*", "", book)


def book_letter(book):
    d = book_display(book).strip()
    return (d[0].upper() if d and d[0].isalpha() else "#")


def chapter_bullet(book, n, title, relation, suffix=""):
    rel = (" — " + relation) if relation else ""
    return '- **%s**, ch. %d "%s"%s%s' % (book_display(book), n, title, rel, suffix)


def concept_line(cslug, meta, merged):
    chs = merged["concept_chapters"].get(cslug, [])
    books = len({c["book"] for c in chs})
    return (chs, "**%s** — %d chapters across %d books"
            % (meta["n"], len(chs), books))


def render_domain(dom, dom_name, merged, meta, intros, tax):
    phil_by_dom = {p: v for p, v in merged["philosopher_usage"].items()
                   if meta["phil_dom"].get(p) == dom}
    lines = ["# %s" % dom_name, ""]
    n_con = sum(1 for c, cm in meta["concept_dom"].items()
                if cm == dom and c in merged["concept_chapters"])
    lines.append("*%d philosophers · %d concepts with chapters indexed so far. "
                 "Each entry: what the concept holds, then the chapters that "
                 "apply it, with what each chapter actually argues.*"
                 % (len(phil_by_dom), n_con))
    lines.append("")
    # philosophers with usage
    for p in sorted(phil_by_dom, key=lambda x: -phil_by_dom[x]["chapters"]):
        usage = phil_by_dom[p]
        pname = meta["philosophers"].get(p, p)
        lines.append("## %s" % pname)
        lines.append("")
        pd = tax_dates(p, tax)
        lead = "%s · " % pd if pd else ""
        lines.append("*%s%d chapters in the corpus.*" % (lead, usage["chapters"]))
        lines.append("")
        pintro = intros.get("phil:" + p, "")
        if pintro:
            lines.append(pintro)
            lines.append("")
        used = sorted(usage["concepts"], key=lambda c: -usage["concepts"][c])
        for cslug in used:
            chs = merged["concept_chapters"].get(cslug, [])
            if not chs:
                continue
            lines.append("### %s" % meta["concepts"].get(cslug, cslug))
            lines.append("")
            intro = intros.get(cslug, "")
            if intro:
                lines.append(intro)
                lines.append("")
            for c in sorted(chs, key=lambda x: (x["book"], x["n"])):
                lines.append(chapter_bullet(c["book"], c["n"], c["title"],
                                            c["relation"]))
            lines.append("")
        # chapters citing the philosopher without a concept
        direct = direct_chapters(merged, p)
        if direct:
            lines.append("### General mentions")
            lines.append("")
            for c in direct:
                lines.append(chapter_bullet(c["book"], c["n"], c["title"],
                                            c["relation"]))
            lines.append("")
    # school-level concepts of this domain
    schools = [c for c, cm in meta["concept_dom"].items()
               if cm == dom and not meta["concept_phil"].get(c)
               and c in merged["concept_chapters"]]
    if schools:
        lines.append("## Schools & General Topics")
        lines.append("")
        for cslug in sorted(schools,
                            key=lambda c: -len(merged["concept_chapters"].get(c, []))):
            chs = merged["concept_chapters"].get(cslug, [])
            lines.append("### %s" % meta["concepts"].get(cslug, cslug))
            lines.append("")
            intro = intros.get(cslug, "")
            if intro:
                lines.append(intro)
                lines.append("")
            for c in sorted(chs, key=lambda x: (x["book"], x["n"])):
                lines.append(chapter_bullet(c["book"], c["n"], c["title"],
                                            c["relation"]))
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def tax_dates(pslug, tax):
    return tax["philosophers"].get(pslug, {}).get("d", "")


def direct_chapters(merged, pslug):
    out = []
    for book, chs in merged["chapters"].items():
        for n, rec in chs.items():
            if rec["done"] and pslug in rec["philosophers"] and not rec["concepts"]:
                out.append({"book": book, "n": int(n), "title": rec["title"],
                            "relation": rec["relation"]})
    out.sort(key=lambda x: (x["book"], x["n"]))
    return out


def render_hub(merged, meta):
    prog = merged["progress"]
    lines = ["# The Philosophy–Pop Culture Reverse Index", ""]
    lines.append("Most pop-philosophy books work forward: take an episode, tell "
                 "what happened, then attach a philosopher. This index works "
                 "backward. It is organized by **philosopher and concept** — for "
                 "each one you get a short statement of the idea, then the book "
                 "chapters that apply it to a pop-culture work, each with a note "
                 "on what that chapter actually argues.")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append("- Corpus: **%d books · %d chapters** (Open Court *Popular Culture "
                 "and Philosophy*, Wiley-Blackwell *… and Philosophy*, and friends)"
                 % (prog["books_in_units"], prog["chapters_total"]))
    lines.append("- Chapters read chapter-by-chapter so far: **%d of %d** (%.0f%%)"
                 % (prog["chapters_read"], prog["chapters_total"],
                    100.0 * prog["chapters_read"] / max(1, prog["chapters_total"])))
    lines.append("- Chapters mapped to index entries: **%d**" % prog["chapters_mapped"])
    lines.append("- Concepts in the index: **%d** (%d already with chapters) · "
                 "Philosophers: **%d** (%d already with chapters)"
                 % (len(meta["concepts"]), prog["concepts_used"],
                    len(meta["philosophers"]), prog["philosophers_used"]))
    if prog["chapters_read"] < prog["chapters_total"]:
        lines.append("")
        lines.append("> **Build in progress** — the reading pass is still working "
                     "through the corpus. Stats and pages will grow as books are "
                     "completed.")
    lines.append("")
    lines.append("## Browse by tradition")
    lines.append("")
    dom_order = ["ancient", "eastern-world", "medieval-early-modern",
                 "kant-german-idealism", "nineteenth-century",
                 "utilitarian-consequentialist", "existentialism-phenomenology",
                 "mind-language-metaphysics", "knowledge-science-reality",
                 "ethics-moral-psychology", "political-social",
                 "pragmatism-american", "feminism-gender-race",
                 "environment-animal", "religion-meaning"]
    for dom in dom_order:
        n_phil = sum(1 for p, pd in meta["phil_dom"].items()
                     if pd == dom and p in merged["philosopher_usage"])
        n_con = sum(1 for c, cm in meta["concept_dom"].items()
                    if cm == dom and c in merged["concept_chapters"])
        lines.append("- [%s](%s.md) — %d philosophers · %d concepts"
                     % (meta["domains"][dom]["n"], dom, n_phil, n_con))
    lines.append("")
    lines.append("## Most-applied concepts")
    lines.append("")
    top = sorted(merged["concept_chapters"], key=lambda c: -len(merged["concept_chapters"][c]))[:25]
    for cslug in top:
        chs, line = concept_line(cslug, {"n": meta["concepts"].get(cslug, cslug)},
                                 merged)
        dom = meta["concept_dom"].get(cslug, "")
        lines.append("- %s — see [%s](%s.md)"
                     % (line, meta["domains"].get(dom, {}).get("n", dom), dom))
    lines.append("")
    lines.append("## Most-cited philosophers")
    lines.append("")
    pu = merged["philosopher_usage"]
    for p in sorted(pu, key=lambda x: -pu[x]["chapters"])[:25]:
        dom = meta["phil_dom"].get(p, "")
        lines.append("- **%s** — %d chapters — see [%s](%s.md)"
                     % (meta["philosophers"].get(p, p), pu[p]["chapters"],
                        meta["domains"].get(dom, {}).get("n", dom), dom))
    lines.append("")
    book_docs = book_chunk_names(merged)
    lines.append("## The books")
    lines.append("")
    lines.append("Every chapter of every book, with its index entries — the "
                 "forward view of the same map. Each book opens with a short "
                 "introduction: what the pop-culture work is and why it merits "
                 "a book of philosophy.")
    lines.append("")
    for name, desc in book_docs:
        lines.append("- [%s](%s)" % (desc, name))
    lines.append("")
    lines.append("## How this was built")
    lines.append("")
    lines.append("Every chapter was read in full by a dedicated reading pass. For "
                 "each chapter the reader records which philosophers and concepts "
                 "the chapter *actually uses* (not name-drops) and writes 2–4 "
                 "sentences on what the chapter argues and how it connects the "
                 "pop-culture material to the philosophy. Chapters that fit no "
                 "existing index entry are logged as gaps; the index grows to "
                 "absorb them. Coverage numbers above are exact counts of what "
                 "has been read so far — never estimates.")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def book_chunks(merged):
    books = sorted(merged["chapters"].keys(), key=book_display)
    chunks = []
    cur, count, cur_letter = [], 0, None
    for b in books:
        n = sum(1 for r in merged["chapters"][b].values() if r["done"])
        if cur and count + n > CHUNK_BULLETS and book_letter(b) != cur_letter:
            chunks.append(cur)
            cur, count = [], 0
        cur.append(b)
        count += n
        cur_letter = book_letter(b)
    if cur:
        chunks.append(cur)
    return chunks


def book_chunk_names(merged):
    chunks = book_chunks(merged)
    names = []
    for ch in chunks:
        a = book_letter(ch[0])
        z = book_letter(ch[-1])
        if a == z:
            names.append(("books-%s.md" % a.lower(),
                          "Books %s–%s (%d)" % (a, z, len(ch))))
        else:
            stem = re.sub(r"[^a-z]", "", (a + z).lower())
            names.append(("books-%s.md" % stem,
                          "Books %s–%s (%d)" % (a, z, len(ch))))
    return names


def render_book_doc(books, merged, meta, book_intros):
    lines = []
    for i, b in enumerate(books):
        if i == 0:
            lines.append("# %s through %s" % (book_letter(books[0]),
                                              book_letter(books[-1])))
            lines.append("")
        chs = merged["chapters"][b]
        lines.append("## %s" % book_display(b))
        lines.append("")
        bintro = book_intros.get(b, "")
        if bintro:
            lines.append(bintro)
            lines.append("")
        for n in sorted(int(k) for k in chs):
            rec = chs[str(n)]
            if not rec["done"]:
                lines.append('- ch. %d "%s" *(not yet read)*' % (n, rec["title"]))
                continue
            if rec["kind"] in ("front", "notes", "interlude"):
                lines.append('- ch. %d "%s" *(%s)*' % (n, rec["title"], rec["kind"]))
                continue
            tags = []
            if rec["philosophers"]:
                tags.append(", ".join(meta["philosophers"].get(p, p)
                                      for p in rec["philosophers"]))
            if rec["concepts"]:
                tags.append("; ".join(meta["concepts"].get(c, c)
                                      for c in rec["concepts"]))
            tag = (" **·** " + " — ".join(tags)) if tags else " *(no index entry yet)*"
            rel = (" — " + rec["relation"]) if rec["relation"] else ""
            lines.append('- ch. %d "%s"%s%s' % (n, rec["title"], tag, rel))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    merged, intros, tax, book_intros = load_inputs()
    meta = merged["taxonomy_meta"]
    dom_names = {k: v["n"] for k, v in meta["domains"].items()}
    hub = render_hub(merged, meta)
    out_path("index.md").write_text(hub, encoding="utf-8")
    dom_order = list(dom_names)
    for dom in dom_order:
        doc = render_domain(dom, dom_names[dom], merged, meta, intros, tax)
        out_path(dom + ".md").write_text(doc, encoding="utf-8")
    chunks = book_chunks(merged)
    names = book_chunk_names(merged)
    for ch_books, (name, _desc) in zip(chunks, names):
        doc = render_book_doc(ch_books, merged, meta, book_intros)
        out_path(name).write_text(doc, encoding="utf-8")
    print("rendered: index.md + %d domain docs + %d book docs -> %s"
          % (len(dom_order), len(chunks), OUT_DIR))


if __name__ == "__main__":
    main()
