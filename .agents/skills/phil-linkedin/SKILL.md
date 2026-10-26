---
name: phil-linkedin
description: Publish one of the site's articles as a long-form LinkedIn article (Pulse) on the owner's account — cover image, full text, then "share with a post" — via browser automation (browser-use). Use whenever the user asks to post, publish, or promote a repo article on LinkedIn. Requires the share-post text to be supplied verbatim by the user — this skill NEVER drafts, summarizes, translates, or "improves" post content.
---

# phil-linkedin — publish a site article as a LinkedIn article

Publishes `articles/<slug>/` to the owner's LinkedIn (account: Horace Chan,
linkedin.com/in/horacechan) as a **long-form LinkedIn article** (the "Write
article" / Pulse flow) with the article cover as the hero image and the full
markdown text as the body, then shares it with a post carrying the human's
words. Correct flow confirmed by the owner 2026-10-25 — do NOT post a bare
link to the site instead.

## Hard rules

- **The share-post text is 100% human-supplied. If it was not provided in the
  invocation, STOP and ask for it.** Never summarize the article, never draft,
  rewrite, fix typos, translate, or "polish" it. Post it character-for-
  character (double spaces and grammar quirks included). The article body
  itself, by contrast, is site content — copy it from `index.md` faithfully.
- **Load the `browser-use:control-browser` skill first and do the browser work
  yourself** — never delegate to a subagent.
- If the in-app browser is not logged in to LinkedIn, stop and hand the login
  to the user. Never touch credentials.
- One article per invocation; never bulk-publish or auto-retry a failed
  Publish click more than once (check recent activity first — the first click
  often succeeded).
- The Mimosa commit hook may block a push over pre-existing findings elsewhere
  in the tree; commit only this skill's own files and report any blocked
  finding to the user instead of "fixing" unrelated code silently.

## Input prep

1. Read `articles/<slug>/index.md`; take the title from the `# ` line and the
   rest as the body. Check the article's `title`/`summary` in `content.json`.
2. Convert the body (title stripped) markdown → HTML with
   `py -3 -m pip install --user markdown`, then
   `markdown.markdown(body, extensions=['extra'])`. The Pulse paste keeps
   `<p>/<strong>/<em>/<h2>` rich formatting; `<hr>` scene breaks may or may
   not survive — text is what must survive.

## Browser mechanics (learned 2026-10-25, all confirmed live)

- **Write article, not Start a post.** Feed → "Write article" link
  (`/article/new/`) → "Publish new article" editor with a cover area, a
  `textbox "Title"`, and a `textbox "Article editor content"`.
- **Title**: focus via `locator.evaluate((el) => el.focus())`, type via
  `locator.type(...)`. `innerText` reads back empty on this field — verify
  through `domSnapshot()` instead.
- **Cover image upload works via direct file-input injection** (the share
  composer does NOT allow this, but the article editor does):
  1. CUA-click "Upload from computer".
  2. Immediately deep-search shadow DOM for `input[type=file]` (it mounts on
     click; walk elements + `.shadowRoot` recursively).
  3. Build the File in-page: `new Image()` with `crossOrigin="anonymous"` →
     canvas → `toBlob` → `File` → `DataTransfer` → `input.files = dt.files` →
     dispatch `input` + `change` events. Source URL:
     `https://hevangel.github.io/ai_philosophy/articles/<slug>/cover.png`
     (GitHub Pages sends open CORS; LinkedIn's patched `fetch`/XHR are blocked
     by CSP, the `img` route is not).
  4. A crop/confirm dialog appears → screenshot to aim → click its "Next".
- **Body paste**: the Pulse editor ACCEPTS synthetic `ClipboardEvent("paste")`
  with `text/html` + `text/plain` (unlike the feed share composer, which only
  accepts trusted OS input). OS-clipboard routes (`execCommand("copy")`,
  `navigator.clipboard.write`) are all permission-blocked in the IAB.
  Transport the ~40 KB HTML into the page as chunked `evaluate` arguments
  stashed on `window.__chunks[i]` (order-independent), join in order, then:
  1. **First clear the editor with a REAL CUA click into the body text**,
     then CUA `Control+a` + `Backspace` (evaluate-focus alone ignores keys).
     Verify `(el.innerText).trim().length === 0` before pasting.
  2. Dispatch one paste event carrying the full HTML + plain-text twin.
  3. Verify: `innerText` length ≈ 36 k for a 5 k-word essay, head matches the
     first sentence, tail matches the last line.
- **Publish flow**: "Next →" opens the share dialog ("Tell your network what
  your article is about...", article preview attached). Focus its textbox and
  `locator.type` the human's words verbatim — this dialog accepts locator
  typing. "Publish" publishes the article AND the share post together.

## Procedure

1. Convert markdown → HTML (Input prep). Load `browser-use:control-browser`.
2. Open `https://www.linkedin.com/article/new/` (first goto may report a
   navigation timeout — check URL/title before retrying; it loads anyway).
3. Upload the cover (mechanics above), confirm with the dialog's "Next".
4. Type the title; paste the body; verify head/tail/length.
5. Type the human's share text in the "Next" dialog; screenshot the composer
   to confirm text + article preview; click "Publish".
6. Verify: the tab lands on `linkedin.com/pulse/<slug>-horace-chan-<id>/`;
   dismiss the congrats dialog; confirm the share post exists under
   `linkedin.com/in/horacechan/recent-activity/all/` (feed rendering lags) and
   capture its permalink (`a[href*="/feed/update/"]` inside the matching post
   container). Report both URLs.
- The OG share pages (`articles/<slug>/index.html`, template:
  `the_bridge_was_not_built_for_machines`) are NOT needed for this flow —
  the Pulse article carries its own cover. They remain useful only if the
  human explicitly wants to share the *site* link on social platforms.
