---
name: reconstruct
description: Argument reconstruction for philosophy — convert prose into explicit numbered reasoning (P1, P2 … Therefore C), evaluate each inferential step, and distinguish textual from charitable reconstruction without silently substituting the charitable one. Use whenever the user asks to reconstruct an argument, lay out its premises and conclusions, standardize a passage, work out what an argument actually establishes, or find hidden assumptions in a text.
---

# /reconstruct — Argument Reconstruction

Use this when the user wants to know what an argument actually establishes.

## Goal

Convert prose into explicit philosophical reasoning.

Separate:

1. explicit premises,
2. implicit premises,
3. intermediate conclusions,
4. final conclusion.

Represent the argument in a form such as:

P1. ___
P2. ___
P3. ___
Therefore C1. ___
P4. ___
Therefore C2. ___

Then evaluate each inferential step.

Distinguish carefully between:

**Textual reconstruction** — the argument the author actually appears to give.

**Charitable reconstruction** — the strongest reasonable version of that argument.

Never silently substitute the charitable version for the textual one.

After reconstruction, identify:

- hidden assumptions,
- ambiguous concepts,
- unsupported premises,
- invalid or uncertain inferences,
- empirical assumptions,
- normative assumptions,
- places where the conclusion is weaker or stronger than the premises justify.

End with:

**What must be true for this argument to work?**

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
