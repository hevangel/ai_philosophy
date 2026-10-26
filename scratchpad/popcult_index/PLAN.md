# PLAN: Philosophy–Pop Culture Reverse Index (resume protocol)

Goal: a concept-first reverse index of the local pop-philosophy corpus
(`B:\ai_philosophy\data\philosophy_pop_culture\epub`, 267 books). Every chapter is
read in full by a reading agent; each chapter gets the philosophers/concepts it
actually uses plus a 2–4 sentence faithful note on what it argues. Chapters
that fit no index entry are logged as "holes"; the index grows to absorb them.
Final deliverable: knowledge-base docs on the site + by-book companion.

## State (update this section as work proceeds)

- **2026-10-21d TIER-C FILL-IN PASS (Z.ai web search + browser JS rendering).**
  Owner asked to search the web for the three C-tier courses' schedules.
  Result: **no public session listing exists for any of the two Harvard C
  courses** — Gen Ed 1025 Happiness's official SimpleSyllabus (PHIL E-155
  companion, Fall 2025 + Spring 2026, rendered in-browser) says "Full syllabus
  displayed to registered students only" (verified structure: 22
  reading-quiz-covered lecture topics, 2/week Tue/Thu, midterm+final — now in
  the course record's remarks); PHIL 16 Sex, Love, and Friendship has no
  schedule anywhere public (catalogue PDF redirects, dept + instructor sites
  title-only). A pre-2020 Scribd "PHIL 20 Happiness" syllabus exists but is
  gated AND is a different earlier course — not used. mit-sci-fi-freedom was
  already fully indexed from OCW; enriched its remarks with the three required
  texts + Instructor Insights' "26 sessions" fact. Both empty lecture files'
  source_notes now document the full search trail. Lesson: SimpleSyllabus is
  JS-gated — render it in a browser, not with plain fetchers.

- **2026-10-21c PER-LECTURE COURSE INDEX (data.json v3, 286 lectures).**
  Owner asked for syllabus-faithful per-lecture coverage: what each lecture
  teaches + its philosopher/concept links. `LECTURE_PROMPT.txt` defines the
  reading-agent job (official public listings only, honest summaries, taxonomy
  slugs only, "other" kind for non-teaching sessions); 18 agents (4 waves)
  wrote `course_lectures/<cid>.json` — 286 lectures / 284 concept bindings /
  137 philosopher bindings; 16 courses indexed (Yale OYC + Harvard Justice +
  Oxford Podcasts = full official descriptions; MIT OCW = calendar/readings
  grounding; berkeley-mind = unofficial YouTube titles only, zero links on
  purpose; harvard-happiness + harvard-sex-love = honest EMPTY — no public
  session listing exists). `check_lectures.py` validates; `build_explorer.py`
  loads lectures, derives course-level bindings as the lecture union,
  emits `concepts[slug].courses` / `philosophers[slug].courses` as
  `[cid, lecture_n]` pairs (119 concepts / 47 philosophers reached), and
  validates ref symmetry. Explorer renders chapter-style lecture lists with
  `#lecture-N` anchors on course pages and grouped "Lecture N: title" entries
  on concept/philosopher pages. NOTE: courses.json's hand-added course-level
  `concepts`/`philosophers` arrays are now IGNORED by the builder (unions are
  derived from lectures — e.g. yale-death lost epicurus/locke because the
  official lecture pages never name them); they remain only as load-time
  taxonomy validation input. NOT committed (owner go-ahead pending).

- **2026-10-21b COURSES CROSS-LINKED TO CONCEPTS/PHILOSOPHERS (data.json v3).**
  `courses.json` records now carry `concepts` + `philosophers` slug arrays
  (bound to existing taxonomy slugs only, assigned conservatively from what
  each course demonstrably teaches — 46 concepts / 31 philosophers reached;
  yale-wellbeing, oxford-reasoning, the three Irving Singer MIT courses and
  stanford-moral-agent/harvard-sex-love have no philosopher links on purpose).
  `build_explorer.py` validates the slugs, emits the reverse `courses` arrays
  on concepts/philosophers, checks ref symmetry in `validate()`, and gained a
  `--data-only` flag (reuse existing covers from the live data.json instead of
  re-encoding 263 EPUB covers — verified zero cover churn). Explorer renders
  "Concepts explored" / "Philosophers" chip sections on course pages and
  "Courses that teach this …" on concept/philosopher pages.

