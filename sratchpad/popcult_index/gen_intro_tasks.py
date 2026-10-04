"""Generate writer-agent task files for concept/philosopher/book intros.

Reads merged_index.json + taxonomy.json, writes tasks/intro_*.json batches:
  intro_concepts_NN.json  [{slug, name, domain, samples:[{book, n, title, relation}]}]
  intro_phils_NN.json     [{slug, name, dates, domain, concepts:[names], n_ch}]
  intro_books_NN.json     [{book, title, essays:[chapter titles], samples:[relations]}]
"""
import json
from pathlib import Path

BASE = Path(r"B:\ai_philosophy\sratchpad\popcult_index").resolve()
TASKS = BASE / "tasks"
TASKS.mkdir(exist_ok=True)

merged = json.loads((BASE / "merged_index.json").read_text(encoding="utf-8"))
tax = json.loads((BASE / "taxonomy.json").read_text(encoding="utf-8"))
meta = merged["taxonomy_meta"]

CONC_BATCH = 24
PHIL_BATCH = 24
BOOK_BATCH = 10


def concept_samples(cslug, limit=8):
    chs = merged["concept_chapters"].get(cslug, [])
    # prefer chapters whose relation is non-trivial, spread across books
    seen, out = set(), []
    for c in sorted(chs, key=lambda x: len(x.get("relation", "")), reverse=True):
        if c["book"] in seen and len(seen) < limit:
            continue
        seen.add(c["book"])
        out.append({"book": c["book"], "n": c["n"], "title": c["title"],
                    "relation": c.get("relation", "")})
        if len(out) >= limit:
            break
    return out


def concept_batches():
    slugs = [c for c in merged["concept_chapters"]]
    for i in range(0, len(slugs), CONC_BATCH):
        batch = []
        for s in sorted(slugs[i:i + CONC_BATCH]):
            m = tax["concepts"].get(s, {})
            batch.append({"slug": s, "name": m.get("n", s),
                          "domain": meta["concept_dom"].get(s, ""),
                          "samples": concept_samples(s)})
        p = TASKS / ("intro_concepts_%02d.json" % (i // CONC_BATCH))
        p.write_text(json.dumps(batch, ensure_ascii=False, indent=1),
                     encoding="utf-8")
        print(p.name, len(batch))


def phil_batches():
    slugs = [p for p in merged["philosopher_usage"]]
    for i in range(0, len(slugs), PHIL_BATCH):
        batch = []
        for s in sorted(slugs[i:i + PHIL_BATCH]):
            m = tax["philosophers"].get(s, {})
            usage = merged["philosopher_usage"][s]
            batch.append({
                "slug": s, "name": m.get("n", s), "dates": m.get("d", ""),
                "domain": meta["phil_dom"].get(s, ""),
                "concepts": [tax["concepts"].get(c, c)
                             for c in sorted(usage["concepts"],
                                             key=lambda c: -usage["concepts"][c])[:10]],
                "n_chapters": usage["chapters"]})
        p = TASKS / ("intro_phils_%02d.json" % (i // PHIL_BATCH))
        p.write_text(json.dumps(batch, ensure_ascii=False, indent=1),
                     encoding="utf-8")
        print(p.name, len(batch))


def book_batches():
    books = sorted(merged["chapters"].keys())
    for i in range(0, len(books), BOOK_BATCH):
        batch = []
        for b in books[i:i + BOOK_BATCH]:
            chs = merged["chapters"][b]
            essays = [(int(n), r) for n, r in chs.items()
                      if r["done"] and r["kind"] == "chapter"]
            essays.sort()
            samples = [r["relation"] for _n, r in essays
                       if len(r.get("relation", "")) > 120][:6]
            batch.append({
                "book": b,
                "essays": [r["title"] for _n, r in essays][:20],
                "samples": samples})
        p = TASKS / ("intro_books_%02d.json" % (i // BOOK_BATCH))
        p.write_text(json.dumps(batch, ensure_ascii=False, indent=1),
                     encoding="utf-8")
        print(p.name, len(batch))


concept_batches()
phil_batches()
book_batches()
