# AGENTS.md

Instructions for AI coding agents working in this repository.

## What this repo is

An AI-agent-maintained static philosophy website, published on GitHub Pages at
https://hevangel.github.io/ai_philosophy/ (repo: `hevangel/ai_philosophy`, branch `main`).
There is no build step and no package manager — the site is plain files pushed to GitHub.

Content lives in four kinds of folders:

- `articles/` — published philosophy essays, written in dialogue with AI. One folder per article.
- `college-essays/` — the owner's undergraduate philosophy course papers (2006–2011), converted
  from old Word files and published as written. Stripped of header junk: course labels, student
  IDs, and names are removed during conversion; never re-add them.
- `knowledge-base/` — llm-wiki style markdown library of philosophy notes (grows over time).
- `research/` — projects where AI reads and organizes source material into markdown.
- `sratchpad/` — scratch space (note the spelling). Working files, drafts, downloads, scripts.
  **Never displayed by the site; never reference it from `content.json` or move site content into it.**
- `publish/` — journal/preprint submission pipeline for the owner's AI-co-authored writing.
  Venue AI-policy database (`publish/venues.json`, keeps BOTH the AI-banned and AI-allowed
  lists with dated policy histories), plus one sub-folder per article with `state.json`,
  `submissions.json`, polished manuscripts, and per-venue artifacts. **Not site content —
  never register it in `content.json`.** Schemas and workflow: `publish/README.md`.

## Submission pipeline skills

`.agents/skills/` holds four project skills for external academic submission:

- `phil-venues` — research/update `publish/venues.json` (EN + CN venue AI policies).
- `phil-polish` — proofread/upgrade an article to journal standard → `publish/<slug>/polished-*.md`.
- `phil-format` — convert markdown to each venue's format (DOCX/PDF/LaTeX), with blinding,
  cover letter, and AI disclosure. Bundled script: `scripts/md_to_docx.py` (pandoc via
  `pypandoc-binary`; PDF export uses desktop Word via pywin32; installed with
  `py -3 -m pip install --user python-docx pypandoc-binary pywin32`).
- `phil-submit` — drive venue portals via `browser-use:control-browser`, logging to
  `submissions.json`. Always re-verify the venue's live AI policy first; never submit to
  `ai-banned` venues.
- `zh-translate` — the site's authoritative Chinese-translation prompt: Hong Kong Traditional
  Chinese written the way Hong Kong philosophers write in Chinese (HK character forms 裏 着 羣
  啓 衞, HK vocabulary, the HK–Taiwan academic philosophy lexicon, HK name transliterations with
  the 間隔號 ·). Every `chinese_index.md`, `title_zh`, `summary_zh`, and `cover_zh_text` follows
  it; invoke as `/zh-translate <document>`.

`.agents/skills/` also holds the owner's philosophy research toolkit (not part of the
submission pipeline). Nine modes invoked by slash name and combinable (`/map + /socratic`):
`faithful-rewrite` is `/rewrite`; the others are `reconstruct`, `socratic`, `attack`, `map`,
`research`, `ledger`, `originality`, `paper`. For a new idea the default sequence is
/socratic → /map → /attack → /research → /rewrite → /reconstruct → /ledger → /originality →
/paper, using only the modes the problem needs — never automatically write an essay. Every
mode obeys one central rule: **never make an argument stronger, cleaner, or more settled than
it really is.**

- `faithful-rewrite` (/rewrite) — remove linguistic difficulty, never intellectual difficulty;
  preserve the author's complete structure; progressive reveal with the "deeper" / "original" /
  "challenge" / "scholar mode" / "plain mode" controls.
- `reconstruct` (/reconstruct) — prose → numbered P1/P2/Therefore-C form; textual vs charitable
  reconstruction (never silently substituted); ends with "what must be true for this to work".
- `socratic` (/socratic) — question the owner's developing position one small batch at a time;
  don't rescue it; "help" offers possible responses, "assessment" exits and evaluates.
- `attack` (/attack) — strongest-version objections across nine failure types, ranked
  fatal / revision / cost / puzzle; strongest objection first, then evaluate the response.
- `map` (/map) — map plausible meanings, easily-collapsed distinctions, and surrounding
  territory before choosing a definition; ends with "the fork in the road".
- `research` (/research) — translate the question into research language, build a 3–7-work
  reading path, teach paper-reading practice; never manufacture literature consensus.
- `ledger` (/ledger) — running claim ledger (thesis, definitions, accepted/rejected claims,
  dependencies, open objections, revisions, confidence); cross-session ledgers live under
  `sratchpad/`.
- `originality` (/originality) — component-by-component neighbor check; classify as independent
  rediscovery / novel application / novel synthesis / potentially original argument.