- **2026-10-21 UNIVERSITY COURSES ADDED TO THE EXPLORER (data.json v2).**
  Owner supplied `scratchpad/Philosophy_University_Courses.json` (18 courses,
  7 universities, tiers A/B/C = full free video / partial material / readings
  only) + a standalone example HTML in scratchpad. Raw copy lives here as
  `courses.json`; `build_explorer.py` now reads it (`load_courses()`,
  flat link fields → `links` object, tier/dupe/empty-links validation) and
  emits the top-level `courses` section + `stats.courses` (output verified
  against the live data.json — rebuilds keep courses). The explorer
  (`explorer.js|css`) gained the Courses tab (`popcult/course/<id>` routes,
  university+tier filters replacing the tradition select on that tab, tier
  badges, external-link buttons, access notes) and `index.md` coverage was
  recomputed from data (271 books / 10123 chapters / 485 C / 264 P / 18
  courses). NOT yet committed (owner go-ahead pending, as always).

- **2026-10-04 CORPUS-WIDE EXTRACTION AUDIT + REPAIRS.** All 273 books'
  markdown audited against their epubs (word-ratio, spine-count, blob-syndrome,
  oversize-chapter flags; `scratchpad/audit_md/`). Ratios healthy everywhere —
  no lost text anywhere. Repairs:
  - Re-downloaded clean granular epubs: **050 Facebook** (38-doc spine),
    **208 X-Men** (31-doc), **251 Punk Rock** (50-doc — the OLD 251 file was
    the WRONG BOOK, Kristiansen's "Screaming for Change", not Open Court's
    "Punk Rock and Philosophy: Research and Destroy"; correct Heter/Greene
    edition found via Files-tab author matching).
  - **224 Joss Whedon** + **243 Nolan** (no cleaner mirror edition): blob
    markdown split at h1 headings whose section ends with "Notes"
    (`scratchpad/audit_md/split_blobs.py`, 9+16 essays recovered, words
    conserved).
  - REMOVED from corpus: **025 Beatles** — the file was Grant Maxwell's
    "How Does It Feel?" (wrong book; real Open Court Beatles book absent from
    mirror), **242** — byte-identical duplicate of 224 (same book, two
    bibliography titles). 271 books remain. Old epubs backed up in
    `scratchpad/audit_md/bad_epubs/`.
  - LEFT COARSE (no reliable boundaries; blob notes are factually fine):
    301 Comics as Philosophy (3 part-blobs), 284 College Sex (4 blobs).
    False-positive flags (genuine long chapters): 222, 236, 241, 308.
  - 9 units re-read (u081/u082/u297/u325/u326/u358/u359/u363/u450), 0 bad;
    52 holes → 51 accepted (13 philosophers + 38 concepts; taxonomy now
    **264 P / 485 C**), intros in `intros/manual_audit.json`, coverage
    485/485 + 264/264. data.json rebuilt: **271 books / 10,123 chapters, all
    read**. Submodule synced + pushed (gogs 133d43a — again carried
    concurrent philosophy_textbooks files). Parent repo UNCOMMITTED
    (data.json, covers, data gitlink) awaiting owner go-ahead.

- **2026-10-04 BOOK 002 RE-DOWNLOAD + RE-EXTRACTION.** The libgen epub for 002
  was a calibre conversion whose spine held 7 whole-part blobs (labels shifted
  one part vs contents) — the "cut short chapters" report. Re-downloaded the
  1.58 MB publisher epub (md5 04c0c464…, edition.php?id=148402452) via a
  one-off editions-scan flow (`B:\ai_philosophy\scratchpad\libgen_002_redownload\`,
  old epub kept there as `old_calibre_002.epub`). Re-extracted 38 spine docs
  with proper per-chapter titles (one-off `extract_002.py`; monkey-patched
  `load_toc_titles` to keep the FIRST ncx label per basename — this epub's
  sub-section navPoints share the chapter file's basename). Rebuilt
  full_manifest 002 entry + units u439/u440 (`rebuild_units_002.py`), re-read
  both units clean (0 bad), 2 genuine holes → taxonomy extended by
  `allusion` + `hypocrisy` (now 251 P / 447 C, extend-only), hole chapters
  bound, intros added (`intros/manual_002ext.json`), intros 447/447 + 251/251.
  data.json rebuilt: 273 books / 10,029 chapters, all read. Stale
  `sratchpad\` path constants fixed in UNIT_PROMPT.txt, check_notes.py,
  merge_notes.py, build_taxonomy.py, merge_intros.py, build_explorer.py.

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
  document for another AI agent — now maintained as the `popcult-index` skill
  (`.agents/skills/popcult-index/SKILL.md`); the former HANDOFF.md was
  converted into it and deleted.
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
