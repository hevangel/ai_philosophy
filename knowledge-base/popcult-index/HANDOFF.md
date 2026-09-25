# Pop-Culture Philosophy Reverse Index — Build Handoff

Internal working document for the AI coding agent taking over this build.
It is **not** site content — do not register it in `content.json`. The
authoritative deep protocol is `B:\ai_philosophy\sratchpad\popcult_index\PLAN.md`
(keep its State section updated as you work). This file survives pipeline
re-renders; `render_docs.py` only overwrites the files it generates.

## 1. The mission (owner's request, verbatim intent)

Build a **master reverse index** of all books under
`B:\ai_philosophy\philosophy_pop_culture\` (267 EPUBs: Open Court "Popular
Culture and Philosophy" + Wiley-Blackwell "...and Philosophy" series). The
books work forward (pop-culture → philosophy); the owner wants the reverse:
organized by **philosopher / concept**, where each entry has (a) a brief
accurate intro of the concept, (b) references to the book chapters that apply
it, (c) a note on **how each chapter's topics relate to the concept**.

The owner explicitly rejected keyword/title matching as "too cheap and easy":
**every chapter must actually be read**, and each chapter gets a faithful
2–4 sentence relation note (what it argues, how it connects the pop-culture
work to the philosophy — specific characters/episodes/arguments, not a
generic description of the concept). Chapters that fit no existing index
entry are logged as **holes**, and the index (taxonomy) is grown from the
holes. Honest weakness is a feature: never make a relation sound tighter
than the text supports.

## 2. TL;DR — how to resume right now

1. `cd B:\ai_philosophy\sratchpad\popcult_index`
2. `py -3 check_notes.py` — validates every note on disk (last run: 170 checked, 0 bad)
3. Compute remaining units: `units\u*.json` minus `notes\u*.json`
   (as of 2026-09-22: 170/438 done; missing: u024–u032, u169, u176, u180,
   u182, u183, then u184–u437 contiguous)
4. Dispatch reading agents in **waves of 12** (see §5) until 438/438,
   validating each wave with `check_notes.py`, merging/rendering every ~3 waves
5. When all 438 are done → finalization (§7): aggregate holes → extend the
   taxonomy → bind chapters to new slugs → write concept intros → final
   merge/render → register in `content.json` (§8)

**Never commit or push anything without the owner's explicit go-ahead.**

## 3. Current state snapshot (2026-09-22)

- Extraction complete and verified: all 267 EPUBs re-extracted spine-faithfully
  to `philosophy_pop_culture\markdown\<book>\` and verified 1:1 against the
  EPUB spines (266/267 pass; book 071 *The Catcher in the Rye and Philosophy*
  is an image-only scan with no text layer — excluded, documented).
- Work units: 438 units over 266 books, 10,283 chapters. Per-book word-volume
  multiset matching verified no dropped content.
- Reading progress: **170/438 units** (≈39%), 4,473 chapters read, 2,401
  mapped, 1,055 holes logged, 318/332 concepts and 159/165 philosophers in use.
  Sources of truth: `notes\` file count and the `progress` block of
  `merged_index.json` (recompute, don't trust any prose number).
- Site docs: rendered (partial data, honest "Build in progress" hub banner) at
  `B:\ai_philosophy\knowledge-base\popcult-index\` — `index.md` hub, 15
  domain docs, `books-*.md` companion chunks. Reachable on the live site via
  the `/md/` route once registered in `content.json` (§8; not yet registered).
- Provider quota interrupted the run (see §6); waves of 12 are the sustainable
  size. A one-shot scheduled automation (id `automation-e1250479-e86d-4da3-b1c2-8ae0d50288cb`,
  fires 2026-09-23 17:00 local) will follow `PLAN.md` — if you are taking over
  the build before then, tell the owner so it can be deleted (CronDelete) and
  not double-dispatch against your work.

## 4. File map — `B:\ai_philosophy\sratchpad\popcult_index\`

| File | Role |
|---|---|
| `epub_lib.py` | EPUB parsing; `safe_fromstring()` rejects `<!DOCTYPE`/`<!ENTITY` (XXE guard, 4MB cap) |
| `extract_epub.py` | Spine-faithful EPUB → markdown extractor (already ran; do not re-run) |
| `verify_extraction.py` | 1:1 markdown ↔ spine verification (already ran; passed) |
| `build_work_units.py` | Built `full_manifest.json` + `work_units.json` → 438 balanced units (≤90k words / ≤42 content chapters each) |
| `build_taxonomy.py` | **Source of truth** for `taxonomy.json`: 15 domains, 165 philosophers, 332 concepts. Extend the P/C dicts here, then re-run to rebuild |
| `taxonomy.json` | The ONLY allowed philosopher/concept slugs. Extend-only: **never rename or delete slugs** |
| `units\uNNN.json` | Work unit: `{unit, book, part, path, range, chapters:[{n,file,words}], content:[n's ≥200 words]}` |
| `notes\uNNN.json` | One reading agent's output per unit (schema in §5) |
| `UNIT_PROMPT.txt` | The complete reading-agent instructions (`UNIT` placeholder) |
| `check_notes.py` | Validator: JSON validity, full chapter coverage vs unit, slug validity vs taxonomy, no empty relation on real essays. `py -3 check_notes.py [--ids u169,u176]` |
| `merge_notes.py` | Aggregates all notes → `merged_index.json` (chapters, concept_chapters, philosopher_usage, holes, progress) |
| `render_docs.py` | Renders the site docs into `knowledge-base\popcult-index\` (writes specific files, never wipes the folder) |
| `PLAN.md` | Deep protocol + resume steps + known rendering considerations — keep its State section current |

## 5. The reading pass

**Dispatch.** Waves of **12** parallel agents (Agent tool, `general-purpose`,
each with its own fresh context). One unit per agent, prompt is a single line:

```
Execute the instructions in B:\ai_philosophy\sratchpad\popcult_index\UNIT_PROMPT.txt exactly, with UNIT = uNNN everywhere (read units\uNNN.json, write notes\uNNN.json, replace UNIT with uNNN in the final message). A previous attempt at this unit failed due to provider rate limits — if notes\uNNN.json already exists, validate it instead of re-reading.
```

Drop the "previous attempt" sentence for never-tried units. The agent reads
only the chapters in the unit's `content` array (essays ≥200 words) in full,
classifies the rest by word count/filename, and writes `notes\uNNN.json`:

```json
{"book":"<book>","unit":"uNNN",
 "chapters":[{"n":1,"file":"c01.md","kind":"chapter|front|notes",
   "philosophers":["slug"],"concepts":["slug"],
   "relation":"2-4 sentences, chapters only; \"\" otherwise"}],
 "holes":[{"ch":3,"type":"concept","suggested_slug":"kebab-case",
   "name":"Display Name","philosopher":"slug or ''",
   "domain":"domain slug or guess","what":"...","why":"..."}]}
```

**Cadence.** After each wave: `py -3 check_notes.py` (expect "0 bad");
every ~3 waves: `py -3 merge_notes.py && py -3 render_docs.py`. Token cost is
~1–2M per unit; a 12-wide wave is the proven sustainable size (24-wide burned
~40M tokens and tripped the weekly quota).

## 6. Failure modes and repairs

- **Provider quota errors in agent results:**
  - `[1302]` burst limit → just re-dispatch the unit once; it has succeeded
    on retry every time so far.
  - `[1308]` 5-hour rolling limit → stop dispatching; resume after the reset
    time given in the error message. Do not burn failed dispatches.
  - `[1310]` weekly limit → stop cleanly, merge + render what exists, update
    `PLAN.md`'s State section, and report status to the owner.
- **`check_notes.py` flags an unknown slug** → if it's a near-miss of an
  existing slug (e.g. `james` for `william-james`), patch the note. If the
  concept/philosopher is genuinely missing and keeps coming up in holes,
  extend `build_taxonomy.py` (extend-only), rebuild `taxonomy.json`, re-check.
- **Empty `relation` on a real essay (kind `chapter`)** → read that one
  chapter yourself in the main session and write the relation into the note.
  This has been needed ~5 times in 170 units (agents occasionally skip one).
- **Note file missing after an agent claims OK** → re-run `check_notes.py`,
  re-dispatch that unit.

## 7. Finalization (when 438/438)

1. `py -3 merge_notes.py`, then aggregate `holes` from `merged_index.json`;
   cluster by `suggested_slug`; discard one-off noise, keep genuinely missing
   philosophers/concepts (past high-frequency holes already absorbed into the
   taxonomy: Bergson, Freud, Jung, Lacan, Isaiah Berlin, Gadamer).
2. Extend `build_taxonomy.py` P/C dicts with accepted holes → rebuild
   `taxonomy.json`. Never rename existing slugs.
3. **Bind hole-proposing chapters to the new slugs**: each surviving hole
   names its chapter (`ch`, `why`) — patch those notes' chapter entries to add
   the new slug. No re-reading needed.
4. Generate `intros.json`: a 2–4 sentence **accurate** intro per concept
   (writer subagents in batches; these become the entry text in the domain
   docs). Accuracy over eloquence — a wrong intro is worse than a plain one.
5. Final `merge_notes.py && render_docs.py`. If a domain doc exceeds ~1.5MB,
   split per-philosopher sub-pages in `render_docs.py` (see PLAN.md).
6. Register in `content.json` under `knowledge-base` (§8).

## 8. Publishing and verifying (site rules)

- Register the docs in `B:\ai_philosophy\content.json` (the whole UI is driven
  by it; nothing is auto-scanned): an entry per doc under the `knowledge-base`
  section — hub, 15 domains, book chunks — with `slug`, `title`, `summary`,
  `path`, `date` (ISO). Relative URLs only (GitHub Pages subpath hosting).
  This file (`HANDOFF.md`) and anything under `sratchpad\` are **never**
  registered. Chinese fields are optional; the UI falls back to English
  silently. If the owner wants zh translations, follow
  `.agents/skills/zh-translate/SKILL.md` (HK Traditional Chinese register).
- Verify locally: serve the repo root with `py -3 -m http.server <port>` on a
  **free port** (never 8000 — Windows reserved range, `WinError 10013`;
  8123/8125 are often held — check `netstat -ano | grep :<port>`). Check the
  hub renders, `/md/knowledge-base/popcult-index/...` deep links work,
  in-doc relative `.md` links resolve, images/covers fine, `content.json`
  still valid JSON, both languages and both themes.

## 9. Hard rules (violating these has real consequences)

1. **No `git commit` / `git push` without the owner's explicit go-ahead.**
2. `sratchpad\` (note the spelling) is scratch space — never site content,
   never referenced from `content.json`. The EPUB/markdown corpus under
   `philosophy_pop_culture\` is gitignored working data — never commit it.
3. The repo is AI-maintained; the owner reads but never edits.
4. The Mimosa security hook blocks many tool-call shapes — follow these
   patterns or your Writes will be rejected:
   - Scripts must not contain variable-built output paths, `".."` string
     literals, or non-literal `open()` calls. Use `pathlib` with module-level
     literal path constants, `read_text`/`write_text`, `os.pardir` instead of
     `".."`, and a `checked_path()` helper (resolve + `commonpath`
     containment) for anything user-derived.
   - XML parsing must reject DTDs/entities (use `epub_lib.safe_fromstring`).
   - Bash heredoc file creation is blocked — create files with the Write tool
     and literal paths.
5. Extend-only taxonomy: existing slugs are load-bearing in 170+ note files.
6. `.mimosa\` is scanner state — leave it alone.
