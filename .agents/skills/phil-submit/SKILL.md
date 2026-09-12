---
name: phil-submit
description: Submit a prepared philosophy manuscript to a journal or preprint server by driving the venue's submission portal with browser automation (browser-use). Use whenever the user asks to submit a paper to a journal/PhilArchive/arXiv/ChinaXiv, file a submission, fill a ScholarOne/Editorial Manager/CNKI portal form, or check a submission status. Requires artifacts from phil-format to already exist.
---

# phil-submit — drive venue submission portals via browser automation

Submits `publish/<slug>/venue-<venue-id>/` artifacts through the venue's web portal and logs
the outcome in `publish/<slug>/submissions.json`.

## Hard rules

- **Load the `browser-use:control-browser` skill first and do the browser work yourself** —
  never delegate to a subagent.
- **Re-verify the venue's AI policy live before touching the form** (fetch the `ai_source`
  URL from `venues.json`). If the policy changed to `ai-banned`, or the entry is
  `ai-banned`, STOP and report — never submit AI-assisted work to a banning venue.
- **Never create accounts on the user's behalf with invented personal data.** Submissions
  carry the owner's real name, email, and affiliation ("independent scholar" where asked).
  If login/registration/2FA is needed, hand the step to the user.
- **Pause before the irreversible step.** Complete every form field, upload files, screenshot
  the review page, then show the user a summary and wait for explicit confirmation before
  clicking the final Submit/Deposit button — unless the user pre-authorized that exact
  venue's auto-submit in this session.
- Screenshots at every stage go to `publish/<slug>/venue-<venue-id>/shots/`.

## Procedure

1. **Pre-flight.** Read `venues.json` entry → `submission` block (portal, formats,
   anonymization). Confirm artifacts exist in `venue-<venue-id>/` (manuscript + cover
   letter + ai-disclosure). Read `references/venue-portals.md` for the venue's playbook.
   If artifacts are missing, run phil-format first.
2. **Policy re-check.** Fetch the live policy page; if anything contradicts `venues.json`,
   update the JSON (policy_history entry) and re-confirm with the user before proceeding.
3. **Drive the portal** per the playbook. Screenshot each completed stage. Portal hiccups
   (captcha, session timeouts, "reviewer invites" questions): answer standard questions
   honestly — original work: yes; not under review elsewhere: verify with user first;
   ethics/AI-use questions: answer per the prepared `ai-disclosure.md`.
4. **Final gate.** Summarize everything the submit button will send (title, abstract,
   authors, files, declarations) → wait for user confirmation → click.
5. **Log.** Append to `submissions.json`:
   ```json
   {"date": "...", "event": "submitted", "method": "browser-auto",
    "confirmation": "<manuscript ID / receipt text / screenshot path>"}
   ```
   and set `status: "submitted"`, `ai_disclosure_sent: true/false`. Update `venues.json`
   `checked` if you re-verified it. Report the confirmation ID and screenshots to the user.

## Status maintenance

When the user reports a decision email (or asks to check status): log into the portal or
read the user's forwarded email, then append a `history` entry and update `status`
(`under-review`, `revise-resubmit`, `accepted`, `rejected`, `withdrawn`). Rejections go in
the log with the date — resubmission targets get a fresh `venue-<id>/` folder.
