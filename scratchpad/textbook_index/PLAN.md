# Textbook knowledge-base — build state

**2026-10-04: corpus renamed `data\philosophy_textbooks` → `data\philosophy_readings`**
(owner instruction; the library now holds books AND YouTube transcripts).

## YouTube transcripts (Carneades.org)

Owner instruction 2026-10-04: add all transcripts from
https://www.youtube.com/@CarneadesOfCyrene to this library.

- Channel listing: `carneades_videos.txt` (1151 videos, `id|title`), URL list
  `carneades_urls.txt` (the flat id-title list is NOT valid for `yt-dlp -a`).
- **COMPLETE 2026-10-04 night: 817 md files in youtube\ — 801 transcripts +
  16 no-caption stubs; the other 334 videos are permanently unavailable
  (deleted/unlisted; recorded in yt_archive.txt as final verdicts).**
  Pass 1 hit YouTube's hourly rate limit at ~727 videos; resumed via a
  synthesized archive (`yt_archive.txt` = converted ids + unavailable ids),
  then a 32-video targeted retry. `yt_archive.txt` now marks every video,
  so re-running the yt-dlp command is a no-op.
- Download: `py -3 -m yt_dlp -a carneades_urls.txt --skip-download
  --write-auto-subs --write-subs --sub-langs en --sub-format vtt
  -o "...\youtube\%(id)s" --download-archive yt_archive.txt --sleep-requests 1
  --sleep-interval 2 --max-sleep-interval 6 --ignore-errors` — resumable via
  the archive file; ~3% of videos have no English captions.
- Convert: `vtt_to_md.py` → `data\philosophy_readings\youtube\<id> - <title>.md`
  (header = title + watch URL + "auto-generated captions"; rolling-cue dedupe;
  empty-caption videos become one-line stubs; VTT deleted after conversion).
- Copyright note: transcripts are YouTube auto-captions of a publicly
  published educational channel; private research corpus, never site content.

Second knowledge-base, mirroring the popcult-index pipeline: the owner's
philosophy textbooks (42 books — 18 initial list 2026-10-03 + 24 added same
evening; The Problems of Philosophy and Human Knowledge appeared on both
lists and are single books 6 and 7), downloaded from libgen, extracted to
per-chapter markdown, then (later) indexed.

Owner instruction (2026-10-03): step 1 = download books → data folder →
extract markdown. Index/explorer design comes later, popcult-style.

## Layout

- Corpus: `data\philosophy_readings\{epub,markdown,pdf}` (data submodule,
  gogs `data/philosophy` — commit only with owner go-ahead).
