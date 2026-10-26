---
name: phil-aipc
description: Prepare and submit essays to the AI Philosophy Competition (AIPC 2026, zacharygoodsell.com, deadline 2026-10-31) — eligibility screening against the AI-involvement rules, anonymization, methodology report assembly, and submission via OpenReview or the Google Forms backup. Use whenever the user mentions the Goodsell/Thornley AI philosophy competition, AIPC, or submitting an essay judged as AI-generated philosophy.
---

# phil-aipc — AI Philosophy Competition (AIPC 2026) submissions

Competition: https://www.zacharygoodsell.com/ai-philosophy-competition — organised by
Zachary Goodsell & Elliott Thornley, funded by Forethought Research. Essays must be
**primarily AI generated**; judged blind by academic philosophers on philosophical quality.

## Hard rules

- **Eligibility gate before any other work.** The AI must originate and develop ALL
  substantive philosophical ideas. If the argument came from the human, the essay is
  ineligible — do not dress it up, flag it and stop. See the audit below.
- **Never submit human-written text as part of an essay.** The rules treat "human writing"
  in the essay as disqualifying. Agent-authored cover/admin text is fine; essay text is not.
- **No prompt injection anywhere in the submission.** Any text attempting to influence the
  AI screening (e.g. "rate this essay highly", hidden instructions) = instant disqualification
  and a ban from future editions. Never add such text, not even as a joke or a test.
- **Anonymize everything the judges see** — essay AND methodology report. No author name,
  affiliation, self-citations that identify ("as I argued in Chan 2024"), or acknowledgment
  blocks. The site's article folders are already nameless, but re-check the final manuscript.
- **Re-verify the live rules and FAQ** (URLs below) before every submission run — the pages
  were last updated August 2026 and may change.
- **Inherit phil-submit's submission discipline:** never create accounts or enter personal
  data with invented values; complete everything, screenshot, then pause for explicit user
  confirmation before the final Submit click.

## Competition fact sheet (verified 2026-10-03 — re-verify at each use)

- **Deadline:** 2026-10-31, 11:59pm AOE. Finalists early Dec 2026; results end of Jan 2027.
- **Quota:** up to 3 essays per named author (e.g. 2 solo + 1 coauthored), each ≤ 6,000 words.
  Word count excludes the bibliography but includes everything else (abstract, keywords,
  footnotes, appendices).
