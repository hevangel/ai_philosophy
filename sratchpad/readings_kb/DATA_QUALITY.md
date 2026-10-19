# Data quality — readings corpus extraction audit

*Compiled 2026-10-18 from the epistemology pilot and the nine subfield build reports. Every problem found while actually reading the corpus for the KB, per book. The builders worked from what genuinely exists; nothing below was papered over.*

## Headline: the catalogue itself is wrong about 8 of 26 books

The folder names (and the original textbook list) misidentify these books. In each case the extraction is of a real book — just not the catalogued one. All KB book maps declare the true identity at their head.

| № | Catalogued as | Actually is |
|---|---|---|
| 004 | *On Manners* (etiquette anthology) | Melissa Manners, *The Pannell Witch* (2022) — a self-published historical novel; zero philosophy content |
| 010 | Day, *The Philosophy of History: An Introduction* | Dolphin, *Teaching Geology Using the History and Philosophy of Science* (Springer, 2024), complete |
| 012 (folder 1) | Kymlicka, *Contemporary Political Philosophy: An Introduction* | Goodin & Pettit (eds.), *Contemporary Political Philosophy: An Anthology*, **3rd ed. (2019)**, full text. No Kymlicka *Introduction* exists in the corpus |
| 013 | Taylor, *Metaphysics* | Beebee & Sabbarton-Leary (eds.), *The Semantics and Metaphysics of Natural Kinds* (Routledge, 2010) |
| 018 | Solomon, *Existentialism* | Walter Kaufmann (ed.), *Existentialism from Dostoevsky to Sartre* (authorship correction) |
| 020 | Cahn (ed.), *Philosophy of Religion* anthology | Eckel, Speight & DuJardin (eds.), *The Future of the Philosophy of Religion* (Springer, 2021) |
| 031 | Bauer, Holmes & Warren, *Language Matters* | VanPatten & Lee (eds.), *Second Language Acquisition / Foreign Language Learning* (Multilingual Matters 58, 1990) |
| 039 | Feinberg & Coleman, *Philosophy of Law* | *Gilles Deleuze and Film Criticism* (eds. Lash & Law, Palgrave, 2023) |

Downstream consequences: no philosophy-of-law subfield could be built (039); no Day-based philosophy-of-history entries (010); no Taylor-based free-will / personal-identity / time entries — the matching Carneades lectures stand unassigned in `lectures-index.md`; no manners/etiquette entry (004); the religion slice has no classical anthology (020).

## Per-book detail

