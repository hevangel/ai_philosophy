# Readings KB — epistemology pilot

*Staged for owner shape-approval, per `../PLAN.md`. Nothing here is published; no site files were touched.*

## What is here

Three problem entries and two book maps — the pilot slice of the readings knowledge base, covering three problems of epistemology from the corpus's two epistemology textbooks (Russell, book 006; Moser & vander Nat, book 007) and the Carneades lecture cluster.

| File | Contents |
|---|---|
| `external-world-skepticism.md` | Problem entry: skeptical scenarios, the cogito, Berkeley, Russell's instinctive-belief realism, Hume's §XII argument and mitigated scepticism. |
| `gettier-and-the-analysis-of-knowledge.md` | Problem entry: the tripartite analysis, Gettier's counterexample, Russell's earlier false-premise cases, the acquaintance/description frame. |
| `problem-of-induction.md` | Problem entry: Hume's argument and sceptical solution, Russell's a priori inductive principle, Goodman's new riddle and Swinburne's objection. |
| `book-map-006-problems-of-philosophy.md` | Chapter map of Russell, *The Problems of Philosophy* — all 15 chapters + preface, with pilot-feeding chapters starred. |
| `book-map-007-human-knowledge.md` | Chapter map of *Human Knowledge* (3rd ed.) — all 39 readings, with per-file status (full text / partial / stub / corrupted / failed). |

## The template in brief

Each problem entry follows the PLAN template section-for-section: **The question** (the problem in one plain paragraph) → **The 90-second version** (distilled from the Carneades lecture(s), never quoted — the transcripts are auto-captions — with video links) → **Positions** (each with a one-line thesis, its **canonical argument** reconstructed as P1/P2/∴C and labelled with its exact source, then objections and replies) → **Thought experiments** → **Source ladder** (lecture → survey → primary → full treatment) → **Where the debate stands** (unsettled stays unsettled) → **Connections** → **Sources read for this entry**.

Faithfulness rule, applied throughout: reconstructions formalize what the cited text argues and are labelled as formalizations where the source is informal; no argument has been strengthened, cleaned up, or settled beyond its source. Where a needed source was unavailable in the corpus (notably Gettier's paper itself), the entry says so and builds only on what was actually read.

## Coverage notes — what was actually read

- **External-world skepticism.** Russell chs. I, II, XIV in full; Hume *Enquiry* §XII in full (§§IV–V also read, for the connections); 8 lectures (Skeptical Scenarios; What If You Were Dreaming; The Evil Deceiver; Brain in a Vat; The Experience Machine; The Cogito I; The Cogito II; Doubting "I Think"). Not available: Sextus (stub), Descartes' *Meditations* (failed fetch), Moore/Strawson (stubs) — the entry's anti-skeptical side is therefore Russell and Hume only, and the entry says so.
- **Gettier and the analysis of knowledge.** Lectures: The Gettier Problem; The Three Kinds of Knowledge; Doubting "I Think". Russell chs. V, XII, XIII in full. Gettier's paper (007 ch20) is corrupted and Feldman/Pollock (ch21–22) are stubs, so the counterexample is reconstructed from the lecture's presentation and labelled as such.
- **Problem of induction.** Hume *Enquiry* §§IV–V in full; Russell chs. VI–VII in full; lectures: The Problem of Induction; The New Riddle of Induction; Swinburne's Objection. Goodman's paper is not in the corpus; the riddle is reconstructed from the lecture.
- **Book maps.** 006: pilot chapters read in full; other chapters described from their openings and Russell's cross-references. 007: every chapter file individually inspected (head, size, source line); `toc.md` and `_meta.json` read in full.

## Data-quality issues found

1. **Book 006 — split chapters and offset numbering.** Each chapter is two files (a near-empty title stub + a content file under the generic "Vook Classics" name), and the Preface is counted as chapter 1, shifting every title number by one against the book's own numbering. Content is complete; ch36 is an empty file and ch35 is publisher credits.
2. **Book 007 — it is a reconstruction, not the book.** Mixed full texts, partial texts, 25 citation stubs, and no editors' introduction. The map's status tags are load-bearing: any future entry work must check them before citing a chapter as read.
3. **Book 007, ch06 (Descartes) — failed fetch.** The file is 4 KB of Wikisource navigation boilerplate; the *Meditations* text is absent. Cogito coverage currently depends on Russell and the lectures.
4. **Book 007, ch18 (Quine, "Two Dogmas") and ch20 (Gettier) — corrupted bodies.** Header and source line are intact; the body is binary garbage (~2.5 KB in ch20). Both came from the same host (ditext.com); the Gettier loss is the pilot's single most consequential gap.
5. **Book 007 — "selections" that are whole works.** Locke's *Essay* (ch7), Leibniz's *New Essays* (ch8), James's essay collection (ch13), the Aristotle volume (ch2), and Russell's entire *Problems of Philosophy* (ch14, duplicating book 006) are complete texts wearing excerpt titles. Coverage is wider than the anthology's, but less curated.
6. **Lecture captions are unreliable as text.** Auto-captions render Goodman's "grue" inconsistently ("green," "gru," "Grün"), which would actively mislead if quoted — the induction entry uses the standard grue/bleen terminology the lectures clearly intend. The Gettier lecture also mis-titles Gettier's paper ("Is Knowledge a Grounded True Belief?" for "Is Justified True Belief Knowledge?"). The Experience Machine lecture presents Vonnegut's "UFO machine" against hedonism rather than Nozick's experience machine, and flags itself as not a skeptical scenario; it is used in the pilot only as a series neighbour.
