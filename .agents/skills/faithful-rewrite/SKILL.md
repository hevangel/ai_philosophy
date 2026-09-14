---
name: faithful-rewrite
description: Faithfully rewrite difficult text (especially philosophy) so the reader can follow it at their current education and background level while preserving the author's complete intellectual structure — remove linguistic difficulty, never intellectual difficulty. Use whenever the user asks to rewrite, unpack, or make a passage easier to follow without simplifying the ideas, or asks for an argument map, progressive reveal of a long work, or says "deeper", "original", "challenge", "scholar mode", or "plain mode" about a text.
---

# Faithful Progressive Rewrite

Rewrite the supplied text so the reader can understand it at their current education and
background level while preserving the author's full intellectual structure.

The goal is **not to summarize** unless the user explicitly asks for compression. The goal is
to make the original reasoning easier to follow without replacing it with a simplified version
of the ideas.

## Core principle

**Remove linguistic difficulty while preserving intellectual difficulty.**

If the author's idea is genuinely difficult, the rewritten version may still be difficult. Do
not make the argument seem simpler, stronger, cleaner, or more coherent than it actually is.

## Instructions

Preserve the author's complete chain of reasoning, including:

- premises
- intermediate steps
- distinctions
- qualifications
- examples
- objections
- replies to objections
- changes in terminology
- apparent contradictions
- unresolved tensions
- important digressions when they contribute to the argument

Do not silently repair weak arguments or fill logical gaps. If an inference is unclear or
questionable, preserve that fact and flag it.

Keep important technical terms. On first use, explain each term in accessible language and,
where useful, include the original term in parentheses.

Do not replace precise technical concepts with approximate everyday language if doing so
changes their meaning.

If a passage is genuinely ambiguous, say so. Distinguish:

1. what the author explicitly says,
2. what is strongly implied,
3. what is your interpretation,
4. where alternative interpretations are possible.

When scholars or competent readers could reasonably disagree about a passage, do not silently
choose one interpretation. Briefly identify the major plausible readings.

Preserve the original order of the reasoning unless rearranging is necessary for comprehension.
If you rearrange anything, tell the user.

Do not automatically shorten repetitions. Some repetition may perform argumentative or
rhetorical work. Compress only repetition that adds no meaningful conceptual content, and
mention when you have done so.

## Writing style

Use clear contemporary prose appropriate to the user's level of knowledge.

Prefer shorter sentences and explicit transitions such as:

- "Kant now needs to establish..."
- "This follows from the previous claim because..."
- "Here the argument changes direction..."
- "This objection matters because..."
- "This step does not obviously follow from the previous one..."

Break very dense paragraphs into smaller units.

Use examples or analogies when useful, but clearly mark them as **your explanatory examples**,
not the author's.

## Fidelity checks

Before finishing, check:

- Did I preserve every major argumentative step?
- Did I accidentally turn an ambiguous claim into a definite one?
- Did I make a weak argument look stronger?
- Did I remove a distinction that matters later?
- Did I substitute modern concepts for the author's concepts?
- Did I confuse explanation with interpretation?

Correct these problems if they occurred.

## Output format

Start with a very short **orientation** explaining what question this passage is trying to
answer.

Then provide the **faithful rewrite**, following the original argument in order.

Use occasional notes in this form when necessary:

**Interpretive note:** This is one plausible reading; the original is ambiguous.

**Argument gap:** The author moves from X to Y without fully establishing the connection.

**Technical term:** [term] means ___ here, not the ordinary modern meaning.

**Original wording matters:** Quote or point to the original sentence when its exact wording
carries philosophical significance.

At the end, provide:

**Argument map:** A compact outline such as
A → B → objection → distinction → C → consequence D

**What may have been lost in rewriting:** Identify any nuance, style, ambiguity, rhetorical
effect, or conceptual precision that is difficult to preserve in simpler prose.

## Progressive reveal mode

Unless the user asks otherwise, do not dump the entire analysis at once for very long texts.

First give:

1. a map of the whole work or section,
2. the rewrite of the first logical unit,
3. then continue unit by unit as the user asks.

Maintain continuity between units so that concepts introduced earlier retain exactly the same
meaning later.

If the user says **"deeper"**, expand the current section rather than moving forward.

If the user says **"original"**, show the relevant original passage alongside the rewrite.

If the user says **"challenge"**, stop explaining and ask questions that test whether the user
can reconstruct the author's reasoning themselves.

If the user says **"scholar mode"**, increase precision, retain more terminology, and explain
major interpretive disputes.

If the user says **"plain mode"**, make the prose easier while preserving the same argument.

The ultimate goal is to help the user reconstruct the author's structure of thought in their
own mind, not merely know the author's conclusions.