- Pipeline: this folder (`sratchpad\textbook_index\`).
  - `books.json` — the 18-book list (nums = book numbers).
  - `books_pdf.json` — subset that had no epub on the mirror.
  - `batch_state.json` / `batch_state_pdf.json` — chunk_loop states.
  - `epub_lib.py` — popcult epub_lib + CJK word counting + malformed-OPF
    (mlns-typo) namespace fallback.
  - `extract_epub.py` — popcult extractor, ROOT = data\philosophy_readings.
  - `verify_extraction.py` — popcult verifier (WORD_RE includes CJK).
  - PDF extraction: follow `extract_new_pdfs.py` (git, popcult_index) —
    PyMuPDF + hand-verified page boundaries. Not yet written here.

## Downloads (chunk_loop, container kb_camoufox, mirror libgen.li)

Started 2026-10-03 22:14. Cadence: ~4.7 h sleep between chunks (politeness).

**Container sharing (2026-10-04):** another session runs popcult downloads
in the same kb_camoufox container and writes /tmp/libgen/books.json — that
clobbered our chunks (KeyError crashes 03:35 + 08:53). Our loops now run
ISOLATED: workdir /tmp/libgen_tb (epub) and /tmp/libgen_tb_pdf (pdf),
dl-dirs to match, flow copies camoufox_flow_tb.py / camoufox_flow_tb_pdf.py
here. When launching chunk_loop from Git Bash, /tmp... args get MSYS-mangled
into C:\Users\...\Temp paths — always set MSYS_NO_PATHCONV=1 (bit us twice).
The other session also fetched editions_002.json (book 002 verification).

**scimag articles (owner request 2026-10-04 "try download from libgen"):**
BLOCKED. libgen.rs/.is/.st refuse connections from home IP, the container,
AND oc1.hevangel.com (SSH ok, target refused). libgen.li (the only reachable
mirror) has no journal-articles database (curtab=a is Authors, not articles).
Article stubs therefore stand; retry scimag if a live mirror appears.

The 4-book pdf retry (7,12,14,15) timed out 16:19 while running concurrently
with the epub chunk — next pdf chunk ~21:00 runs solo. Watch whether solo
chunks behave better; if not, the mirror is degraded again (wait politely).

**2026-10-14/15: junk-PDF discovery + mirror down.**
- The 6 "landed" PDFs were NOT books: first-row matching on common titles
  grabbed journal issue TOCs (006: 2p Philosophy East and West; 007: 3p
  Philosophical Quarterly; 015: 6p article; 017: 12p 1984 article; 029: 100p
  After Dinner Conversation Magazine). Only 009 was real content (Curry's
  own 19p paper "From Environmental to Ecological Ethics") but still not the
  book. ALL deleted, all six books re-queued.
- Size-based row selection A/B-failed (big-file editions sit on stale
  mirrors with dead GET links — books 6/7 stopped working); REVERTED to
  first-row. Junk is now caught by `validate_pdfs.py` (page-count +
  first-page check; <60 pages auto-article, 60-129 review) run after each
  chunk; junk gets deleted + re-queued manually.
- Driver `pdf_driver.py` (background): restart container → 120s warmup →
  one chunk (window 2.6h) → chunk_loop's 4-7h polite sleep → next cycle,
  max 8 cycles, exits when batch_state_pdf3.json has no pending_retry.
  Wait 120s after restart (18s caused a whole chunk of instant goto fails).
- 2026-10-15 00:55: libgen.li unreachable from the container even via plain
  urllib (browser too) — the mirror's global gate is down again. Driver
  keeps cycling; nothing client-side to fix.
- **2026-10-16/17: the "outage" was CONTAINER networking, not the mirror**
  (host reached libgen.li with 200 the whole time; container recovered on
  its own). AND the sequential in-container flow was still busy-spinning
  through Playwright C-level calls SIGALRM cannot interrupt. Final
  architecture: `pdf_driver2.py` — ONE book per container invocation under
  the container's own `timeout 720` (OS-enforced kill; no in-flow guard
  needed), epub-first with pdf fallback (the mirror's index changed since
  10-03: books once "no-epub" now have epubs — 006 Russell and 012
  Goodin/Pettit landed as epubs within minutes), politeness 45-90s between
  books + 10-15 min every 5. Junk caught by validate_pdfs.py after each
  harvest. Gotcha: copy_out/state must match the ext of each attempt;
  300KB pdf floor rejects the small-but-real Curry paper (#9) — accepted,
  the real book is the target; revisit at final accounting.
- Final no_results so far: 1 Sophie's World, 25 One-Minute Philosopher.

| # | Book | Status |
|---|------|--------|
| 1 | Sophie's World | epub pending_retry (retry chunk 2) |
| 2 | 李天命的思考藝術 | epub done |
| 3 | Cynical Theories | epub pending_retry |
| 4 | On Manners | epub done |
| 5 | Bullshit and Philosophy | epub pending_retry |
| 6 | The Problems of Philosophy | epub pending_retry |
| 7 | Human Knowledge (Moser/vander Nat) | epub no_result; pdf failed → pdf retry |
| 8 | Gödel, Escher, Bach | epub done |
| 9 | Ecological Ethics (Curry) | pdf done |
| 10 | Philosophy of History (Mark Day) | epub pending_retry |
| 11 | What Darwin Got Wrong | epub done |
| 12 | Contemporary Political Philosophy (Goodin/Pettit) | epub no_result; pdf timeout → pdf retry |
| 13 | Metaphysics (Richard Taylor) | epub pending_retry |
| 14 | Contemporary Political Philosophy (Kymlicka) | epub no_result; pdf no GET → pdf retry |
| 15 | Aesthetics (Townsend) | epub no_result; pdf timeout → pdf retry. NOTE: real title is *An Introduction to Aesthetics* (Blackwell 1997) — books.json search title fixed 2026-10-04; "Aesthetics: An Introduction to the Philosophy of Art" is Anne Sheppard (OUP 1987) |
| 16 | On Bullshit (Frankfurt) | epub pending_retry |
| 17 | Contemporary Moral Problems (White) | pdf done |
| 18 | Existentialism (Solomon) | epub done |
| 19 | Beyond Good and Evil (Nietzsche, Kaufmann tr.) | pending (added 2026-10-03 23:3x, downloads start chunk 2) |
| 20 | Philosophy of Religion (ed. Cahn) | pending |
| 21 | Anarchy, State, and Utopia (Nozick) | pending |
| 22 | A Good Book, In Theory (Sears) | pending |
| 23 | Writing Philosophy (Vaughn) | pending |
| 24 | On Liberty (Mill) | pending |
| 25 | The One-Minute Philosopher (Brown) | pending |
| 26 | Philosophy: 100 Great Thinkers (Harwood) | pending |
| 27 | The Evidential Argument from Evil (ed. Howard-Snyder) | pending |
| 28 | Dimensions of Moral Theory (Jacobs) | pending |
| 29 | The Story of Philosophy (Magee) | pending |
| 30 | First Philosophy Vol. II (ed. Bailey) | pending |
| 31 | Language Matters (Bauer/Holmes/Warren) | pending |
| 32 | Core Questions in Philosophy (Sober) | pending |
| 33 | Investigating Culture (Delaney) | pending |
| 34 | The Theory of Knowledge (Pojman) | pending |
| 35 | A Theory of Justice (Rawls) | pending |
| 36 | The Arrow Impossibility Theorem (Maskin/Sen) | pending |
| 37 | Social Choice and Individual Values (Arrow) | pending |
| 38 | The Prince (Machiavelli) | pending |
| 39 | Philosophy of Law 7th ed. (Feinberg/Coleman) | pending |
| 40 | The Philosophy of Language 4th ed. (ed. Martinich) | pending |
| 41 | Environmental Ethics: An Anthology (Light/Rolston) | pending |
| 42 | An Introduction to the Philosophy of Language (Morris) | pending |

Books 9 and 23 of the owner's second list were duplicates of books 6 and 7
(Problems of Philosophy; Human Knowledge) — not re-added.

## Extraction

- 5 epub books extracted 2026-10-03 22:55 → 160 chapters,
  verify_extraction.py: 0 failures (after the mlns-typo fallback fix).

## Next steps

1. Epub loop (background, exits when queue empty or 24 h): chunk 2 at
   ~03:35 retries 1,3,5,6,10,13,16 + starts the new books. Container
   /tmp/libgen/books.json was cleared 23:20 so it re-uploads the full list
   (42 books as of 23:3x).
2. Final pdf pass for still-missing books after the epub loop exits
   (fresh state file — batch_state_pdf.json is polluted with epub statuses).
3. Extract markdown for new epubs (rerun extract_epub.py) and for PDFs
   (write extract_pdfs.py, PyMuPDF, hand-verify boundaries per book).
4. verify_extraction.py must pass; then owner decides the index design.
5. TOC reconstructions (owner instruction 2026-10-04): for books that end up
   undownloadable (no epub AND no pdf), keep the online-TOC reconstruction
   from `reconstructions/` as the book's corpus entry. Done so far for
   7, 12, 14, 15 (full reading-level TOCs, sourced). Promote into
   `data\philosophy_readings\markdown\<book>\` only once the book is
   confirmed unavailable; delete the reconstruction if the real book lands.
   After the final download verdict, run another research round for any
   newly unavailable books.
6. Anthology deep reconstruction (owner instruction 2026-10-04: "some of
   the textbooks are just collections of other philosopher's paper, you can
   reconstruct those books") — DONE for the two confirmed-unavailable
   anthologies, via `fetch_readings.py` + research-agent manifests
   (`007_readings.json`, `012_readings.json`):
   - 007 Human Knowledge: corpus folder has toc.md + ch01–ch39
     (15 full openly-available texts — Plato…Kant, James, Russell, Quine's
     Two Dogmas, Gettier — from Gutenberg/New Advent/Wikisource/archive.org/
     ditext.com; 24 citation stubs for copyrighted modern papers).
   - 012 Goodin/Pettit: corpus folder has toc.md + ch01–ch48
     (2 full texts — Thomson's Defense of Abortion, Berlin's Two Concepts;
     46 citation stubs with verified landing pages + original citations).
     Skinner's British Academy PDF 404'd — retry candidate if a live copy
     surfaces.
   - fetch_readings.py enforces http/https + public-host checks, handles
     HTML and PDF (PyMuPDF), auto-writes stubs on failure. Monographs 14/15
     stay TOC-only. If 7 or 12 later download as real PDFs, delete the
     reconstructed folders.
7. 002's filename-safe download name and any renames: check final names
   match books.json titles (002 downloaded as "002 - .epub" internally but
   chunk_loop renamed to 002 - 李天命的思考藝術.epub).
