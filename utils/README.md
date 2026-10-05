# utils/

Working scripts and run artifacts kept outside the scratch space because they
are worth keeping organized. Nothing here is site content — never register it
in `content.json`.

## libgen-pdf-run/ — artifacts of the 2026-10 libgen PDF top-up run

The 42-book PDF-format top-up of the philosophy-and-pop-culture corpus was
driven by the reusable download machinery in
`.agents/skills/libgen-download/scripts/` (see that skill's SKILL.md). This
folder keeps the run's own files:

- `books.json` — the 42-book top-up list (libgen search metadata per book).
- `batch_state.json` / `batch_state.log` — per-book resumable state and the
  batch runner's log.
- `chunk_loop_log.txt` — log of the camoufox chunk loop (chunks, per-book
  outcomes, timings).
- `diag/` — one-off Playwright diagnostics (`diag.py` … `diag10.py`) written
  while reverse-engineering the libgen.li session/JS gate during the run:
  locating the search box, the Editions tab, edition/download links, and
  result-table columns. They are kept as reference for how the gate was
  probed, not as reusable tools — each hardcodes a probe target and runs
  against the camoufox container's Playwright endpoint
  (`ws://localhost:9222/hkej`).
- `screenshots/` — the diagnostics' page captures of the mirror's pages.