- **001 — Sophie's World.** No book text at all: only `_meta.json` (provenance "reconstructed", no epub/PDF found) and a 35-chapter TOC compiled from Wikipedia/LitCharts. Orientation/source-ladder use only.
- **002 — 李天命的思考藝術.** Folder interleaved with a different book: 38 of 59 files are *The Simpsons and Philosophy*; only 21 files are Li's Chinese text (~200k chars). Two formulas lost in ch. 10 §IV(B) (angle-bracket fallbacks kept and flagged in the translation); one Robbins formula lost in ch. 9's notes (flagged, not invented). TOC source is the folder's ch04 file; page numbers lost except one (p. 99).
- **003 — Cynical Theories.** Extraction complete and clean. Limitation is stance (advocacy), labelled in map and entry.
- **004 — "On Manners".** See headline table. 51 files, ~72,000 words, all inspected; "philosoph-" occurs 3×, all incidental.
- **005 — Bullshit and Philosophy.** File titles name each chapter's *last* section heading, not the chapter (e.g. file "ch07 — Bullshit and Truth" is Chapter 1). ch01/ch02 are empty stubs; ch28 is collected endnotes; ch29's summary misspells "Frankfort". Frankfurt's *On Bullshit* itself is **not in the corpus** — the bullshit entry uses Frankfurt only as presented by the volume's essayists, and says so.
- **006 — Russell, Problems of Philosophy.** Each chapter split into a near-empty title stub + a content file under a generic "Vook Classics" name; the Preface is counted as chapter 1, shifting all numbers +1 against the book's own numbering. ch36 empty; ch35 publisher credits. Text otherwise complete.
- **007 — Human Knowledge.** A reconstruction, not the book: 12 of 39 readings usable in full/part, 25 citation stubs, editors' General Introduction absent. Specific losses: ch06 (Descartes) is a failed fetch — 4 KB of Wikisource navigation boilerplate, no *Meditations* text; ch18 (Quine, "Two Dogmas") and ch20 (Gettier) have corrupted bodies (header intact, ~2.5 KB binary garbage; both from ditext.com) — the Gettier loss is the corpus's most consequential single gap; ch05 (Aquinas) is prologue/contents only; the whole A Priori section (chs. 23–25) is stubs. Several "selections" are entire works: Locke's *Essay* (ch7), Leibniz's *New Essays* (ch8), James's essay collection (ch13), the Aristotle volume (ch2), and ch14 = the entire *Problems of Philosophy*, duplicating book 006. OCR faults inside usable text: Reid (ch11) VI §24's key credulity sentence is interleaved with unrelated page matter mid-sentence; Kant *Prolegomena* (ch12) §2 has an apparent misprint ("analytical" where the argument requires "synthetical"); Leibniz (ch8) OCR misreadings are scattered but the Preface argument is legible.
- **008 — Gödel, Escher, Bach.** Stratified extraction: ch01–15 files are TOC fragments only; usable text begins at ch18 (= Ch. I); ch21 contains Chs. IV *and* V; ch44 duplicates ch35; ch37–43 are endnotes; heavy OCR noise in formulas.
- **010 — "Philosophy of History".** See headline table (Dolphin, complete, ~124k words, 12 files). Extraction quality of the Dolphin text is good; nothing of Day exists anywhere in the corpus.
- **011 — What Darwin Got Wrong.** Complete (Terms + chs. 1–9). File titles are internal section headings rather than chapter titles (recoverable from the TOC files); two non-identical TOC files; part dividers counted as chapters.
- **012 — Anthology, 3rd ed. (folder "012 - Contemporary Political Philosophy").** Full text, 49 chapters in 9 parts. File titles are epub-spine labels and unreliable — files titled "References" carry the next chapter's body; chapters split across files. Ch. 45 (Luban) suspiciously short (14k chars) — possibly excerpted.
- **012 — Anthology, 2nd ed. (folder "… - An Anthology").** A reconstruction: 46 of 48 readings are citation stubs; only Thomson (ch21) and Berlin (ch24) are full text. `toc.md` is a sourced reconstruction (LOC/IA/Google Books, 2026-10-04); its 1st-edition list is partly inferred.
- **013 — "Metaphysics".** See headline table. Extraction itself excellent: the Contents page (file ch06) lists all 12 papers + authors; 12/12 papers full text (~5,800–11,600 words each); ch01–ch07 are front-matter fragments; ch20 contributors; ch21 index has some garbled diacritics. PLAN.md's earlier note ("every chapter mis-titled") was the same fact seen from the wrong side: the shared title is the volume's real title.
- **018 — "Existentialism".** See headline table (Kaufmann ed.). Camus present only as the concluding chapter of *The Myth of Sisyphus* (the absurd's definition and the suicide argument are absent — the entry declares this); Dostoevsky is Part One only; two files are Pickle Partners publisher matter.
- **019 — Beyond Good and Evil.** Full text, all 296 §§ (Kaufmann tr., Vintage 1989). Only defects: generic identical filenames and part-title stubs.
- **020 — "Philosophy of Religion".** See headline table. Extraction clean: 18 files, titles match the printed contents, all chapters full text.
- **021 — Anarchy, State, and Utopia.** Ch. 7 split across files ch18+ch19; ch19 opens mid-argument with no heading. All 26 files share one title — cite by internal chapter heading.
- **024 — On Liberty.** The folder holds two works from the combined 1879 edition: *On Liberty* (files ch03–ch07) plus *The Subjection of Women* (files ch09–ch12); the *Subjection* files have bare colliding titles ("CHAPTER I", …).
- **025 — The One-Minute Philosopher.** No text at all: only `_meta.json` + a MARC-505-reconstructed TOC (owner instruction 2026-10-04; no obtainable ebook, final verdict 2026-10-13). Title-level coverage only; no entry could be built from it.
- **026 — 100 Great Thinkers.** Clean text but popular level: reports positions, rarely argues them. Contents misspells Thales of "Melitus" and Charles Sanders "Pierce"; its Lyotard-1978 dating is the book's claim, flagged in the map.
- **027 — The Evidential Argument from Evil.** All 29 files carry the identical book title; chapter identity recoverable from in-text author headings + the contents file (ch07), which agree. Files ch01–ch06 and ch10 are front-matter fragments (17–199 words). All 16 papers otherwise full text — no stubs or corruption.
- **028 — Dimensions of Moral Theory.** Text complete (~73,135 words) but chopped into 3 mega-chunks whose file titles name a section near each chunk's *end*; both seams verified continuous, no text lost. ch01 is cover only; ch05 a duplicated TOC stub.
- **031 — "Language Matters".** See headline table. Extraction is page-per-file (284 files); 4 single pages missing — pp. 12, 72, 184 (blank/divider) and front-matter p. viii — no chapter content lost; no stubs or corruption.
- **036 — The Arrow Impossibility Theorem.** Uniform file titles (as with 021/037) — cite by internal chapter heading, never filename alone.
- **037 — Social Choice and Individual Values.** Main text intact (files ch05–ch19), but ~180 files (ch20–ch201) are footnotes shattered into separate fragments. Theorem 2's statement in file ch14 contains a misprint ("Conditions 2 and 8"); entries cross-checked it against the chapter's proof summary and interpretation passage.
- **039 — "Philosophy of Law".** See headline table. Extraction titles were generated from the folder name, hiding the mismatch; Part III chapter numbers are scrambled in the titles.

## Lectures (global)

- Auto-captions are unreliable as text throughout: Goodman's "grue" rendered "green"/"gru"/"Grün"; Frege as "Fraga"; Quine as "Quin"; *salva veritate* garbled. All entries distill, never quote.
- Two lectures have **no transcript at all**: `gGO8A9wiI5o` (Teleological Arguments From Analogy) — which blocks any design-argument entry — and `VsmQdpD21iE` (What is Expected Consequentialism, 18 words).
- The Gettier lecture mis-titles Gettier's paper ("Is Knowledge a Grounded True Belief?").
- The "Experience Machine" lecture actually presents Vonnegut's "UFO machine" against hedonism and flags itself as not a skeptical scenario; used only as a series neighbour.
- The Moore's Open Question lecture outruns its source (concludes goodness "is not a property / does not exist" via a Russell spin; Moore and Jacobs hold good is real and indefinable) — flagged in the entry.
- The *Can Theists Be Moral* lecture's title promises 5 arguments; it covers 4 plus a general objection — noted in the entry.
