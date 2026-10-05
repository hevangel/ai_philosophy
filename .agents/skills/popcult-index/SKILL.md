---
name: popcult-index
description: Maintain and extend the Philosophy × Pop Culture reverse index (273 books / 9,999 chapters, feeding the /popcult two-pane explorer on the site). Use when adding new books to the corpus, re-running or extending the chapter reading pass, extending the philosopher/concept taxonomy from holes, regenerating knowledge-base/popcult-index/data.json, or auditing index quality.
---

# popcult-index — maintain and extend the reverse index

The corpus books work forward (pop-culture work → philosophy essays). This
index is the reverse: organized by **philosopher / concept**, each entry with
(a) a brief accurate intro, (b) references to the book chapters that apply it,
(c) a note on **how each chapter's topics relate to the concept**.

Non-negotiable, owner-set rules for every part of this skill:

- **Every chapter must actually be read.** Keyword/title matching was
  explicitly rejected as "too cheap and easy". Each real essay gets a faithful
  2–4 sentence relation note (what it argues, how it connects the pop-culture
  work to the philosophy — specific characters/episodes/arguments, not a
  generic description of the concept).
- **Honest weakness is a feature.** Never make a relation sound tighter than
  the text supports. Chapters fitting no entry are logged as **holes**; the
  taxonomy grows from the holes.

Current state (recompute from data, never trust prose numbers): build
**complete** — 273 books, 450/450 units, 9,999 chapters read, 445 concepts /
251 philosophers (443/247 in use). Live on the site as the `/popcult`
two-pane explorer, fed by `knowledge-base/popcult-index/data.json`. The deep
protocol and running State section live in `scratchpad/popcult_index/PLAN.md`
— keep its State section current as you work.

## Pipeline — `scratchpad/popcult_index/`

| File | Role |
|---|---|
| `epub_lib.py` | EPUB parsing; `safe_fromstring()` rejects `<!DOCTYPE`/`<!ENTITY` (XXE guard, 4MB cap) |
| `extract_epub.py` | Spine-faithful EPUB → markdown extractor |
| `extract_new_pdfs.py`, `extract_metallica.py` | PDF-only books → corpus-standard markdown (TOC/hand-verified boundaries) |
| `verify_extraction.py` | 1:1 markdown ↔ spine verification |
| `build_work_units.py` | Built `full_manifest.json` + work units (balanced: ≤90k words / ≤42 content chapters) |
| `reconcile_manifest.py` | Reconciles `full_manifest.json` to the work units |
| `register_new_books.py` | Registers newly added books as new units (one unit per book for small additions) |
| `build_taxonomy.py` | **Source of truth** for `taxonomy.json`; extend the P/C dicts here, re-run to rebuild |
| `taxonomy.json` | The ONLY allowed philosopher/concept slugs. Extend-only: **never rename or delete slugs** |
| `units\uNNN.json` | Work unit: `{unit, book, part, path, range, chapters:[{n,file,words}], content:[n's ≥200 words]}` |
| `notes\uNNN.json` | One reading agent's output per unit (schema below) |
| `UNIT_PROMPT.txt` | Complete reading-agent instructions (`UNIT` placeholder) |
| `check_notes.py` | Validator: JSON validity, full chapter coverage vs unit, slug validity vs taxonomy, no empty relation on real essays. `py -3 check_notes.py [--ids u169,u176]` |
| `repair_notes.py` | Deterministic repairs of flagged notes |
| `merge_notes.py` | Aggregates notes → `merged_index.json` (chapters, concept_chapters, philosopher_usage, holes, progress) |
| `gen_taxonomy_ext.py` | Final hole-driven taxonomy extension (curated accept list) |
| `gen_intro_tasks.py` | Writer-agent task batches for concept/philosopher/book intros |
| `INTRO_PROMPT.txt`, `intros\`, `merge_intros.py` | Intro generation → `intros.json` (keys validated against taxonomy) |
| `build_explorer.py` | Builds the publishable graph + normalized covers → `knowledge-base/popcult-index/data.json` (the live explorer's dataset) |
| `render_docs.py` | Legacy markdown renderer into `knowledge-base/popcult-index/` — superseded by the explorer; writes only its own files |

The corpus itself: `philosophy_pop_culture\` in the repo root (gitignored)
and mirrored in the `data` submodule (`data\philosophy_pop_culture\`, gogs
`data/philosophy`). Book 071 (*The Catcher in the Rye and Philosophy*) is an
image-only scan with no text layer — excluded from units, documented.

## Adding books (the extension workflow)

1. Get the book into `philosophy_pop_culture\` (libgen download: use the
   `libgen-download` skill; PDF-only books also need a cover extracted).
2. Extract to corpus markdown: EPUB via `extract_epub.py`, PDF via
   `extract_new_pdfs.py` as the pattern. Verify with `verify_extraction.py`.
3. Register the book and build its work unit(s) — `register_new_books.py`
   pattern: small additions get one unit per book (`u439+` numbering).
4. Run the reading pass (below) on the new units, then validate, merge, and
   check the holes it produced.
5. If holes cluster on missing philosophers/concepts: extend
   `build_taxonomy.py` (extend-only), rebuild `taxonomy.json`, bind the
   hole-proposing chapters to the new slugs in their note files (no
   re-reading needed), and generate intros for the new entries.
6. `py -3 merge_notes.py && py -3 build_explorer.py` → commit the regenerated
   `knowledge-base/popcult-index/` files **only with the owner's go-ahead**.

## The reading pass

**Dispatch.** Reading agents use the Agent tool (`general-purpose`, fresh
context each), one unit per agent, prompt as a single line:

```
Execute the instructions in B:\ai_philosophy\scratchpad\popcult_index\UNIT_PROMPT.txt exactly, with UNIT = uNNN everywhere (read units\uNNN.json, write notes\uNNN.json, replace UNIT with uNNN in the final message). A previous attempt at this unit failed due to provider rate limits — if notes\uNNN.json already exists, validate it instead of re-reading.
```

(Drop the "previous attempt" sentence for never-tried units.) Dispatch in
foreground waves — **~3–5 concurrent agents** is the user-level cap as of
2026-09-28; background launches fail instantly over it, and 12-wide waves
worked fine as successive foreground batches (24-wide burned ~40M tokens and
tripped the weekly quota). Token cost is ~1–2M per unit.

The agent reads only the chapters in the unit's `content` array (essays
≥200 words) in full, classifies the rest by word count/filename, and writes
`notes\uNNN.json`:

```json
{"book":"<book>","unit":"uNNN",
 "chapters":[{"n":1,"file":"c01.md","kind":"chapter|front|notes",
   "philosophers":["slug"],"concepts":["slug"],
   "relation":"2-4 sentences, chapters only; \"\" otherwise"}],
 "holes":[{"ch":3,"type":"concept","suggested_slug":"kebab-case",
   "name":"Display Name","philosopher":"slug or ''",
   "domain":"domain slug or guess","what":"...","why":"..."}]}
