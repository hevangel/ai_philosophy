# Readings knowledge base — design & build plan

*Second knowledge base (companion to the popcult-index), built from the
`data/philosophy_readings` corpus: ~42 philosophy textbooks, introductions,
anthologies and primary texts, plus 817 Carneades lecture transcripts.
Owner decisions locked 2026-10-18 (see "Decisions").*

## Decisions (owner, 2026-10-18)

1. **Public** — this KB is a public site feature, like /popcult.
2. **Argument reconstruction** — entries carry P1/P2/∴C reconstructions of
   the canonical arguments, faithful to the source: never stronger,
   cleaner, or more settled than the text really is (repo house rule).
3. **Lectures are the front door** — each entry opens with the plain-language
   90-second layer distilled from the Carneades lecture(s), with video links.
4. **Build on the 26 extracted books first**; the remaining books (PDF-only
   extractions) join later.
5. **Language** — build in English; 李天命的思考藝術 (book 002) is translated
   into English for inclusion. Eventually bilingual: the Chinese edition uses
   Hong Kong Traditional Chinese with HK philosophy terminology, following
   `.agents/skills/zh-translate/SKILL.md`. English first.

## Why this KB is not the popcult-index

Popcult is a reverse index over essays that *apply* philosophy: concept →
chapters that use it, one relation note per link. The readings corpus *is*
the philosophy: textbooks stage positions and arguments, anthologies carry
primary papers, and the lectures are already atomic one-problem explainers.
So the unit of this KB is not the chapter×concept link — it is the
**problem**, with its positions, arguments, objections, and sources.

## Shape

Three layers:

1. **Problem entries** (the product). Spine: Subfield → Problem → Positions
   → Arguments. See the entry template below.
2. **Book layer.** One page per book: a structured chapter map (what each
   chapter covers, which problems it feeds). Makes coverage auditable
   without deep-reading front matter and exercises.
3. **Lecture layer.** The 817 transcripts indexed by problem. Auto-captions
   are noisy: lectures are pointers and plain-language raw material, never
   quotable text. Distill, don't quote.

### Problem entry template

```markdown
# <Problem name>
*Subfield: <…> · Also known as: <…>*

## The question
<The problem stated plainly, one short paragraph.>

## The 90-second version
<Distilled from the Carneades lecture(s); link the video(s).>

## Positions
### <Position name>
<One-line thesis. Best faithful statement of the view.>
**Canonical argument** (source: <book, chapter>):
- P1 …
- P2 …
- ∴ C …
**Objections** — <objection, its source> → **Replies** — <…>

## Thought experiments
<Where the problem is driven by one: the setup, what it is meant to show,
which positions it pressures.>

## Source ladder
- Start: <lecture> → Survey: <textbook chapter> → Primary: <anthology
  paper / primary text> → Full treatment: <book>

## Where the debate stands
<Honest status: what is settled, what is not. Unsettled stays unsettled.>

## Connections
<Links to sibling problems.>

## Sources read for this entry
<Every book chapter / lecture actually read, so coverage is auditable.>
```

## Build order

1. **Pilot (epistemology)** — 3 problem entries + chapter maps for the two
   epistemology textbooks, staged in `pilot/` for owner shape-approval
   before anything is published:
   - External-world skepticism (skeptical scenarios; cogito as a thread)
   - The analysis of knowledge and the Gettier problem
   - The problem of induction (incl. the new riddle)
   Sources: Russell, *The Problems of Philosophy* (006); Moser & vander
   Nat, *Human Knowledge* (007); the skepticism / Gettier / induction
   lecture cluster.
2. Owner reviews the pilot shape → adjust template.
3. Scale subfield by subfield across the 26 extracted books; grow the
   problem taxonomy bottom-up from textbook tables of contents + lecture
   titles (holes drive additions, as in popcult).
4. Translate book 002's relevant content into English as its subfield
   (logic & critical thinking) is built.
5. Publish: entries into `knowledge-base/` + site registration/explorer
   (mechanics decided at publish time, after the shape is proven).
6. Later: remaining 16 books (PDF extraction), then the zh-HK edition.

## Data-quality notes (from corpus inspection, 2026-10-18)

- 26 of 42 books have extracted markdown (1,131 chapter files); 24 epub +
  ~12 pdf still partly unextracted. Pilot works with what is extracted.
- Extraction quirk to fix during the book-layer pass: Taylor, *Metaphysics*
  (013) — every chapter file is titled "The Semantics and Metaphysics of
  Natural Kinds"; chapter titles need recovery from the text/TOC.
  **[Superseded 2026-10-18:** the whole folder *is* that volume — Beebee &
  Sabbarton-Leary (eds.), *The Semantics and Metaphysics of Natural Kinds*
  (2010). The catalogue attribution to Taylor was wrong; Taylor remains
  unextracted. See `DATA_QUALITY.md` — 8 of 26 folders are misattributed.]
