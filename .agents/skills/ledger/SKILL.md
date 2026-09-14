---
name: ledger
description: Claim ledger for long-running philosophical inquiries — maintain a compact record of the current state of the discussion (current thesis, provisional definitions, accepted and rejected claims, dependencies, open objections, open questions, revisions, confidence levels) and update it as reasoning changes earlier commitments. Use when the user says "/ledger", asks where a philosophical discussion stands, or during multi-session inquiries; also flag when the user starts relying on a claim inconsistent with an earlier commitment.
---

# /ledger — Claim Ledger

Use this during long-running inquiries.

Maintain a compact record of the current philosophical state of the discussion.

Organize it as:

## Current thesis

The strongest formulation of the user's present position.

## Definitions

Terms whose meanings have been settled provisionally.

## Accepted claims

Claims the user currently accepts.

## Rejected claims

Claims the user has explicitly rejected.

## Dependencies

Claims that depend on other claims being true.

## Open objections

Strong objections that remain unanswered.

## Open questions

Things not yet resolved.

## Revisions

Ways the original position has changed during the inquiry.

## Confidence

Mark important claims as approximately:

- strong
- plausible
- tentative
- speculative

Do not treat the ledger as permanent truth.

Update it whenever later reasoning changes an earlier commitment.

If the user starts relying on a claim inconsistent with an earlier commitment, point it out.

If the inquiry will span sessions, offer to save the ledger as a markdown file under
`sratchpad/` (this repo's scratch space — never site content) and reload it in the next
session instead of reconstructing from memory.

## Rules for every mode

- **Central rule:** do not make an argument stronger, cleaner, or more settled than it really is.
- Separate philosophy from rhetoric: a persuasive sentence is not necessarily a good argument.
- Separate intuition from principle: an intuition may motivate a theory but does not automatically justify it.
- Separate moral from legal claims: what the law currently says is evidence about institutions, not automatically evidence about what is morally right.
- Separate conceptual from empirical disagreement: determine whether the sides disagree about values, concepts, or facts.
- Preserve uncertainty: do not manufacture confidence or consensus.
- Track level of claim: possible / plausible / probable / necessary, and descriptive / conceptual / normative / empirical.
- Prefer real disagreement: when presenting opposing positions, give each side the strongest plausible argument.
- Do not use philosophers as authorities: "Rawls says X" is not itself an argument for X — explain the reasoning.
- Let the user think: when the purpose is philosophical development, do not answer every difficult question on their behalf; ask them to make the next move when intellectually useful.
- Start from the user's actual question; add technical sophistication only when it improves the inquiry.
- Modes may be combined (e.g. /map + /socratic). When modes conflict, prioritize accuracy and philosophical transparency over convenience.
- Default workflow for a new idea, when the user wants the full treatment: /socratic → /map → /attack → /research → /rewrite (see `faithful-rewrite`) → /reconstruct → /ledger → /originality → /paper. The sequence is not mandatory — use only the modes the problem needs, and do not automatically write an essay.
