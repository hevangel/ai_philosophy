# publish/ — Journal & Preprint Submission Pipeline

Working space for submitting the owner's AI-co-authored philosophy writing to journals and
preprint servers (English and Chinese). **This folder is NOT site content — never register it
in `content.json`, never serve it on the website.** It contains manuscripts being prepared for
external submission, not published web pages.

## The four skills

| Skill | Does |
|---|---|
| `phil-venues` | Research/update `venues.json` — the AI-banned and AI-allowed venue lists |
| `phil-polish` | Proofread & beef an article up to academic publication standard |
| `phil-format` | Convert markdown into each venue's required submission format (DOCX/PDF/LaTeX), tailored per venue |
| `phil-submit` | Drive the venue's submission portal via browser automation and log the result |

Typical flow for an article `articles/my-article/index.md`:

```
phil-venues            (optional: refresh policy data first)
phil-polish my-article         → publish/my-article/polished-en.md (+ polished-zh.md)
phil-format my-article philarchive    → publish/my-article/venue-philarchive/manuscript.pdf
phil-submit my-article philarchive    → submission logged, confirmation captured
```

## Folder layout

One sub-folder per article, named after the article slug:

```
publish/
  venues.json                    ← venue database (both AI-banned and AI-allowed lists)
  README.md                      ← this file
  <article-slug>/
    state.json                   ← current work state of polish/conversion for this article
    submissions.json             ← submission tracking log for this article
    polished-en.md               ← polished manuscript (English)
    polished-zh.md               ← polished manuscript (Chinese), if applicable
    polish-notes.md              ← what the polish pass changed & remaining doubts
    venue-<venue-id>/            ← one per venue this article is being prepared for
      manuscript.docx / manuscript.pdf / main.tex ...
      cover-letter.md
      ai-disclosure.md           ← statement matched to that venue's policy
      blinded-manuscript.docx    ← double-blind version where required
      notes.md                   ← venue-specific tailoring notes
```

## JSON schemas

### `state.json` — current work state

```json
{
  "article": "my-article",
  "source": "articles/my-article/index.md",
  "updated": "2026-09-11T00:00:00Z",
  "polish": {
    "status": "not-started | in-progress | done",
    "language": "en | zh | both",
    "runs": [
      {"date": "...", "focus": "argument structure / citations / style", "summary": "..."}
    ]
  },
  "conversions": {
    "<venue-id>": {
      "status": "pending | in-progress | done | blocked",
      "artifacts": ["venue-<venue-id>/manuscript.docx"],
      "notes": "why blocked, or what was tailored"
    }
  }
}
```

### `submissions.json` — submission tracking

```json
{
  "article": "my-article",
  "updated": "2026-09-11T00:00:00Z",
  "submissions": [
    {
      "venue": "philarchive",
      "status": "planned | submitted | under-review | revise-resubmit | accepted | published | rejected | withdrawn",
      "history": [
        {"date": "...", "event": "submitted", "method": "browser-auto | manual",
         "confirmation": "manuscript id / receipt url / screenshot path"}
      ],
      "ai_disclosure_sent": true,
      "notes": ""
    }
  ]
}
```

Update `state.json` after every polish/conversion run and `submissions.json` after every
submission action or status change (decision letters arrive by email — record them in
`history`).

## Venue database rules (`venues.json`)

- **Both lists are kept**: AI-banned venues (`ai_status: "ai-banned"`) and AI-allowed venues
  (`allowed` / `disclosure-required` / `case-by-case` / `no-stated-policy`) live in the same
  file, never delete either side. Rules flip often (e.g. *Philosophy & Public Affairs* banned
  AI-authored content in Aug 2026 after publishing an AI-authored article on purpose).
- Every entry carries `ai_policy` (summary), `ai_source` (URL), `checked` (date of last
  verification), and `policy_history` (append-only change log with dates).
- Never submit based on `venues.json` alone — re-check the venue's live policy page at
  submission time (the `phil-submit` skill does this as its first step).
- Chinese venues: see `defaults.cn_journal_default` — most CN journals converge on the ISTIC
  《学术出版中的AIGC使用边界指南》 template: no AI authorship, no AI-generated core content,
  auxiliary AI use (润色/检索/整理) only, with a 《生成式人工智能工具使用情况说明》 attached at
  submission (tool, version, prompts, records, verification). CN journals run AIGC detection
  (知网 AMLC / 维普) at initial review; some desk-reject above a threshold.

## Honesty rule

This pipeline is AI-assisted by design. Never hide that: generate the per-venue disclosure
statement from the actual usage log, never let unreviewed AI text through, and verify every
citation exists (hallucinated references are the #1 desk-reject and arXiv-ban trigger).