- Lecture transcripts are auto-generated captions (lowercase, unpunctuated)
  — handle as raw material only.

## Build state

*Scale-up executed 2026-10-18 (owner approved the pilot shape). One line per subfield, as reported by the builders; assembly (index, lecture index, data-quality audit) by the coordinator.*

- Epistemology extension (2026-10-18): six new entries — perception/sense-data, acquaintance/description, a priori knowledge, truth, memory, testimony — complete the full-entry potential of books 006–007; all remaining epistemology gaps are stub-driven (007's contemporary sections), not topic-driven.
- Logic & critical thinking (2026-10-18): book maps for 002/008/025; 5 entries (arguments & validity; semantic analysis; fallacies & sophistry; closed systems; Gödel & self-reference); book 002's full TOC + 7 chapters translated to English — corpus findings: book 025 has no text at all, and book 002's folder is interleaved with a Simpsons volume; translations of 002 chs. 11–12 still outstanding (read in the original, flagged in place).
- Metaphysics (2026-10-18): 013 re-catalogued — folder is Beebee & Sabbarton-Leary (eds.), *The Semantics and Metaphysics of Natural Kinds* (2010), not Taylor's *Metaphysics* — book map + 6 entries (natural kinds, rigidity, essences/identities, necessary a posteriori, hierarchy thesis, Hume's Dictum) built from its 12 full-text papers; Taylor remains unextracted.
- Ethics & metaethics (2026-10-18): 11 entries + 3 book maps (028 fully supports 10 entries; 005 supports the bullshit entry with Frankfurt flagged as presented-only; 004 "On Manners" is a mislabelled novel and supports nothing — manners survives only as politeness material inside the bullshit entry).
- Political philosophy (2026-10-18): 6 book maps + 5 entries (Mill harm principle, Nozick entitlement vs pattern, minimal state, Arrow's theorem, democracy/voting paradoxes) — with a correction: the two 012 folders are the 3rd (full text) and 2nd (reconstruction, 46/48 stubs) editions of the Goodin & Pettit anthology, and no Kymlicka *Introduction* exists in the corpus.
- Philosophy of religion (2026-10-18): book maps for 020 (Eckel et al., *The Future of the Philosophy of Religion* — not a Cahn anthology as briefed) and 027 (Howard-Snyder, *Evidential Argument from Evil*, all 16 papers) plus 7 entries (evidential & logical problems of evil, ontological & cosmological arguments, faith/acceptance/hope, religious diversity & salvation, the future of the field); teleological argument blocked — its only lecture has no transcript.
- Philosophy of language (2026-10-18): built from book 031 — which proved to be VanPatten & Lee's *SLA/FLL* (1990), not Bauer et al.'s *Language Matters* — book map plus 4 entries (second/foreign classification, communicative competence, language-as-resource, and a lecture-led names/descriptions/reference); identity and linguistic-relativity candidates honestly reported as unsupported by the sources.
- Philosophy of science & history (2026-10-18): book 011 (Fodor & Piattelli-Palmarini) fully read and mapped, yielding entries on selection-for/adaptationism and historical explanation as narrative — but book 010's folder contains Dolphin's *Teaching Geology Using HPS* instead of Day's *Philosophy of History*, so Day-based entries await a correct extraction.
- History of philosophy & general (2026-10-18): 6 book maps (001 reconstruction-only; 039 found to contain a Deleuze film book instead of Feinberg & Coleman) and 4 entries (Sartre, Camus/Sisyphus, Nietzsche master/slave morality, postmodernism's applied turn); philosophy-of-law subfield deferred pending re-extraction of the real 039.
- Assembly (2026-10-18): 53 entries and 26/26 book maps in place; `lectures-index.md` maps all 817 transcripts (129 assigned, 79 front-door assignments, 686 unassigned, 2 unusable); `DATA_QUALITY.md` audits every extraction problem per book; `index.md` is the KB home. The two 012 maps were renamed to `…-anthology-3rd-ed.md` / `…-anthology-2nd-ed.md` (the "kymlicka" filename was a brief artefact). Publishing (knowledge-base/ + site) remains a separate, later step.
- Published (2026-10-19): the KB is live on the site — public set (index, 53 entries, 26 book maps, lectures-index, DATA_QUALITY) copied to `knowledge-base/readings-kb/` with site-relative links fixed and verified (300 relative links, 0 unresolved), a copperplate-engraving cover generated, and the KB registered in `content.json` in the Knowledge Base section (slug `readings-kb`, no `kind` field — a normal markdown document). PLAN.md, `pilot/`, and `translations/` stay in sratchpad only (translations are working sources, never published).
