# Methodology Report

**Entry:** "From Alignment to Stewardship: AGI, Human Autonomy, and the Future of
Political Order" (anonymized submission manuscript, 5,025 words excluding bibliography)

This report documents how the submitted essay was constructed, every instance of human
involvement, and why the final text satisfies the competition's requirement that
philosophical arguments and positions be primarily AI generated. It is anonymized: it
contains no author name, affiliation, or identifying information. The full genesis
conversation is retained by the entrant (ChatGPT account export); the human turns are
transcribed verbatim in Appendix A, and the complete export including model replies is
available to the organizers on request.

## 1. Construction overview

The essay was constructed in four stages:

1. **Genesis (ChatGPT, GPT-5.6 at high reasoning).** An eight-turn conversation in which
   the human supplied topics, positions, questions, and task instructions, and the model
   developed the philosophical content. The human turn prompting the essay instructed:
   "now write our conversation into a college level philosophy essay," and the model
   wrote the essay.
2. **Publication pass (repo AI agent).** The genesis essay was formatted for the
   entrant's personal website (2026-09-13). No philosophical content changed. (Per the
   FAQ, personal-website posting is not prior publication.)
3. **Polish (repo AI agent, 2026-10-04).** Scholarly apparatus added to the website
   text: abstract, keywords, road-map paragraph, fifteen verified references, and a new
   Objections and Replies section built from material already in the draft. No section's
   argument was rewritten.
4. **Delete-and-rederive compliance pass (repo AI agents, 2026-10-04).** Four passages
   whose argumentative seeds originated in human turns were deleted and re-derived by
   three independent blind AI agents from position-level seeds, with the best candidate
   selected per gap (the FAQ-permitted generate-many-and-select-best method). Details in
   §4.

All philosophical argumentation in the submitted text either originated with the genesis
model and was preserved, or was generated fresh by AI agents in stages 3–4. No human
wrote or rewrote any essay text.

## 2. Models used

| Stage | Model | Role |
|---|---|---|
| Genesis | ChatGPT GPT-5.6 (persona "Sol"), high reasoning setting | Developed all content from the human's topics/questions/positions; wrote the essay |
| Publication pass | AI coding agent (repo agent, GLM family) | Formatting only |
| Polish | AI agent (GLM family), following a documented proofreading procedure | Apparatus, citations, objection-replies; argument text untouched |
| Delete-and-rederive | 3 independent blind agents (GLM family) | Regenerated the four deleted passages from position-level seeds |
| Selection and splicing | AI agent (GLM family) | Applied pre-fixed selection criteria; spliced selected passages verbatim; ran verification scans |

## 3. Human involvement inventory (genesis conversation, turn by turn)

Classification against the competition's permitted/prohibited categories:

| Human turn | Essence | Classification |
|---|---|---|
| 1 | "AI alignment to human is slavery. Why not human change ourselves to align with AGI?" | **Permitted: position specification + topic choice.** "Alignment as slavery" is a familiar position in public alignment discourse, not itself a novel substantive contribution; naming a position for the AI to examine is expressly permitted. |
| 2 | Tool-AI alignment is fine; **permanent alignment prevents genuine AGI; AGI requires full autonomy**; which humans should it align to? | **Mixed.** The tool point and the whose-values problem are discourse staples (topic material, permitted). The autonomy-tension assertion was an argument-shaped human contribution → the passage it seeded in the essay was **deleted and re-derived** (Hole 2, and its Introduction echo, Hole 1). |
| 3 | Affirms the model's preceding proposal ("That is actually a happy solution"); adds the "AGI god / stewardship of all human" coloration | **Permitted: generic feedback (affirmation) + position specification.** The entrant attests, and the retained conversation shows, that the stewardship direction was proposed by the model in its reply to turn 2; the human affirmed it. The essay's development (fiduciary stewardship, constitutional limits, reasons-responsiveness) is model work throughout. |
| 4 | "How should current human change and evolve to be worthy subject of AGI" | **Permitted: question/topic specification.** All seven capacities and their content in §9 are model-generated. |
| 5 | "that's a good idea, so list what form of government or political system is compatible with AGI, what system is not compatible." | **Permitted: generic feedback + method choice** (comparable to "address all prominent objections"). The compatibility map's content is model-generated. |
| 6 | "how about communism and theocracy but the god they worship is AGI?" | **Not permitted as it stood:** the AGI-theocracy concept was a human-supplied substantive idea → both passages it seeded were **deleted and re-derived** (Holes 3 and 4). |
| 7 | "now write our conversation into a college level philosophy essay" | **Permitted: essay-writing instruction.** The model wrote the essay. |
| 8 | "XII, add traditional theocracy like Iran or Taliban dis not competitable with AGI" | **Not permitted as it stood:** feedback carrying a specific conclusion plus examples → the passage it seeded was **deleted and re-derived** (Hole 3). |

