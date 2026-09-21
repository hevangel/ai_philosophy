---
name: libgen-download
description: Batch-download books (philosophy or any subject) from a libgen mirror into a local corpus folder, driven by a JSON book list. Use when the user wants to build a reading corpus, download a bibliography from Library Genesis / libgen.li, resume or retry a stalled batch, skip books already owned locally, or start a new corpus with a fresh list. Two transports polite requests over an SSH SOCKS pool, and a camoufox in-container organic browser flow for session/JS-gated mirrors.
---

# libgen-download — batch-build a book corpus from a libgen mirror

Everything is driven by a **book list** (JSON) and writes into a **destination
folder**. State is checkpointed after every book, so any run is resumable —
just re-run the same command. Per-user personal scholarly use; keep the
politeness delays (they exist because the mirrors throttle and ban).

## Book list format

```json
[{"num": 1, "group": "Open Court", "title": "Seinfeld and Philosophy",
  "subtitle": "A Book about Everything and Nothing",
  "full_title": "Seinfeld and Philosophy: A Book about Everything and Nothing",
  "author": ""}]
```

`num` must be unique — it keys the download state and the extracted
`book_NNNN.<ext>` filenames. `title`/`subtitle` drive search and matching.
`examples/philosophy_pop_culture.books.json` is a real 310-book list from the
2026 philosophy-and-popular-culture corpus run; `examples/parse_bibliography.py`
shows how it was generated from a bibliography markdown. Files land in the
destination as `NNN - Title - Subtitle.<ext>`.

## Transport 1 — polite requests flow (fast path)

`scripts/batch_download.py`: mirror search → best record (scores epub > pdf,
English, size) → `ads.php` keyed link → `get.php` download, in-memory with a
60 MB cap and magic-byte validation. One worker thread per SSH SOCKS5 tunnel
(`scripts/proxy_pool.py`, `ssh -D`), so the local IP sends the mirror zero
requests.

```bash
py -3 scripts/batch_download.py --books books.json --dest ./corpus \
    --ssh-hosts oc1.example.com,oc2.example.com   # or --direct for local IP
# resume / retry / scope:
py -3 scripts/batch_download.py --books books.json --dest ./corpus --retry-failed
py -3 scripts/batch_download.py --books books.json --dest ./corpus --only 1,2,7
```

- State: `batch_state.json` next to `--books` (override `--state`); log next to it.
- `--skip-report match_report.json` skips nums already satisfied by
  `local_match.py` (see below).
- Throttle handling: exponential per-worker cooldown (10 min → 1 h cap) after a
  retry signature; a book goes back on the queue for another IP until
  `--max-attempts` (default 4). `--abort-on-retry` exits immediately for
  external IP-rotation drivers.
- Requires `requests` + `pysocks` (for socks5h). Mirror is `https://libgen.li`
  by default (`--mirror` to change); https-only, public hosts only — localhost/
  private/reserved mirrors are rejected.

## Transport 2 — camoufox in-container browser flow (when requests get gated)

If the requests flow stalls on throttle walls (the 2026 run hit a session/JS
gate that plain requests could not pass), switch to the organic browser flow:
real anti-detect Firefox clicking the human path (homepage → type query →
results → edition page → mirror → GET). Runs **inside** a docker container
(image `kb-camoufox:latest`, container `kb_camoufox`, Playwright WS
`ws://localhost:9222/hkej` inside, noVNC on host port 7900).

`scripts/chunk_loop.py` orchestrates it in polite chunks: compute pending →
pipe `scripts/camoufox_flow.py` into the container (`docker exec -i … python -`,
no shell) → copy `book_NNNN.epub` out → rename to final names → merge flow
state into the batch state → sleep 4–7 h between chunks.

```bash
py -3 scripts/chunk_loop.py --books books.json --dest ./corpus \
    --container kb_camoufox --chunk 25 --hours 24 --skip-report match_report.json
```

It self-heals container restarts (re-uploads `books.json` to `/tmp/libgen`,
which wipes on restart) and only deletes container files it successfully
extracted, so nothing is lost on a crash. Default hunts epub only; pass
`--ext pdf` (forwarded to the flow) for another type.

## Skip books you already own

`scripts/local_match.py` fuzzy-matches the list against a local library index
(one path per line, e.g. `find /e/ebook -iname '*.epub' > index.txt`), copies
matches into the destination under final numbered names, and writes the
`match_report.json` that `--skip-report` consumes:

```bash
py -3 scripts/local_match.py --books books.json --index library_index.txt --dest ./corpus
```

## Gotchas (paid for in the 2026 run)

- The mirror gate is **session/JS-based**: if ads.php stops returning keyed
  links to requests, don't tune the requests flow — go straight to transport 2.
- 43/310 pop-culture books had **no usable epub** on the mirror (a couple were
  PDF-mislabeled-as-epub); `no_result` is a final verdict, not a retry signal.
- Never shell out to `bash` from Python for docker here: on Windows that
  resolves to WSL's `System32\bash.exe`, which drops positional args. Pipe
  scripts via stdin and `cat` files out instead (chunk_loop does this).
- IP rotation via a gluetun VPN loop was prototyped in the 2026 run but NOT
  needed; its configs are credentials and stay out of git (archive only).
- Container restarts wipe `/tmp` — chunk_loop re-uploads `books.json`
  automatically, but if you run `camoufox_flow.py` by hand, check it's there.
- Markdown/corpus analysis of a downloaded corpus (epub → per-chapter
  markdown, cross-book maps) is project-specific and not part of this skill.
  The 2026 pop-culture run's analysis scripts were deleted with the
  `sratchpad/libgen_batch/` archive — recoverable from pre-2026-09-20 git
  history if a similar pipeline is ever needed.