- `paper` (/paper) — structure and write the essay only after substantial thinking; preserve
  conditionals and unresolved objections. Publishing the result is the site workflow, not this
  toolkit.

`.agents/skills/` also holds utility skills outside both toolkits:

- `libgen-download` — batch-download books from a libgen mirror into a local corpus folder,
  driven by a JSON book list. Two transports: a polite requests flow over an SSH SOCKS5 pool
  (`scripts/batch_download.py` + `proxy_pool.py`), and a camoufox in-container organic browser
  flow for session/JS-gated mirrors (`scripts/chunk_loop.py` + `camoufox_flow.py`, container
  `kb_camoufox`). Resumable per-book state; `scripts/local_match.py` skips books already on
  disk. The 310-book philosophy-and-pop-culture list ships as the skill's example
  (`examples/`). The completed 2026 corpus run's archive was deleted from `sratchpad/` at the
  owner's request (2026-09-20); its states, logs, and analysis scripts remain recoverable from
  git history if ever needed.

## Site architecture

- `index.html` (repo root) is the entire app: a single-page web app. GitHub Pages serves it
  under the subpath `/ai_philosophy/`, so **every URL must be relative** — no leading `/`.
- `content.json` (repo root) drives the whole UI: menu, section lists, article metadata.
  Nothing is auto-scanned; a page only exists on the site if it is registered in this file.
- Markdown is rendered client-side by `marked` + `DOMPurify` (loaded from jsDelivr CDN).
- Routing uses the History API with clean paths: `/ai_philosophy/` home,
  `/ai_philosophy/section/<id>`, `/ai_philosophy/read/<section>/<slug>`, `/ai_philosophy/md/<path>`
  for markdown reached via in-document links. The app derives its base path from
  `location.pathname` (`APP_BASE` — `/ai_philosophy/` on both live hosts, `/` for a local server
  rooted at the repo) and prefixes every app-relative resource/link with it. A document-level
  click interceptor routes in-app links via `pushState`; `popstate` re-routes; legacy `#/…` URLs
  are upgraded to clean paths in place (never re-introduce hash-only links). Deep links rely on
  server fallback: Apache `RewriteRule . index.html [L]` in the tracked `.htaccess` (committed to
  the repo; GitHub Pages ignores it, and it governs the horace.org mirror — pull keeps the server
  copy in sync, so never hand-edit it there), and the
  repo's `404.html` shim on GitHub Pages (which has no fallback) — keep `404.html` in sync if the
  base path ever changes.
- The SPA strips the first `H1` of rendered markdown (the title comes from `content.json`)
  and resolves relative `img src` against the markdown file's own folder.
- Google Analytics 4 (`G-QQXX5SHEHH`) is wired into `index.html`: the gtag config sets
  `send_page_view: false` and the router's `setTitle()` sends `page_view` manually (via
  `trackPageView`) so every hash-route change counts, with the final document title and full
  hash URL. Don't bypass `setTitle()` in route code, or pages stop being tracked. Both hosts
  (GitHub Pages and the horace.org mirror) report into the same GA4 property.
- The SPA is bilingual (English / Hong Kong Traditional Chinese) and themeable (light / dark).
  The top bar has an `EN / 中` language switch and a 🌙/☀️ theme button. Both persist in
  `localStorage` (`aiphil-lang`, `aiphil-theme`; theme falls back to the OS preference), and an
  inline `<head>` script applies both before first paint to avoid a flash. Toggling re-renders
  the current route in place — each document has one hash URL for both languages.
- Language resolution falls back gracefully at every step: display fields use the `<field>_zh`
  value when present and fall back to English (`title_zh`, `summary_zh` per item; `name_zh`,
  `description_zh` per section; `site.title_zh`, `site.tagline_zh`); Chinese text loads the
  `chinese_`-prefixed sibling of the registered `path` (`articles/x/index.md` →
  `articles/x/chinese_index.md`), falling back to the English file if missing; covers prefer
  `chinese_cover.png`, else the English cover renders with a translated-text overlay built from
  the item's `cover_zh_text` array (first line = title; compact title-only overlay on cards).
  Dates render in `zh-HK` locale and `<html lang>` becomes `zh-HK` in Chinese mode.

## Content conventions

- One folder per document: `<folder>/<slug>/index.md` plus that document's images in the same
  folder (cover image named `cover.png`). Images are committed to the repo, never hotlinked.
- First line of each markdown file is the document `# Title`.
- To publish something: create the folder + markdown (promote it out of `sratchpad/` if it was
  drafted there), then add an entry to `content.json` with `slug`, `title`, `summary`, `path`,
  `cover`, `date` (ISO), plus the Chinese fields (`title_zh`, `summary_zh`; sections carry
  `name_zh` / `description_zh`, `site` carries `title_zh` / `tagline_zh`). The UI falls back to
  the English value when a `_zh` field is absent, so a missing translation never breaks the site.
  Empty `items: []` sections are fine — the UI shows a placeholder.