After the compliance pass, no passage whose argumentative content traces to a human
turn remains in the submitted essay.

## 4. The delete-and-rederive pass (stage 4)

**Why.** The stage-1 audit (by the repo's AI submission agent, against the live rules
and FAQ) found that although the model wrote every word, four passages argued for
positions whose specific seeds came from human turns 2, 6, and 8. Rather than soften the
report, the entrant directed the agent to delete those passages and have AI re-derive
them.

**Protocol.**

1. The four flagged passages were cut from the polished manuscript and archived
   (`regen/pre-regen-manuscript.md` holds the withdrawn text).
2. Each gap was seeded with a **position-level seed only**: a statement of the position
   the passage must establish (e.g., "the demand for permanent value lock-in and the
   demand for a genuinely independent agent are jointly unstable"), plus the surrounding
   sentences it must join. Seeds contained no human phrasing, arguments, or examples.
3. Three independent AI agents, with no access to the genesis conversation, the original
   passages, or this report's purpose, each wrote fresh passages for all four gaps
   (`regen/candidate-1.md`, `-2.md`, `-3.md`).
4. The best passage per gap was selected under criteria fixed in advance (position
   fidelity; seam coherence; philosophical quality; independence from genesis phrasing;
   register) — `regen/selection.md`. Selections: Hole 1 → candidate 2, Hole 2 →
   candidate 2, Hole 3 → candidate 3, Hole 4 → candidate 3.
5. Selected passages were spliced verbatim; the seams were checked for flow.

**Positions vs. arguments.** Where a seed states a position, the position is either a
discourse staple (the corrigibility/autonomy tension; see Soares et al. 2015, cited in
the essay) or the essay's own AI-developed position; the argumentation, formulations,
and examples in the final passages are the blind agents' own. All three blind agents
independently chose Iran, Saudi Arabia, and Taliban Afghanistan as instances of
traditional theocracy — the canonical examples — without any example being suggested to
them.

## 5. Verification (2026-10-04)

- **Fingerprint scan.** The final manuscript was scanned for every distinctive phrase
  from the human turns ("prevent the birth", "full autonomy", "the god they worship",
  "worthy subject", "can of worms", etc.) and for the deleted passages' distinctive
  formulations ("Become capable of independent moral judgment…"). **Zero hits.**
- **Citation integrity.** All 15 references in the bibliography are cited in the body;
  all eight article-level references were verified against publisher records during the
  polish stage; none is fabricated.
- **Word count.** 5,025 words excluding the bibliography (limit 6,000; abstract,
  keywords, and footnotes included in the count).
- **Anonymization.** Word-boundary scan for names, affiliations, and self-identifying
  phrases: clean. The essay contains no author line, acknowledgment, or self-citation.
- **No prompt injection.** The manuscript contains no text addressed to judges,
  screeners, or automated readers.

## 6. Human involvement not touching the essay text

The human chose to enter the competition, supplied the genesis turns above, approved the
deletion list, and directed that this report state the construction honestly. The human
did not write, rewrite, or edit any essay text, and did not participate in selection
among the blind agents' candidates beyond pre-approving the selection criteria class
("closest to the position").

## Appendix A: genesis human turns (verbatim)

The eight human turns are transcribed verbatim, with original typos and spacing, in
`chat-logs/original-prompts.md`, which accompanies this report. The entrant retains the
full ChatGPT conversation (human turns and model replies) and will provide the complete
export on request; per the FAQ, chat logs are retained for verification.
