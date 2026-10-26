# philosophy_readings knowledge base — navigation & linking design

Proposed 2026-10-15. Owner approval required before building.
Corpus: `data\philosophy_readings\` — 42 books (20 epubs extracted = 915
chapters / 2.2M words; PDF pass ongoing; 2 reconstructions) + 817 Carneades
YouTube transcripts. Existing asset: popcult-index explorer (485 concepts /
264 philosophers slugs with written intros, live on site).

## Design principles

1. **The spine is the discipline.** This corpus is a curriculum, not a pop
   index: the top-level navigation is the classic fields — Epistemology,
   Metaphysics, Ethics, Political Philosophy, Philosophy of Religion,
   Aesthetics, Philosophy of Language, Philosophy of Science & Mathematics,
   Critical Thinking & Argumentation, Philosophy of History/Law/Society.
   A field map (`fields.json`, curated, extend-only like the taxonomy)
   orders the corpus the way a philosophy degree does.
2. **Concepts are the connective tissue.** Reuse the popcult taxonomy
   slugs (485 concepts / 264 philosophers, extend-only — the central
   rule from the popcult build). A concept page aggregates every
   appearance across both libraries.
3. **Two material layers with different roles:**
   - Carneades videos = the **explainer layer** — short, definitional
     ("What is X?" / "Ninety Second Philosophy"). Each video binds to 1-3
     concepts it explains.
   - Books = the **treatment layer** — argumentative, deep. Each chapter
     binds to the concepts it teaches/argues about, with an honest
     relation note (what it argues, how it treats the concept — never
     tighter than the text supports; holes logged).
4. **Philosophers are the third axis** — a philosopher page shows: their
   works in the corpus, videos about them, the concepts they own, and
   their popcult-KB appearances.
5. **Curriculum reading paths** (the textbook value-add the popcult KB
   lacks): each field carries an ordered path — e.g. Political Philosophy:
   Kymlicka's Introduction → Rawls → Nozick → Goodin/Pettit primary
   readings → Arrow/Sen for the formal tier. Authored by curation (the
   reading-agent notes inform it), stored in fields.json.

## Data model (reuses the popcult machinery)

- `units\uNNN.json` — reading units; books use the popcult balance
  (≤90k words / ≤42 content chapters); videos batch 40-60 transcripts per
  unit (they are 800-2,000 words each).
- `notes\uNNN.json` — same schema as popcult: per chapter/video
  `{n, file, kind: chapter|video|front|notes, philosophers[], concepts[],
  relation}` + holes[]. Relation note conventions differ by kind:
  - chapter: what it argues + how it treats the concept (popcult style);
  - video: which concept it explains + accuracy/level note (these are
    amateur explainer videos — the note may honestly say "introduces X
    simply; skips Y").
- `taxonomy.json` — popcult taxonomy + extensions (new slugs expected for
  this corpus: incompleteness, social-choice, varieties-of-gibberish,
  bullshit-frankfurt vs bullshit-harry (already there?), critical-thinking
  terms, 李天命's 思方學 concepts).
- `fields.json` — NEW: `{field_slug: {name, name_zh, description,
  concepts[], philosophers[], books[], path[]}}`; extend-only.
- `merge_notes.py` variant → `merged_index.json` → `build_explorer.py`
  variant → `knowledge-base\readings-index\data.json`.

## Reading pass

- ~25 book units + ~16 video units ≈ 40-45 units, 3-5 concurrent agents,
  1-2M tokens/unit → roughly 50-90M tokens total, a week-plus of polite
  cadence (mirror-download pace no longer gates; transcripts are done).
- Special cases: 李天命 (Chinese — relation notes may quote Chinese terms;
  concepts stay English slugs); GEB / Arrow / Social Choice (technical —
  format-junk chapters in Language Matters (284) and Social Choice (201)
  need the popcult ≥200-word content filter); reconstructed books are
  indexed at the toc.md level only (one unit each, kind-honest).
- After each wave: check_notes.py; every ~3 waves: merge + build.

## Explorer UI (new, separate from /popcult)

`/readings` two-pane explorer, same interaction patterns as /popcult but
three browse roots:
- **By field** (default): field → its concepts, philosophers, books, and
  the curriculum path;
- **By concept**: concept page = intro + videos (explainer layer) +
  chapters (treatment layer, with relation notes) + cross-link "this
  concept applied in the pop-culture library";
- **By philosopher**: works, videos, concepts.
Plus the reverse view the books afford: **book page** → its chapters with
their concept bindings (the textbook's own TOC, made clickable).
Bilingual (EN / HK-中) same as popcult; relation notes written in English
first, translated in a later pass.

## Phases

1. **Phase 1 (build):** fields.json draft; taxonomy extension list from a
   hole-survey of the corpus; reading pass; explorer with field/concept/
   philosopher roots. Deliverable: live `/readings` page.
2. **Phase 2 (curriculum):** authored reading paths per field; book-level
   TOC views; bilingual notes.
3. **Phase 3 (cross-links):** concept bridges into /popcult (same slug =
   link both ways), so the two libraries form one philosophy knowledge
   graph over the whole site.

## What I need from the owner

- Approve/adjust the field list and the concept-centric linking.
- Approve the reading-pass token budget (~50-90M).
- Name the route: `/readings` proposed.