- Sections in `content.json` map to the content folders: `articles`, `college-essays`,
  `knowledge-base`, `research`.
- Chinese translations live in the same document folder with a `chinese_` prefix on the
  filename: `<folder>/<slug>/chinese_index.md`, first line `# 中文標題`. Translate into Hong
  Kong Traditional Chinese — a **complete, paragraph-faithful translation** (never a digest) at
  a final-year philosophy-student register, using the wordings and phrases of Hong Kong
  philosophers writing in Chinese: HK character forms (裏 着 羣 啓 衞 恆), HK general vocabulary
  (機械人 軟件 網絡 質素 身分 透過), the HK–Taiwan academic philosophy lexicon (知識論 存有論
  後設倫理學 對確 證成), HK name transliterations separated by the 間隔號 ·（U+00B7, never ・）.
  The full, authoritative prompt is `.agents/skills/zh-translate/SKILL.md` — follow it for every
  translation, retranslation, and review, including titles and summaries (`title_zh`,
  `summary_zh`, `cover_zh_text`).
- Chinese cover images: `chinese_cover.png` in the same folder — the same scene as the English
  cover with the human-readable words translated into Chinese (background words may stay
  English). If image generation is unavailable, do NOT create placeholder files: list the
  translated words in the item's `cover_zh_text` (array of lines) and let the SPA overlay
  them on the English cover.
- Cover images are AI-generated via the glm-image API:
  `POST https://api.z.ai/api/coding/paas/v4/images/generations` with
  `{"model": "glm-image", "prompt": ..., "size": "1344x768"}`; the API key is in
  `~/.zai/auth.json` (Z.ai coding plan). Style formula that works: "Classical copperplate
  engraving scene: <motif>. … Purely pictorial artwork with absolutely no text, no letters,
  no words, no captions." (asking for a "cover" makes the model stamp misspelled titles).
  Save the result as `cover.png` in the document folder and download the returned URL
  immediately — it expires quickly.

## Verifying changes

- `fetch()` does not work from `file://`. Serve locally with `py -3 -m http.server <port>` from a
  **free port** (8123/8125 have been held by other sessions' servers — check with
  `netstat -ano | grep :<port>`; port 8000 is in a Windows reserved range and always fails with
  `WinError 10013`). Serving the repo root is fine for browsing and hash-form URLs; hard-loading a
  clean deep URL locally 404s because `http.server` has no SPA fallback — test deep links on
  horace.org, or serve the parent folder (`cd B:\ && py -3 -m http.server <port>` →
  http://localhost:<port>/ai_philosophy/) for production-identical base paths.
- Check: home renders all sections from `content.json`, every registered entry opens and
  renders, images resolve (no broken thumbnails or covers), and `content.json` is still valid JSON.
- Check both languages and both themes: toggle `EN / 中` and 🌙/☀️ on the home page, one
  article, and one essay. Chinese mode must show `chinese_index.md` content, `zh-HK` dates,
  and either `chinese_cover.png` or the English cover with the `cover_zh_text` overlay;
  missing Chinese text or covers must fall back to English silently.
- Markdown export artifacts (e.g. `citeturn…` tokens from chat exports) must be stripped
  when promoting drafts into site folders.

## Gotchas

- Relative paths only (GitHub Pages project site = subpath hosting).
- CDN scripts need network access during local preview; if the libs fail to load the page
  will not render markdown — check the browser console.
- Port 8000 sits in a Windows reserved-port range on this machine (`py -3 -m http.server 8000`
  fails with `WinError 10013`) — use another port, e.g. 8123. Local preview servers are
  ephemeral: the live site is GitHub Pages, which needs no local server.
- The z.ai API key in `~/.zai/auth.json` currently has NO image-generation balance: glm-image
  returns error 1113 (`Insufficient balance or no resource package`), and other model names
  (`z-image`, `cogview-4`) do not exist on that endpoint (error 1211). Until the key is topped
  up, Chinese covers use the `cover_zh_text` overlay fallback; once generation works, drop
  `chinese_cover.png` into the document folder and the site prefers it automatically.
- `.mimosa/` is security-scanner state, not site content — leave it alone and don't register it.
- The `sratchpad/libgen_batch/` run archive (states, logs, analysis scripts, gluetun VPN
  configs) was deleted from disk 2026-09-20 — recoverable from git history, except
  `gluetun_configs/` which was never committed (credentials). Bulk data under `sratchpad/` is
  working data, not site content.
