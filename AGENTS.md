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

## Site architecture

- `index.html` (repo root) is the entire app: a single-page web app. GitHub Pages serves it
  under the subpath `/ai_philosophy/`, so **every URL must be relative** — no leading `/`.
- `content.json` (repo root) drives the whole UI: menu, section lists, article metadata.
  Nothing is auto-scanned; a page only exists on the site if it is registered in this file.
- Markdown is rendered client-side by `marked` + `DOMPurify` (loaded from jsDelivr CDN).
  Routing is hash-based: `#/` home, `#/section/<id>`, `#/read/<section>/<slug>`,
  `#/md/<path>` for markdown reached via in-document links.
- The SPA strips the first `H1` of rendered markdown (the title comes from `content.json`)
  and resolves relative `img src` against the markdown file's own folder.

## Content conventions

- One folder per document: `<folder>/<slug>/index.md` plus that document's images in the same
  folder (cover image named `cover.png`). Images are committed to the repo, never hotlinked.
- First line of each markdown file is the document `# Title`.
- To publish something: create the folder + markdown (promote it out of `sratchpad/` if it was
  drafted there), then add an entry to `content.json` with `slug`, `title`, `summary`, `path`,
  `cover`, `date` (ISO). Empty `items: []` sections are fine — the UI shows a placeholder.
- Sections in `content.json` map to the content folders: `articles`, `college-essays`,
  `knowledge-base`, `research`.
- Cover images are AI-generated via the glm-image API:
  `POST https://api.z.ai/api/coding/paas/v4/images/generations` with
  `{"model": "glm-image", "prompt": ..., "size": "1344x768"}`; the API key is in
  `~/.zai/auth.json` (Z.ai coding plan). Style formula that works: "Classical copperplate
  engraving scene: <motif>. … Purely pictorial artwork with absolutely no text, no letters,
  no words, no captions." (asking for a "cover" makes the model stamp misspelled titles).
  Save the result as `cover.png` in the document folder and download the returned URL
  immediately — it expires quickly.

## Verifying changes

- `fetch()` does not work from `file://`. Serve locally and open the printed URL:
  `python -m http.server 8000` → http://localhost:8000/
- Check: home renders all sections from `content.json`, every registered entry opens and
  renders, images resolve (no broken thumbnails or covers), and `content.json` is still valid JSON.
- Markdown export artifacts (e.g. `citeturn…` tokens from chat exports) must be stripped
  when promoting drafts into site folders.

## Gotchas

- Relative paths only (GitHub Pages project site = subpath hosting).
- CDN scripts need network access during local preview; if the libs fail to load the page
  will not render markdown — check the browser console.
- `.mimosa/` is security-scanner state, not site content — leave it alone and don't register it.
- `libgen_batch/` and other bulk data under `sratchpad/` are working data, not site content.
