---
name: phil-polish
description: Proofread and upgrade a philosophy article to academic journal publication standard, producing polished-en.md / polished-zh.md in publish/<slug>/. Use whenever the user asks to polish, beef up, academicize, proofread, or prepare an article (EN or Chinese) for journal submission, or mentions getting an essay up to publication standard.
---

# phil-polish — bring an article up to philosophy-journal standard

Turns a draft (usually `articles/<slug>/index.md`) into a submission-grade manuscript in
`B:\ai_philosophy\publish\<slug>\`, working from `publish/README.md` conventions.

## Steps

1. **Set up the folder.** Create `publish/<slug>/` if missing; create/merge `state.json`
   (schema in `publish/README.md`). Read the source article fully before changing anything.
2. **Clean.** Strip chat-export artifacts (`citeturn…`, stray markdown debris), dead links,
   and duplicated headings. The first line stays `# Title`.
3. **Structural pass (the actual beef-up).** Assess, then rewrite:
   - Is there ONE clear thesis stated early, defended in identifiable steps?
   - Each section: what does it contribute? Cut or merge ornamental ones.
   - Anticipated objections: a publishable philosophy paper names its strongest opponents
     (with real citations) and answers them. Add/expand an objections-and-replies section if
     absent.
   - Definitions and terms of art used consistently; key concepts introduced before use.
   - Argumentative moves that assert should either argue or cite.
4. **Scholarly apparatus.**
   - Abstract (150–250 words, EN; 200–300字, CN) + 4–6 keywords (关键词).
   - Citations: only REAL sources. For every citation, verify it exists via web search
     (title + author + year + journal); add DOI where findable. If the draft cites something
     you cannot verify, flag it `TODO(author, verify): ...` — never silently keep or invent
     references. Hallucinated references are the #1 desk-reject and arXiv-ban trigger.
   - Claiming "philosophers have argued X" without a name/citation → either find one (search)
     or soften the claim.
5. **Language pass.** Academic register, precise wording, no LLM filler ("delve",
   "It is important to note"), varied sentence rhythm, consistent spelling dialect (pick
   based on target venue or US default), consistent transliteration for Chinese names
   (pinyin + characters on first mention). For `polished-zh.md`: 学术书面语, no 欧化长句
   pileups, terms with EN in parentheses on first use (生成式人工智能（Generative AI）).
6. **Length calibration.** EN general philosophy journals: 6,000–9,000 words (Analysis:
   ~4,000; Mind: ~7,500; specialist journals up to 10,000). CN CSSCI philosophy journals:
   1.5万–3万字. Trim ruthlessly toward the target venue's norm if one was given.
7. **AI-use log.** Append to `polish-notes.md` a factual log of what the AI changed at what
   date (structure, citations found, wording) — this feeds the per-venue `ai-disclosure.md`
   in the format step and CN journals' 《生成式人工智能工具使用情况说明》. Honest and specific;
   never claim "no AI was used".
8. **Write outputs.** `polished-en.md` and/or `polished-zh.md` (first line `# Title`),
   `polish-notes.md` (summary of changes, open questions, the AI-use log, TODO(author)
   list). Update `state.json` (`polish.status`, `runs`, `updated`).
9. **Report** to the user: word counts before/after, what was strengthened, every
   TODO(author) item — those are things only the human author can confirm.

## Rules

- The argument must remain the AUTHOR'S. Strengthen their thesis; never replace it with a
  different, "safer" one. When a philosophical claim is ambiguous, flag it rather than
  silently choosing an interpretation.
- No fabricated credentials, names, or affiliations. The owner is an independent philosophy
  writer — never invent institutional affiliations.
- If the target venue is `ai-banned` (check `publish/venues.json`), warn the user before
  starting: this pipeline is AI-assisted, and the venue prohibits AI-authored content.