```

**Cadence.** After each wave: `py -3 check_notes.py` (expect "0 bad"); every
~3 waves: `py -3 merge_notes.py` (+ `build_explorer.py` if you want the site
dataset current).

## Failure modes and repairs

- **Provider quota errors in agent results:** `[1302]` burst limit →
  re-dispatch the unit once. `[1308]` 5-hour rolling limit → stop dispatching,
  resume after the reset time in the error. `[1310]` weekly limit → stop
  cleanly, merge what exists, update `PLAN.md`'s State section, report to the
  owner. Do not burn failed dispatches.
- **`check_notes.py` flags an unknown slug** → near-miss of an existing slug
  (e.g. `james` for `william-james`): patch the note. Genuinely missing and
  recurring in holes: extend `build_taxonomy.py` (extend-only), rebuild,
  re-check.
- **Empty `relation` on a real essay (kind `chapter`)** → read that one
  chapter in the main session and write the relation into the note (needed
  ~5 times in 450 units).
- **Note file missing after an agent claims OK** → re-run `check_notes.py`,
  re-dispatch that unit.

## Publishing and verifying (site rules)

- `build_explorer.py` writes `knowledge-base/popcult-index/data.json` (+
  covers); the `/popcult` explorer page renders it. The legacy
  `render_docs.py` domain/book docs still render but are huge (17–84MB) and
  superseded — deleting them before a future commit is the owner's call.
- Explorer pages are reached via `/md/` routes; registration lives in
  `content.json`. Nothing under `scratchpad\` is ever registered or published.
- Verify locally: serve the repo root with `py -3 -m http.server <port>` on a
  **free port** (never 8000 — Windows reserved range, `WinError 10013`;
  8123/8125 are often held — check `netstat -ano | grep :<port>`). Check the
  explorer loads, `data.json` fetches, in-doc links resolve, both languages
  and themes, and `content.json` is still valid JSON.

## Hard rules (violating these has real consequences)

1. **No `git commit` / `git push` without the owner's explicit go-ahead.**
2. `scratchpad\` is scratch space — never site content, never referenced from
   `content.json`. The corpus under `philosophy_pop_culture\` (and its
   `data\` submodule copy) is working data, not site content.
3. The repo is AI-maintained; the owner reads but never edits.
4. The Mimosa security hook blocks many tool-call shapes — scripts must not
   contain variable-built output paths, `".."` string literals, or non-literal
   `open()` calls (use `pathlib` with module-level literal path constants,
   `os.pardir`, and a `checked_path()` containment helper); XML parsing must
   reject DTDs/entities (`epub_lib.safe_fromstring`); Bash heredoc file
   creation is blocked — create files with the Write tool and literal paths.
5. Extend-only taxonomy: existing slugs are load-bearing in hundreds of note
   files.
6. `.mimosa\` is scanner state — leave it alone.