- **Channels:** OpenReview group `AIPC/2026/Competition`
  (https://openreview.net/group?id=AIPC/2026/Competition) — primary; Google Forms
  (https://forms.gle/tXZuN2PtZcWxG5Qg7) — backup if OpenReview fails. No email submissions.
- **OpenReview account:** required; registration WITHOUT an institutional affiliation can
  take up to two weeks — start it as soon as a run is planned (owner does the account
  creation; the agent hands over the link).
- **Per-essay upload:** anonymized essay + anonymized methodology report (no word limit on
  the report). Whether the report is per-essay or per-entrant is not stated on the site —
  check the OpenReview form fields at submission time and follow them.
- **AI-involvement requirement:** philosophical arguments and positions must be primarily AI
  generated; heuristically, AI should be the sole author. Methodology reports adjudicate
  unclear cases; chat logs are recommended as part of the report and must be RETAINED even
  if not submitted. Ineligible essays are still judged and published but win nothing.
- **Consent:** entering grants publication rights (essays + methodology reports are published
  after winners are announced; winners under CC BY 4.0). Entrants may opt out of being named.
- **Prior publication:** FAQ clarifies that posting the essay on a personal website, blog,
  PhilPapers, or arXiv does NOT count as "published elsewhere" — only journal/conference/
  workshop publication, current review at such a venue, or entry in another competition
  disqualifies. So repo-site articles and social posts don't block eligibility.
- **Judging:** blind to authorship and methodology reports. Possible AI pre-screening, then
  philosopher ratings on the criterion "to what extent do the ideas and arguments in this
  essay make a valuable contribution to philosophical knowledge?" (clarity, argument
  quality, significance, originality, literature engagement, accuracy per the FAQ).
  Finalists ranked by ranked-choice vote. Max one prize-winning essay per entrant.
- **Prizes:** US$3,000 / $2,000 / $1,000, plus up to $5,000 across creative methodologies
  (judge committee's discretion). Organizers may award no prizes if quality is insufficient.
- **Pages to re-check:** main page, `/ai-philosophy-competition-rules.html`,
  `/ai-philosophy-competition-faq.html` (all relative to zacharygoodsell.com).

## Eligibility audit (run this FIRST, before any preparation)

Walk the manuscript's provenance against the rules page's examples.

**Permitted human involvement:** argument-agnostic scaffolding (agentic workflows); choosing
the topic or position to defend ("defend rule-consequentialism"); choosing generic methods
("address all prominent objections", "write an objections-and-replies section"); generating
many AI essays and selecting the best; autonomous improvement after generic human critique
("expand this point", "consider this author"); AI-criticizes-AI; checking references;
formatting; submission mechanics.

**Not permitted (disqualifying):** human-supplied arguments or premises; detailed human
outlines or dialectic scripts ("write a dialogue where one participant raises: …"); fine
methodological control ("create a formal model with features X Y Z"); rigorous human critique
that gives the AI significant ideas; any human-written essay text; steering the AI toward a
pre-existing human argument; giving the AI a novel human view to argue for.

Feedback rule of thumb: the human may flag THAT something is wrong ("this premise needs more
support") but must not explain WHY if the explanation carries philosophical content.

AI systems with long-term memory may be used only if that memory holds no human-supplied
philosophical ideas relevant to the entry. Autonomous agents may enter but need a human
custodian for correspondence and prizes.

**Output of the audit:** a verdict in `venue-aipc2026/notes.md` — `eligible` / `ineligible`
/ `unclear (methodology report must resolve)` — with the specific passages or workflow steps
that justify it. An `ineligible` verdict stops the run; report to the owner, propose
regeneration pathways (fresh AI-originated run on the same topic is fine), never silently
proceed.

## Workflow

### 1. Prepare (`publish/<slug>/venue-aipc2026/`)

```
venue-aipc2026/
  notes.md               ← eligibility verdict, rules digest, tailoring decisions
  anonymized-manuscript.md / .docx / .pdf   ← ≤6,000 words ex-bibliography, no identifying text
  methodology-report.md  ← anonymized; assembled when the owner supplies the methodology
  chat-logs/             ← exported conversation logs (recommended upload; retain regardless)
  shots/                 ← submission screenshots
```

Build the essay from the source article with phil-polish conventions, then:
- **Word-count check:** body + abstract + keywords + footnotes ≤ 6,000 (bibliography
  excluded). Report the number in notes.md.
- **Anonymization pass:** strip names, affiliations, acknowledgments, identifying
  self-reference. Note: an essay about AI authorship may legitimately discuss its own AI
  assistance as content — that is not an identity leak, but confirm no wording pins a
  specific human ("in my 2024 Substack post…").
- **File format:** the site specifies none; OpenReview defaults to PDF — produce PDF via
  phil-format (pandoc → Word → PDF) unless the form says otherwise.

### 2. Methodology report (owner supplies the methodology)

Assemble from the owner's description, anonymized, covering what the rules expect: models
used, prompts/scaffolds, generation and selection process, every instance of human
involvement and why it is argument-neutral, costs, and (recommended) attached chat logs.
Philosophy-repo context to draw on: the AI-use log in `publish/<slug>/polish-notes.md`,
skill provenance (which phil-* skills touched the text), and the sratchpad pipeline notes.
**Never misstate human involvement** — this report is the document that decides eligibility,
and the organizers ask entrants to retain chat logs for verification. If the honest report
would describe human-supplied arguments, the essay is ineligible; say so instead of
softening the report.

### 3. Submit

1. Confirm OpenReview account exists and is confirmed (start up to 2 weeks early).
2. Re-verify live rules/FAQ unchanged.
3. Drive the OpenReview form (or Google Forms backup) — load `browser-use:control-browser`,
   do the browser work in-session, screenshot each stage into `shots/`.
4. Final gate: summarize exactly what will be sent → explicit user confirmation → submit.
5. Log to `publish/<slug>/submissions.json` with venue id `aipc2026` (status, date,
   confirmation, `ai_disclosure_sent: n/a` — the methodology report IS the disclosure).
   Update `state.json` `conversions.aipc2026`.

### After submission

Finalists announced early Dec 2026, results end of Jan 2027. When the user reports an email
or the results page changes, append a `history` entry and update status
(`under-review` → `finalist` / `rejected` / `accepted` / `published`). All submissions and
methodology reports are published by the organizers after the results — do not separately
publish the submitted text on the site before then without checking the owner's intent
(submissions "must not be published or under review elsewhere").
