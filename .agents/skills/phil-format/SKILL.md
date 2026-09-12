---
name: phil-format
description: Convert a polished philosophy article markdown into each venue's required submission format (DOCX, PDF, LaTeX) with per-venue tailoring — blinding for double-blind journals, cover letter, AI disclosure statement, CN journal formatting. Use whenever the user asks to convert/format/prepare a manuscript for a journal or preprint server, make a submission-ready PDF/DOCX/Word file, anonymize a manuscript, or write a cover letter / AI disclosure.
---

# phil-format — venue-specific submission artifacts

Produces everything a venue's upload form wants, into `B:\ai_philosophy\publish\<slug>\venue-<venue-id>\`.
Schemas and folder layout: `publish/README.md`. Venue requirements: `publish/venues.json`.

## Steps

1. **Read the venue entry** in `publish/venues.json` (`id`, `submission.formats`,
   `anonymized`, `ai_status`, `notes`). If `checked` is stale (>3 months) or the entry is
   `unknown`, run the phil-venues flow for it first.
2. **Pick the manuscript.** `publish/<slug>/polished-en.md` (or `-zh.md` for CN venues —
   all CN journals want Chinese; 《世界哲学》 also expects an English abstract + title).
   If polished files don't exist, tell the user to run phil-polish first.
3. **Tailor per venue** — each venue gets its own `venue-<venue-id>/` folder, never
   overwrite another venue's artifacts:
   - **Double-blind journals** (`anonymized: true` — most EN journals): produce
     `blinded-manuscript.md` first: strip author name, acknowledgments, funding, and
     self-identifying phrases ("as I argued in <my 2023 paper>"), replace with
     `REDACTED FOR REVIEW`. Convert the blinded file.
   - **Word limit**: count (`py -3 -c "print(len(open(r'<file>',encoding='utf-8').read().split()))"`);
     if over the venue's limit, trim (flag cuts in `notes.md`, don't silently butcher) or
     ask the user.
   - **Citation style**: EN analytic journals mostly author-date (Chicago) or notes style —
     match the venue's recent issues if known; CN journals: 脚注 GB/T 7714 style
     (作者：《书名》，出版社，年份，页码。). Restructure only if the venue demands it; note the
     style used in `notes.md`.
   - **CN extras**: 中文摘要+关键词 AND (for 《世界哲学》-type venues) English title+abstract;
     justified body text is handled by the DOCX font pass.
4. **Convert** with the bundled script:
   ```
   py -3 "B:\ai_philosophy\.agents\skills\phil-format\scripts\md_to_docx.py" <in>.md <venue-folder>\manuscript.docx
   py -3 ... <in>.md <venue-folder>\manuscript.pdf --pdf      # needs desktop Word
   py -3 ... <in>.md <venue-folder>\main.tex   --latex         # arXiv-class only
   ```
   CJK is auto-detected. The script strips `citeturn` artifacts, converts via pandoc
   (footnotes survive), and sets Times New Roman / 宋体 fonts. DOCX is the canonical
   journal format; PDF only where the venue demands it (PhilArchive, SSRN, preprint
   servers); LaTeX only for arXiv. If Word COM PDF export fails, deliver the DOCX and say
   so — don't silently skip.
5. **Cover letter** (`cover-letter.md`): addressed to the journal editor; states title,
   word count, thesis in two sentences, why this venue (fit with its scope/special
   issues), original-work + not-under-review-elsewhere declarations. Plain, no flattery.
6. **AI disclosure** (`ai-disclosure.md`): built from the venue's `ai_status`:
   - `disclosure-required` EN (e.g. Springer): one paragraph naming the AI tools used and
     the nature of assistance (research assistance, drafting suggestions, copy-editing),
     affirming human authorship and full verification of content.
   - CN venues: full 《生成式人工智能工具使用情况说明》 per the CN default in `venues.json`
     (tool name/version/vendor, dates+purposes, prompts and generated-content records,
     verification confirmation) — source the specifics from `polish-notes.md`'s AI-use log.
   - `ai-banned` venues: STOP. This pipeline is AI-assisted; tell the user the conflict
     instead of producing a file.
   - `no-stated-policy`/`case-by-case` preprint servers: include the statement anyway
     (transparency is the pipeline's standing rule).
7. **Verify**: list the venue folder's contents, check the DOCX opens (re-open with
   python-docx and count paragraphs), confirm no `TODO(author)` strings remain (grep),
   then update `state.json` → `conversions["<venue-id>"] = {status: "done", artifacts: [...]}`.

## Example artifact set for `publish/my-article/venue-philarchive/`

```
manuscript.pdf        (PhilArchive takes PDF only)
cover-letter.md       (short deposit note)
ai-disclosure.md      (transparency statement even though no policy exists)
notes.md              ("PDF only; not anonymized; checked policy 2026-09-11")
```
