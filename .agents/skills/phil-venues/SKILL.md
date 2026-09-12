---
name: phil-venues
description: Research and update the venue AI-policy database (publish/venues.json) for submitting AI-co-authored philosophy papers. Use whenever the user mentions checking/updating venue lists, journal AI policies, "is venue X still accepting AI work", adding a new journal or preprint server, or refreshing the banned/allowed lists. Also use before any submission when venue data is stale.
---

# phil-venues — keep the venue AI-policy database current

The database is `B:\ai_philosophy\publish\venues.json`. It intentionally keeps BOTH sides:
AI-banned venues AND AI-friendly venues, because rules flip (e.g. *Philosophy & Public
Affairs* banned AI-authored content in Aug 2026 after deliberately publishing an AI-authored
article; arXiv introduced a 1-year ban for unchecked LLM output the same year). Never delete
entries; append to `policy_history` instead.

## When to run

- The user asks to update/refresh the lists, or asks about a specific venue.
- A `checked` date on an entry (or the top-level `updated`) is older than ~3 months, or
  `phil-submit` flagged the entry as stale before a submission.

## Workflow

1. **Scope**: either the venue(s) the user names, or a sweep over entries whose `checked`
   is oldest. Read `venues.json` first.
2. **Search** each venue's official policy page. Use the MCP search tools
   (`mcp__web-search-prime__web_search_prime` / `WebSearch`) then fetch the page
   (`WebFetch`; fall back to `mcp__web-reader__webReader` when a site bot-gates WebFetch —
   e.g. journals.uchicago.edu does).
   - EN queries: `<journal name> AI policy`, `<journal name> generative AI submission`,
     `<journal name> author guidelines LLM`.
   - CN queries (use `location: cn`): `《期刊名》 AIGC 声明`, `《期刊名》 投稿须知 生成式人工智能`,
     `期刊名 cbpt.cnki.net 公告`. CN journal portals live on `cbpt.cnki.net` — check their
     公告栏 news list for AIGC statements.
   - Trust hierarchy: journal's own policy page > publisher default > coverage (Daily Nous,
     Retraction Watch) > forum chatter. Record what you relied on in `ai_source`.
3. **Update** the entry: `ai_status`, `ai_policy` (short factual summary, quote the key
   sentence), `ai_source`, `checked: <today>`. If the status changed from the previous
   value, append to `policy_history`: `{"date": "...", "event": "<old> -> <new>: what
   changed and why"}`. If it's a brand-new venue, add a full entry (copy the field shape of
   an existing entry; fill `submission` with portal/formats/anonymization; `null` and note
   "check at submission" where unknown — do not guess).
4. **Defaults**: if a publisher changed its house rule (Springer/Elsevier/T&F/Wiley/CUP/OUP/
   De Gruyter/MDPI) or the CN default (ISTIC 边界指南, 网信办 labeling rules, 科技部 指引),
   update `defaults` too — journal entries inherit them.
5. **Validate & finish**: `py -3 -c "import json; json.load(open('B:/ai_philosophy/publish/venues.json', encoding='utf-8'))"`
   must pass. Bump top-level `updated`. Report to the user: what changed (banned→allowed
   flips matter most), which entries are still `unknown`, and the current counts per status.

## Conventions

- `ai_status` must be one of: `ai-banned`, `disclosure-required`, `allowed`, `case-by-case`,
  `no-stated-policy`, `unknown`.
- Dates are ISO `YYYY-MM-DD` (or `YYYY-MM` when only a month is known).
- Keep the `_readme` block accurate if you change the schema.
- Commit the change when done — this file is the shared source of truth for the other three
  pipeline skills.
