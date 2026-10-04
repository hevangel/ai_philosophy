# Textbook knowledge-base — build state

Second knowledge-base, mirroring the popcult-index pipeline: the owner's
philosophy textbooks (42 books — 18 initial list 2026-10-03 + 24 added same
evening; The Problems of Philosophy and Human Knowledge appeared on both
lists and are single books 6 and 7), downloaded from libgen, extracted to
per-chapter markdown, then (later) indexed.

Owner instruction (2026-10-03): step 1 = download books → data folder →
extract markdown. Index/explorer design comes later, popcult-style.

## Layout

- Corpus: `data\philosophy_textbooks\{epub,markdown,pdf}` (data submodule,
  gogs `data/philosophy` — commit only with owner go-ahead).
- Pipeline: this folder (`sratchpad\textbook_index\`).
  - `books.json` — the 18-book list (nums = book numbers).
  - `books_pdf.json` — subset that had no epub on the mirror.
  - `batch_state.json` / `batch_state_pdf.json` — chunk_loop states.
  - `epub_lib.py` — popcult epub_lib + CJK word counting + malformed-OPF
    (mlns-typo) namespace fallback.
  - `extract_epub.py` — popcult extractor, ROOT = data\philosophy_textbooks.
  - `verify_extraction.py` — popcult verifier (WORD_RE includes CJK).
  - PDF extraction: follow `extract_new_pdfs.py` (git, popcult_index) —
    PyMuPDF + hand-verified page boundaries. Not yet written here.

## Downloads (chunk_loop, container kb_camoufox, mirror libgen.li)

Started 2026-10-03 22:14. Cadence: ~4.7 h sleep between chunks (politeness).

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
| 15 | Aesthetics (Townsend) | epub no_result; pdf download timeout → pdf retry |
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
   ~03:35 retries 1,3,5,6,10,13,16. Container /tmp/libgen/books.json was
   cleared 23:20 so it re-uploads the full list.
2. Final pdf pass for still-missing {7,12,14,15} after the epub loop exits
   (fresh state file — batch_state_pdf.json is polluted with epub statuses).
3. Extract markdown for new epubs (rerun extract_epub.py) and for PDFs
   (write extract_pdfs.py, PyMuPDF, hand-verify boundaries per book).
4. verify_extraction.py must pass; then owner decides the index design.
5. 002's filename-safe download name and any renames: check final names
   match books.json titles (002 downloaded as "002 - .epub" internally but
   chunk_loop renamed to 002 - 李天命的思考藝術.epub).
