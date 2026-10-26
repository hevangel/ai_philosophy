# Readings Knowledge Base

*A public knowledge base built from the `data/philosophy_readings` corpus — philosophy textbooks, anthologies, and primary texts, plus the Carneades lecture series. Design: `PLAN.md`. Shape approved via the epistemology pilot (kept in `pilot/`); this is the scaled build, staged for the publish step.*

**Structure.** The spine is **Subfield → Problem → Positions → Arguments**. Each problem entry follows the locked template: the question in plain terms → the 90-second version (distilled from the Carneades lecture(s) — the entry's front door — or, where no lecture exists, from the textbook and marked as such) → positions with faithful P1/P2/∴C reconstructions labelled by source → thought experiments → source ladder → where the debate stands (unsettled stays unsettled) → connections → sources actually read. The **book layer** ([`book-maps/`](book-maps/001-sophies-world.md)) maps every extracted book chapter by chapter; the **lecture layer** ([`lectures-index.md`](lectures-index.md)) maps all 817 transcripts to entries or marks them unassigned. Extraction problems are audited in [`DATA_QUALITY.md`](DATA_QUALITY.md) — read it before trusting the catalogue: **8 of the 26 folders contain a different book than their name claims.**

## Coverage at a glance

- **53 problem entries** across 9 subfields (philosophy of law could not be built — see below)
- **26 of 26 book maps** complete
- **Lectures:** 129 of 817 assigned to entries (79 front-door assignments); 686 unassigned; 2 unusable (no transcript)
- **Book 002 (李天命的思考藝術）:** full TOC + 7 chapters translated into English (`translations/002/`); remainder listed there, not silently skipped

## Subfields and problems

### Epistemology — [`entries/epistemology/`](entries/epistemology/external-world-skepticism.md)
- [External-world skepticism](entries/epistemology/external-world-skepticism.md) — skeptical scenarios, the cogito, Berkeley, Russell's instinctive-belief realism, Hume's mitigated scepticism *(pilot)*
- [Gettier and the analysis of knowledge](entries/epistemology/gettier-and-the-analysis-of-knowledge.md) — the tripartite analysis, Gettier's counterexample, Russell's earlier false-premise cases *(pilot)*
- [The problem of induction](entries/epistemology/problem-of-induction.md) — Hume's circle, Russell's a priori principle, Goodman's new riddle *(pilot)*
- [Perception and sense-data](entries/epistemology/perception-and-sense-data.md) — Locke's qualities, Berkeley's collapse, Russell's sense-data, Reid's sign-reading
- [Knowledge by acquaintance and description](entries/epistemology/knowledge-by-acquaintance-and-description.md) — Russell ch. V: the acquaintance inventory, descriptions, the principle of acquaintance
- [A priori knowledge](entries/epistemology/a-priori-knowledge.md) — innateness, Kant's synthetic a priori, Russell's split verdict, Kripke's contingent a priori
- [Truth and falsehood](entries/epistemology/truth-and-falsehood.md) — Russell's requisites, coherence as criterion, the multiple-relation theory
- [Memory and knowledge of the past](entries/epistemology/memory-and-knowledge-of-the-past.md) — Locke's annexed pastness, Russell's acquaintance with the past, Reid's original principle
- [Knowledge by testimony](entries/epistemology/knowledge-by-testimony.md) — Hume's experience-derived trust vs Reid's pre-experiential credulity

### Logic & critical thinking — [`entries/logic-and-critical-thinking/`](entries/logic-and-critical-thinking/arguments-validity-and-soundness.md)
- [Arguments, validity, and soundness](entries/logic-and-critical-thinking/arguments-validity-and-soundness.md) — with Li Tianming's validity condition and the lectures' own caveat on strong/cogent
- [Semantic analysis and clarity of meaning](entries/logic-and-critical-thinking/semantic-analysis-and-clarity-of-meaning.md) — Li's 語理分析 programme, vagueness vs ambiguity, the heap
- [Fallacies and sophistry](entries/logic-and-critical-thinking/fallacies-and-sophistry.md) — Li's taxonomy (chs. 11–13) + the Fallacy February lectures
- [Closed systems and pseudo-explanation](entries/logic-and-critical-thinking/closed-systems-and-pseudo-explanation.md) — Li on 心魔 and disconfirmability, kept distinct from Popper
- [Gödel, self-reference, and formal systems](entries/logic-and-critical-thinking/godel-self-reference-and-formal-systems.md) — GEB chs. I–XV as read; Lucas vs Hofstadter left open where the text leaves it

### Metaphysics — [`entries/metaphysics/`](entries/metaphysics/natural-kinds.md)
*Built from the book actually in folder 013: Beebee & Sabbarton-Leary (eds.),* The Semantics and Metaphysics of Natural Kinds.
- [Natural kinds](entries/metaphysics/natural-kinds.md) — Ellis's criteria, Boyd's HPC kinds, Quine on similarity
- [Rigidity and natural kind terms](entries/metaphysics/rigidity-and-natural-kind-terms.md) — Besson, Martí & Martínez, Wikforss, Noonan
- [Essences and theoretical identities](entries/metaphysics/essences-and-theoretical-identities.md) — Kripke–Putnam, LaPorte's stipulation, Bird, Hendry
- [The necessary a posteriori](entries/metaphysics/the-necessary-a-posteriori.md) — Kripke's category and the Ellis "abuse" verdict
- [Classification and the hierarchy thesis](entries/metaphysics/classification-and-the-hierarchy-thesis.md) — Tobin on crosscutting kinds
- [Causal necessity and Hume's Dictum](entries/metaphysics/causal-necessity-and-humes-dictum.md) — Wilson's conditional; Schaffer's criterion tested

### Ethics & metaethics — [`entries/ethics-and-metaethics/`](entries/ethics-and-metaethics/moral-objectivity-and-realism.md)
- [Moral objectivity and realism](entries/ethics-and-metaethics/moral-objectivity-and-realism.md) — Jacobs's seven objectivities; Mackie's error theory
- [Moral relativism and subjectivism](entries/ethics-and-metaethics/moral-relativism-and-subjectivism.md)
- [Emotivism and expressivism](entries/ethics-and-metaethics/emotivism-and-expressivism.md) — Ayer, Blackburn, Foot
- [Naturalism and the open question](entries/ethics-and-metaethics/naturalism-and-the-open-question.md) — Moore, reconstructed naturalism, Harman vs Sturgeon/Railton
- [God and morality](entries/ethics-and-metaethics/god-and-morality.md) — the Euthyphro as 028 and the lectures stage it
- [Moral motivation](entries/ethics-and-metaethics/moral-motivation.md) — Kant/Hume/Aristotle, Korsgaard, Mackie
- [Self-interest and egoism](entries/ethics-and-metaethics/self-interest-and-egoism.md) — the egoism equivocation; Hobbes to Plato's reversal
- [Moral luck](entries/ethics-and-metaethics/moral-luck.md) — 028's own cases: the careless pair, the failed rescue, unacted intentions
- [Are moral considerations overriding?](entries/ethics-and-metaethics/are-moral-considerations-overriding.md) — Williams, Wolf's moral saints
- [Forms of moral theory](entries/ethics-and-metaethics/forms-of-moral-theory.md) — the five forms as positions; the trolley (lecture-only, labelled)
- [Bullshit vs lying](entries/ethics-and-metaethics/bullshit-vs-lying.md) — Frankfurt as presented by book 005's essayists (his own text is not in the corpus)

### Political philosophy — [`entries/political-philosophy/`](entries/political-philosophy/the-harm-principle-and-freedom-of-expression.md)
- [The harm principle and freedom of expression](entries/political-philosophy/the-harm-principle-and-freedom-of-expression.md) — Mill's four grounds and the corn-dealer limit
- [Distributive justice: entitlement vs pattern](entries/political-philosophy/distributive-justice-entitlement-vs-pattern.md) — Nozick ch. 7, O'Neill's objection, Rawls's **1958 paper** (not *A Theory of Justice*)
- [The minimal state](entries/political-philosophy/the-minimal-state.md) — Nozick's invisible-hand derivation and its stated limits
- [Arrow's theorem and the possibility of social choice](entries/political-philosophy/arrows-theorem-and-the-possibility-of-social-choice.md) — both condition-bookkeepings kept distinct; Sen and Maskin replies
- [Democracy and the voting paradoxes](entries/political-philosophy/democracy-and-the-voting-paradoxes.md) — Dahl's criteria, Downs's paradox and its five replies

### Philosophy of religion — [`entries/philosophy-of-religion/`](entries/philosophy-of-religion/evidential-argument-from-evil.md)
- [The evidential argument from evil](entries/philosophy-of-religion/evidential-argument-from-evil.md) — Rowe, Draper, and the replies, from book 027's papers; left unsettled as the authors leave it
- [The logical problem of evil](entries/philosophy-of-religion/logical-problem-of-evil.md) — Mackie's collapse, the free will defense
- [The ontological argument](entries/philosophy-of-religion/ontological-argument.md) — lecture family (seven arguments + objections); the books barely stage it, and the entry says so
- [The cosmological argument](entries/philosophy-of-religion/cosmological-argument.md) — Aquinas, kalām, Russell/Hume/Kant objections, Bhāviveka's anti-creator arguments (020)
- [Faith, acceptance, and hope](entries/philosophy-of-religion/faith-acceptance-and-hope.md) — Chignell's Ladder of Liturgical Sincerity; Lamberth on James; Pascal's wager
- [Religious diversity and salvation](entries/philosophy-of-religion/religious-diversity-and-salvation.md) — exclusivism / inclusivism / pluralism and their formal objections
- [The future of philosophy of religion](entries/philosophy-of-religion/the-future-of-philosophy-of-religion.md) — the meta-entry book 020 actually supports

### Philosophy of language — [`entries/philosophy-of-language/`](entries/philosophy-of-language/second-or-foreign-language-contexts.md)
*Built from the book actually in folder 031: VanPatten & Lee (eds.),* Second Language Acquisition / Foreign Language Learning *(1990).*
- [Second or foreign language? Contexts of acquisition](entries/philosophy-of-language/second-or-foreign-language-contexts.md) — Stern, Berns, Gass, Schinke-Llano, the editors' synthesis
- [Communicative competence and pragmatic failure](entries/philosophy-of-language/communicative-competence-and-pragmatic-failure.md) — Thomas on pragmatic failure; speech-act lectures as front door
- [Language as a resource: conservation and policy](entries/philosophy-of-language/language-as-a-resource-conservation-and-policy.md) — Campbell & Lindholm against the subtractive default
- [Names, descriptions, and reference](entries/philosophy-of-language/names-descriptions-and-reference.md) — **lecture-led** (Russell, Kripke, indexicals); the entry declares the book's non-support plainly

### Philosophy of science & history — [`entries/philosophy-of-science-and-history/`](entries/philosophy-of-science-and-history/selection-for-and-the-critique-of-adaptationism.md)
- [Selection-for and the critique of adaptationism](entries/philosophy-of-science-and-history/selection-for-and-the-critique-of-adaptationism.md) — Fodor & Piattelli-Palmarini at stated strength; no adaptationist-side text exists in the corpus
- [Historical explanation and narrative](entries/philosophy-of-science-and-history/historical-explanation-and-narrative.md) — built from 011 chs. 7–9 (book 010 is not Day — see DATA_QUALITY)

### History of philosophy & general — [`entries/history-of-philosophy-and-general/`](entries/history-of-philosophy-and-general/existence-precedes-essence.md)
- [Existence precedes essence](entries/history-of-philosophy-and-general/existence-precedes-essence.md) — Sartre via Kaufmann's anthology (018)
- [The absurd and Sisyphus](entries/history-of-philosophy-and-general/the-absurd-and-sisyphus.md) — Camus's concluding chapter only; the gap is declared in the entry
- [Master and slave morality](entries/history-of-philosophy-and-general/master-and-slave-morality.md) — *Beyond Good and Evil* §§186–262, with Nietzsche's own mixture caveat
- [Postmodernism and its applied turn](entries/history-of-philosophy-and-general/postmodernism-and-its-applied-turn.md) — Carneades' pluralist definition vs Pluckrose & Lindsay's genealogy, kept as separate stagings

### Philosophy of law — **not built (shortfall)**
Folder 039 contains a Deleuze film-studies volume, not Feinberg & Coleman, and the corpus's single law lecture cannot carry a subfield without writing from general knowledge. Deferred pending re-extraction of the real 039. (See [`DATA_QUALITY.md`](DATA_QUALITY.md).)

## Books — the book layer

Catalogue name as in the corpus; "actually" notes where the folder's contents differ. Every map: [`book-maps/`](book-maps/001-sophies-world.md).

| № | Book (as catalogued) | Map |
|---|---|---|
| 001 | Gaarder, *Sophie's World* — **no text in corpus; TOC reconstruction only** | [001](book-maps/001-sophies-world.md) |
| 002 | 李天命，《思考藝術》— folder interleaved with a Simpsons volume | [002](book-maps/002-the-art-of-thinking.md) |
| 003 | Pluckrose & Lindsay, *Cynical Theories* | [003](book-maps/003-cynical-theories.md) |
| 004 | "On Manners" — **actually a novel, *The Pannell Witch*** | [004](book-maps/004-on-manners.md) |
| 005 | *Bullshit and Philosophy* (Frankfurt's own essay absent) | [005](book-maps/005-bullshit-and-philosophy.md) |
| 006 | Russell, *The Problems of Philosophy* | [006](book-maps/006-problems-of-philosophy.md) |
| 007 | Moser & vander Nat, *Human Knowledge* — reconstruction; 25/39 stubs | [007](book-maps/007-human-knowledge.md) |
| 008 | Hofstadter, *Gödel, Escher, Bach* — stratified extraction | [008](book-maps/008-godel-escher-bach.md) |
| 010 | "Philosophy of History" — **actually Dolphin, *Teaching Geology Using HPS*** | [010](book-maps/010-the-philosophy-of-history.md) |
| 011 | Fodor & Piattelli-Palmarini, *What Darwin Got Wrong* | [011](book-maps/011-what-darwin-got-wrong.md) |
| 012 | Goodin & Pettit (eds.), *Contemporary Political Philosophy: An Anthology*, **3rd ed.** (catalogued as Kymlicka's *Introduction*, which is absent) | [012 · 3rd ed.](book-maps/012-contemporary-political-philosophy-anthology-3rd-ed.md) |
| 012 | The same anthology, **2nd ed.** — reconstruction, 46/48 stubs | [012 · 2nd ed.](book-maps/012-contemporary-political-philosophy-anthology-2nd-ed.md) |
| 013 | "Taylor, *Metaphysics*" — **actually Beebee & Sabbarton-Leary (eds.), *The Semantics and Metaphysics of Natural Kinds*** | [013](book-maps/013-metaphysics.md) |
| 018 | "Solomon, *Existentialism*" — **actually Kaufmann (ed.), *Existentialism from Dostoevsky to Sartre*** | [018](book-maps/018-existentialism.md) |
| 019 | Nietzsche, *Beyond Good and Evil* (Kaufmann tr.) | [019](book-maps/019-beyond-good-and-evil.md) |
| 020 | "Cahn (ed.), *Philosophy of Religion*" — **actually Eckel et al. (eds.), *The Future of the Philosophy of Religion*** | [020](book-maps/020-philosophy-of-religion.md) |
| 021 | Nozick, *Anarchy, State, and Utopia* | [021](book-maps/021-anarchy-state-and-utopia.md) |
| 024 | Mill, *On Liberty* (+ *The Subjection of Women* in the same folder) | [024](book-maps/024-on-liberty.md) |
| 025 | Brown, *The One-Minute Philosopher* — **no text in corpus** | [025](book-maps/025-the-one-minute-philosopher.md) |
| 026 | *Philosophy: A Beginner's Guide to the Ideas of 100 Great Thinkers* | [026](book-maps/026-philosophy-100-great-thinkers.md) |
| 027 | Howard-Snyder (ed.), *The Evidential Argument from Evil* | [027](book-maps/027-the-evidential-argument-from-evil.md) |
| 028 | Jacobs, *Dimensions of Moral Theory* | [028](book-maps/028-dimensions-of-moral-theory.md) |
| 031 | "Bauer et al., *Language Matters*" — **actually VanPatten & Lee (eds.), *SLA/FLL* (1990)** | [031](book-maps/031-language-matters.md) |
| 036 | Maskin & Sen, *The Arrow Impossibility Theorem* | [036](book-maps/036-the-arrow-impossibility-theorem.md) |
| 037 | Arrow, *Social Choice and Individual Values* | [037](book-maps/037-social-choice-and-individual-values.md) |
| 039 | "Feinberg & Coleman, *Philosophy of Law*" — **actually *Gilles Deleuze and Film Criticism*** | [039](book-maps/039-philosophy-of-law.md) |

## Known shortfalls (recorded, not padded)

- **Philosophy of law:** not built (039 is the wrong book).
- **Missing books:** Taylor's *Metaphysics*, Day's *Philosophy of History*, Kymlicka's *Introduction*, Bauer et al.'s *Language Matters*, Cahn's religion anthology, Feinberg & Coleman's *Philosophy of Law* — none exists in the corpus; their problem areas (free will, personal identity, time, historical knowledge, language & identity, linguistic relativity, jurisprudence) have lectures standing by in the index, unassigned.
- **Textless books:** 001 and 025 have no extractable text at all.
- **Book 002 translation remainder:** chs. 11–12 were read in the Chinese and used (fallacies entry) but their translations are still outstanding — the entry, map, and translation README all flag this; chs. 5, 6, 14–21 and the ch. 13 note tail (27–38) are untranslated and unused.
- **Book 007's contemporary sections** are stubs, capping epistemology's modern coverage; Gettier's paper and Quine's "Two Dogmas" are corrupted files.
- **Design argument:** unbuildable for now — its only lecture has no transcript.
