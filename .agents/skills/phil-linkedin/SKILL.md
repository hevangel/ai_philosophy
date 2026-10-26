---
name: phil-linkedin
description: Post one of the site's articles to the owner's LinkedIn feed via browser automation (browser-use), with the article cover reaching the post through an Open Graph share card. Use whenever the user asks to share, post, or promote a repo article on LinkedIn. Requires the post text to be supplied verbatim by the user — this skill NEVER drafts, summarizes, translates, or "improves" post content.
---

# phil-linkedin — post a site article to the owner's LinkedIn

Posts one article (`articles/<slug>/`) to the owner's LinkedIn feed
(account: Horace Chan, linkedin.com/in/horacechan) as a text post whose link
unfurls into a rich card carrying the article cover and title.

## Hard rules

- **The post text is 100% human-supplied. If it was not provided in the
  invocation, STOP and ask for it.** Never summarize the article, never draft,
  rewrite, fix typos, translate, or "polish" the text. Post it character-for-
  character (double spaces and grammar quirks included). The only text the
  skill may add is the article share URL (omitted if the human's text already
  contains a link or they say not to include one).
- **Load the `browser-use:control-browser` skill first and do the browser work
  yourself** — never delegate to a subagent.
- If the in-app browser is not logged in to LinkedIn, stop and hand the login
  to the user. Never touch credentials.
- One post per invocation; never bulk-post or auto-retry a failed Post click
  more than once (check the feed first — the first click often succeeded).
- The Mimosa commit hook may block a push over pre-existing findings elsewhere
  in the tree; commit only this skill's own file and report any blocked finding
  to the user instead of "fixing" unrelated code silently.

## Why the share card (read this before improvising)

The in-app browser cannot attach an image file to the composer: no file-chooser
support, clipboard write is permission-denied, and LinkedIn ignores untrusted
synthetic paste/drop events (it accepts only trusted OS input). The cover
therefore reaches the post through the link preview card (og:image). Also,
GitHub Pages has no SPA fallback: clean routes (`/read/articles/<slug>`) return
HTTP 404 to crawlers, so LinkedIn shows "Cannot display preview" for them.
Both problems are solved by a static share page per article.

## Procedure

1. **Resolve the article** — look up `slug`, `title`, `summary` in
   `content.json`; cover is `articles/<slug>/cover.png`.
2. **Ensure the share page** `articles/<slug>/index.html` exists (og:title,
   og:description from content.json, og:image = absolute
   `https://hevangel.github.io/ai_philosophy/articles/<slug>/cover.png`,
   twitter:card `summary_large_image`, and
   `<meta http-equiv="refresh" content="0; url=../../read/articles/<slug>">`
   so humans land on the article). Copy the committed
   `articles/the_bridge_was_not_built_for_machines/index.html` as the template.
   If you created it: `git add` that one file, commit, push `origin main`,
   then wait for the build — poll
   `gh api repos/hevangel/ai_philosophy/pages/builds/latest --jq .status`
   until `built` (local `curl` to github.io is network-blocked on this machine
   and returns 000 — that is a proxy block, not a missing deploy).
3. **Post URL** is always
   `https://hevangel.github.io/ai_philosophy/articles/<slug>/` — never the
   clean `/read/...` route.
4. **Compose.** Set viewport 1366x900 for the desktop layout, open
   `https://www.linkedin.com/feed/`, then:
   - "Start a post" and the modal toolbar buttons live in shadow roots: role
     and CSS locator *clicks* time out and `evaluate(() => el.click())` is a
     no-op there. Take a screenshot and use `tab.cua.click` coordinates
     (the pill sits under the For you / Network tabs).
   - The editor is `getByRole("dialog") > getByRole("textbox")`. Focus it with
     `editor.evaluate((el) => el.focus())` and type with `editor.type(...)` —
     locator typing works even though locator clicking does not. Paragraph
     breaks: two `editor.press("Enter")`.
   - Type the human text verbatim, then Enter ×2, then the share URL.
5. **Verify the card**: wait up to ~10 s; the dialog snapshot must gain a
   `figure` + the article title and lose "Cannot display preview". If the
   card fails to build, stop before posting and report — a bare link with no
   cover is not the deliverable.
6. **Post** via `tab.cua.click` on the blue Post button (bottom-right of the
   modal; find it on a fresh screenshot — it moves when the card loads).
   Proceed without pausing only because the human supplied the exact content
   in this invocation; if anything differs from the invocation (edited text,
   missing card), stop and confirm first.
7. **Verify**: dialog count 0; feed snapshot contains the text and the card;
   toast "Post successful". Capture the permalink (first
   `a[href*="/feed/update/"]` on the feed). Report permalink + the verbatim
   text you posted + card status.
