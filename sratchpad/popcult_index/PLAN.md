# PLAN: Philosophy–Pop Culture Reverse Index (resume protocol)

Goal: a concept-first reverse index of the local pop-philosophy corpus
(`B:\ai_philosophy\philosophy_pop_culture\epub`, 267 books). Every chapter is
read in full by a reading agent; each chapter gets the philosophers/concepts it
actually uses plus a 2–4 sentence faithful note on what it argues. Chapters
that fit no index entry are logged as "holes"; the index grows to absorb them.
Final deliverable: knowledge-base docs on the site + by-book companion.

## State (update this section as work proceeds)

- **2026-10-03 EXTENSION COMPLETE.** Six newly recovered books added to the
  corpus and fully read: 002 Simpsons + 110 Hamilton (epub), 161 Family Guy +
  194 Taylor Swift + 206 Witcher + 235 TV Noir (PDF, extracted by
  `extract_new_pdfs.py`). Corpus now 273 books / 9,999 chapters (450 units,
  u439–u449; oversized units split 2-part). All notes validate clean; 56 holes
  curated → 53 new taxonomy entries (`build_taxonomy.py`, now 251
  philosophers / 445 concepts); `ethical-pragmatism` hole mapped to existing
  `pragmatism`. Intros: 6 new book intros + 53 new taxonomy intros
  (`intro_batches/NEWBOOKS.json` → `intros/NEWBOOKS.json`) + 4 legacy gaps
  filled; `intros.json` 696 keys, book_intros.json 273. `build_explorer.py`
  rebuilt data.json (7.28 MB), served locally, /popcult data verified.
  18 books downloaded from libgen 2026-10-01/03; 25 of 310 confirmed absent
  from the mirror in every format (10 junk PDFs deleted — wrong book or stub).
  Nothing committed (owner's call).

- **BUILD COMPLETE (2026-09-28).** Reading pass 439/439 units (incl. u438 =
  Metallica and Philosophy, extracted from the owner's PDF via
  `extract_metallica.py` + `register_metallica.py`), all notes validate clean.
  Final counts: 267 books · 9,848 chapters read · 5,627 mapped · 2,232 holes.
- Finalization DONE: 2,230 holes aggregated + canonicalized
  (`gen_taxonomy_ext.py`) → 146 accepted entries appended to
  `build_taxonomy.py` (232 philosophers / 411 concepts) → `bindings.json`
  bound 721 hole chapters to the new slugs (no re-reading). Intros generated
  by writer agents in `tasks/` → `intros_out/` → assembled into
  `intros.json` (409 concepts + 228 "phil:"-keyed philosopher intros) and
  `book_intros.json` (268 books, keyed by leading book id like "183"; the
  owner's request: each book intro explains what the pop-culture work is and
  why it merits a philosophy book).
- Publication: the site UI is the **two-pane explorer** the owner merged
  (2026-09-27, PRs #1/#2): `/popcult` route + content.json entry
  `popcult-index` (kind popcult-index) under knowledge-base. It consumes
  `knowledge-base/popcult-index/data.json`, rebuilt by
  `build_explorer.py` (validates refs + book-intro keys; Metallica cover
  extracted from the PDF into `covers/183.webp` and patched in).
  `render_docs.py`-generated markdown (domain/book docs) still renders but
  the domain docs are HUGE (17–84MB) — the explorer supersedes them;
  recommend deleting the per-domain + books-*.md files before any future
  commit (owner's call). Verified locally on a free port: data.json,
  explorer.js, covers, index.md all 200.
- Quota mechanics learned: [1302] burst = retry once; [1308] 5-hour rolling =
  stop until reset; [1310] weekly = stop cleanly. Agent **concurrency** also
  has a user-level cap (~3–5 concurrent agents as of 2026-09-28; background
  launches fail instantly over the cap — dispatch in foreground waves).
- **Handoff (2026-09-22):** the owner asked for a self-contained instruction
  document for another AI agent — it is
  `B:\ai_philosophy\knowledge-base\popcult-index\HANDOFF.md`.
- Extraction: DONE + VERIFIED. `markdown/<book>/chNN - Title.md`, 1:1 with EPUB
  spine (`py -3 verify_extraction.py` → 266/267 pass). Book `071 - The Catcher
  in the Rye…` is an image-only scan (no OCR available) — EXCLUDED from units.
- Work units: DONE. `units/uNNN.json` (438 units; each lists chapters with word
  counts and a `content` array = chapters ≥200 words needing full reading).
- Taxonomy: `build_taxonomy.py` → `taxonomy.json`
  (15 domains, 165 philosophers, 332 concepts after mid-run extensions:
  Bergson, Freud, Jung, Lacan, Isaiah Berlin, Gadamer). Slugs are the
  contract — EXTEND only, never rename.
- Reading pass: 170/438 units in `notes/` as of 2026-09-22 (4,473 chapters
  read, 2,401 mapped, 1,055 holes; `py -3 check_notes.py` → 170 checked, 0
  bad). Still missing: u024–u032 (early-wave failures, never retried), u169,
  u176, u180, u182, u183, then u184–u437. Completed set = whatever `notes/`
  contains; always recompute.
- Quota mechanics learned so far: [1302] burst = retry once, succeeds;
  [1308] 5-hour rolling limit = stop until the reset time in the message;
  [1310] weekly limit = stop cleanly (2026-09-21 wall reset 2026-09-23 16:08).
  A 24-wide wave burned the weekly quota (≈40M tokens). **Max 12 agents/wave.**
- Pipeline built + tested on partial data: merge → render → hub + 15 domain
  docs + books chunks in `B:\ai_philosophy\knowledge-base\popcult-index\`
  (not yet registered in `content.json`).

## Commands (run from B:\ai_philosophy\sratchpad\popcult_index)

- `py -3 check_notes.py` — validate all notes (JSON, coverage, slug validity)
- `py -3 check_notes.py --ids u002,u003` — validate specific units
- `py -3 merge_notes.py` — merge notes → merged_index.json (+ progress stats)
- `py -3 render_docs.py` — render knowledge-base/popcult-index/*.md
- `py -3 build_taxonomy.py` — rebuild taxonomy.json after editing the P/C dicts

## Resume protocol

1. Remaining units = `units/u*.json` minus `notes/*.json`. Keep u002, u003,
   u011 first (they were promised twice).
2. Dispatch via the Agent tool, `subagent_type: general-purpose`, **12 per
   wave**, prompt = TEMPLATE below with the unit id substituted (3 places:
   units path, output path, final message).
3. After each wave: `py -3 check_notes.py --ids …` for the new units.
   Failures: missing file / invalid JSON / missing chapters / unknown slugs →
   re-dispatch that unit once with the same template plus a first line:
   "A previous attempt failed validation (<problem>). Fix and rewrite the
   complete output file." Rate-limit results look like `[1302]…` or
   `[1310]…` → treat the unit as not done; if `[1310] Weekly/Monthly Limit`
   appears, STOP (step 6).
4. When all 438 notes exist and validate: aggregate holes
   (`notes/*.json` → group by suggested_slug; similar names merge manually),
   then extend `build_taxonomy.py` P/C dicts with accepted entries and rebuild
   taxonomy.json. Chapters whose holes were accepted get bound to the new slugs
   via a small script over notes holes (unit+ch → slug) BEFORE merging — do not
   re-read any book.
5. Concept intros: writer agents (small waves) produce `intros.json`
   ({slug: "2–4 sentence intro"}) for every concept in final taxonomy. Rules:
   accurate, no overclaiming, plain English.
6. `py -3 merge_notes.py && py -3 render_docs.py` → final docs.
7. Register in content.json under knowledge-base (hub + 15 domains + book
   docs), verify locally (`py -3 -m http.server <free port>` from repo root,
   check /md/ deep links, both themes; zh falls back to English), then report.
   Do NOT commit/push without the owner's explicit go-ahead.
8. If [1310] quota errors strike again mid-pass: run merge+render, update the
   State section above with the exact completed set, stop cleanly, and report
   (no new automations).

## Known final-render considerations

- Domain docs grow large (ancient.md already ~1MB at 7% coverage). At final
  build, if any domain doc exceeds ~1.5MB, split per-philosopher sub-pages for
  the giants (Plato, Aristotle, Kant, Nietzsche…) and link them from the domain
  doc — revise render_docs.py then, after seeing real sizes.
- Some chapter titles rendered "Unknown" or the book title (EPUB TOC fallback);
  optionally improve doc_title in extract_epub.py before a final re-extract —
  low priority, cosmetic.

## Agent prompt TEMPLATE (substitute UNIT)

Read your work-unit file at B:\ai_philosophy\sratchpad\popcult_index\units\UNIT.json — it names the book, its chapter folder ("path"), and the exact chapter files (with word counts) you must process. Then do the following.

FIRST read B:\ai_philosophy\sratchpad\popcult_index\taxonomy.json — the canonical slugs for philosophers and concepts.

TASK: The unit's "content" array lists the chapter numbers that need FULL reading (essays ≥200 words) — read every one of those completely, in numeric order. All other chapters (covers, TOC pages, part dividers, notes, indexes) — do NOT read them; classify by word count/filename. For EVERY chapter produce one entry:
- "n": chapter number, "file": filename (copy from the unit)
- "kind": "chapter" (an essay in the content list) | "front" (cover/toc/copyright/divider/blank) | "notes" (endnotes/bibliography/acknowledgments/contributor bios/index)
- "philosophers": taxonomy philosopher slugs the chapter actually USES (not mere name-drops), most important first, [] if none
- "concepts": 1–4 taxonomy concept slugs the chapter actually APPLIES to the pop-culture material, most important first, [] if none
- "relation": for kind "chapter" only: 2–4 sentences in your own words stating what THIS chapter actually argues and HOW it connects the pop-culture work to the philosophy — name specific characters/episodes/scenes/arguments. Faithful to the text; never a generic description of the concept itself. Use "" for all other kinds.
- Every chapter number in your unit must appear exactly once, ordered by n.

HOLES: If a chapter is genuinely ABOUT a distinct philosopher or concept that taxonomy.json lacks, do not force it: map whatever fits, leave slugs [] if nothing fits, and add to the top-level "holes" array an entry {"ch":n,"type":"concept"|"philosopher","suggested_slug":"kebab-case","name":"display name","philosopher":"slug or ''","domain":"domain slug or best guess","what":"one sentence: what it is","why":"one sentence: why chapter N needs it"}. Only real gaps count — an imperfect-but-adequate existing slug is not a hole.

OUTPUT: Write ONE valid JSON file (UTF-8) to B:\ai_philosophy\sratchpad\popcult_index\notes\UNIT.json with shape {"book":"<book>","unit":"UNIT","chapters":[...],"holes":[...]}.

RULES: Use EXACT slugs from taxonomy.json. Do not modify any file except your output JSON. Do not read books outside your unit. English only. The notes folder already exists.
FINAL MESSAGE: exactly one line: "OK UNIT <n_chapters> <n_with_slugs> <n_holes>"
