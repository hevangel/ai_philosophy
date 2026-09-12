"""Extract philosophers & philosophy concepts per chapter; build index maps.

Outputs:
  philosophy_pop_culture/analysis/<book>/index.md   per-book chapter map
  sratchpad/libgen_batch/chapter_index.json         master chapter records
  sratchpad/libgen_batch/aggregate.json             cross-book rankings
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

SRC = Path(r"B:\ai_philosophy\philosophy_pop_culture")
MD_ROOT = SRC / "markdown"
AN_ROOT = SRC / "analysis"
BATCH = Path(r"B:\ai_philosophy\sratchpad\libgen_batch")

# ---------------------------------------------------------------------------
# Lexicons: name -> list of regex variants (case-insensitive unless noted)
# ---------------------------------------------------------------------------
PHILOSOPHERS = {
    "Plato": [r"\bplatonic\b", r"\bplato\b", r"\ballegory of the cave\b", r"\btheory of forms\b", r"\bplatonic forms?\b"],
    "Aristotle": [r"\baristoteli?an\b", r"\baristotle\b", r"\beudaimoni[a]\b", r"\bgolden mean\b"],
    "Socrates": [r"\bsocratic\b", r"\bsocrates\b", r"\bsocratic method\b"],
    "Heraclitus": [r"\bheraclitus\b"],
    "Epicurus": [r"\bepicurean\b", r"\bepicurus\b"],
    "Diogenes": [r"\bdiogenes\b"],
    "Zeno of Citium": [r"\bzeno of citium\b", r"\bstoic (?:sage|philosophy|tradition)\b"],
    "Seneca": [r"\bseneca\b"],
    "Marcus Aurelius": [r"\bmarcus aurelius\b"],
    "Epictetus": [r"\bepictetus\b"],
    "St. Augustine": [r"\baugustine\b", r"\bconfessions of augustine\b"],
    "Thomas Aquinas": [r"\baquinas\b", r"\bthomistic\b", r"\bnatural law theory\b"],
    "William of Ockham": [r"\boccam'?s razor\b", r"\bockham\b"],
    "Descartes": [r"\bdescartes\b", r"\bcartesian\b", r"\bcogito\b", r"\bevil demon\b"],
    "Spinoza": [r"\bspinoza\b", r"\bspinozist\b"],
    "Leibniz": [r"\bleibniz\b", r"\bmonads?\b", r"\bbest of all possible worlds\b"],
    "Locke": [r"\bjohn locke\b", r"\blocke(?:an)?\b", r"\btabula rasa\b"],
    "Berkeley": [r"\bbishop berkeley\b", r"\bgeorge berkeley\b", r"\bberkeleyan idealism\b"],
    "Hume": [r"\bhumean\b", r"\bdavid hume\b", r"\bhume\b"],
    "Kant": [r"\bkantian\b", r"\bimmanuel kant\b", r"\bkant\b", r"\bcategorical imperative\b"],
    "Rousseau": [r"\brousseau\b"],
    "Hobbes": [r"\bhobbes(?:ian)?\b", r"\bleviathan\b", r"\bstate of nature\b"],
    "Bentham": [r"\bbentham\b", r"\bpanopticon\b"],
    "J.S. Mill": [r"\bjohn stuart mill\b", r"\bjs mill\b", r"\bmill'?s harm principle\b"],
    "Schopenhauer": [r"\bschopenhauer\b", r"\bwill to live\b"],
    "Kierkegaard": [r"\bkierkegaard\b", r"\bleap of faith\b"],
    "Hegel": [r"\bhegel(?:ian)?\b", r"\bmaster[-/ ]{0,3}slave\b", r"\bgeist\b"],
    "Marx": [r"\bmarx(?:is[mt]|ian)?\b", r"\bcommodity fetishism\b", r"\bclass struggle\b", r"\bmeans of production\b"],
    "Nietzsche": [r"\bnietzsche(?:an)?\b", r"\bwill to power\b", r"\bübermensch\b", r"\boverman\b", r"\beternal recurrence\b", r"\bamor fati\b", r"\bgenealogy of morals\b"],
    "William James": [r"\bwilliam james\b", r"\bpragmatis(?:m|t)\b"],
    "Dewey": [r"\bjohn dewey\b", r"\bdeweyan\b"],
    "Wittgenstein": [r"\bwittgenstein(?:ian)?\b", r"\blanguage game\b", r"\bfamily resemblance\b"],
    "Heidegger": [r"\bheidegger(?:ian)?\b", r"\bdasein\b", r"\bbeing-toward-death\b", r"\bthrownness\b", r"\bthey-self\b"],
    "Sartre": [r"\bsartrean\b", r"\bsartre\b", r"\bbad faith\b", r"\bexistence precedes essence\b"],
    "Camus": [r"\bcamus\b", r"\babsurd hero\b", r"\bmyth of sisyphus\b"],
    "de Beauvoir": [r"\bbeauvoir\b"],
    "Merleau-Ponty": [r"\bmerleau[- ]ponty\b"],
    "Foucault": [r"\bfoucault\b", r"\bfoucauldian\b", r"\bpanopticism\b", r"\bdisciplinary power\b", r"\bbiopower\b"],
    "Derrida": [r"\bderrida\b", r"\bdeconstruction\b", r"\bdiff[eé]rance\b", r"\blogocentrism\b"],
    "Baudrillard": [r"\bbaudrillard\b", r"\bsimulacr(?:a|um)\b", r"\bhyperrealit(?:y|ies)\b"],
    "Deleuze": [r"\bdeleuze\b", r"\brhizome\b", r"\bbecoming-animal\b"],
    "Barthes": [r"\bbarthes\b", r"\bdeath of the author\b", r"\bmythologies\b"],
    "Lacan": [r"\blacan(?:ian)?\b", r"\bbig other\b", r"\bjouissance\b", r"\bobjet petit a\b"],
    "Levinas": [r"\blevinas\b", r"\bthe face of the other\b"],
    "Arendt": [r"\barenndt\b", r"\bbanality of evil\b"],
    "Rawls": [r"\brawls(?:ian)?\b", r"\bveil of ignorance\b", r"\boriginal position\b"],
    "Nozick": [r"\bnozick\b", r"\bexperience machine\b"],
    "Habermas": [r"\bhabermas(?:ian)?\b", r"\bpublic sphere\b", r"\bdiscourse ethics\b"],
    "Gadamer": [r"\bgadamer\b", r"\bfusion of horizons\b"],
    "Ricoeur": [r"\bricoeur\b"],
    "Rorty": [r"\brorty\b"],
    "Nussbaum": [r"\bnussbaum\b"],
    "Peter Singer": [r"\bpeter singer\b", r"\bspeciesism\b"],
    "Thomas Nagel": [r"\bthomas nagel\b", r"\bnagel\b", r"\bwhat is it like to be a\b"],
    "Derek Parfit": [r"\bparfit\b", r"\bteletransporter\b"],
    "Saul Kripke": [r"\bkripke\b"],
    "Daniel Dennett": [r"\bdennett\b"],
    "John Searle": [r"\bsearle\b", r"\bchinese room\b"],
    "David Chalmers": [r"\bchalmers\b", r"\bhard problem\b"],
    "Hilary Putnam": [r"\bputnam\b", r"\bbrain in a vat\b"],
    "Martin Buber": [r"\bbuber\b", r"\bi[- ]thou\b"],
    "Ayn Rand": [r"\bayn rand\b", r"\bobjectivis(?:m|t)\b"],
    "Slavoj Žižek": [r"\bžižek\b", r"\bzizek\b"],
    "Judith Butler": [r"\bjudith butler\b", r"\bperformativity\b", r"\bgender performativ\b"],
    "Donna Haraway": [r"\bharaway\b", r"\bcyborg manifesto\b"],
    "Umberto Eco": [r"\bumberto eco\b", r"\beco\b"],
    "Han Byung-Chul": [r"\bbyung[- ]chul han\b", r"\bburnout society\b"],
    "Laozi": [r"\blaozi\b", r"\blao tzu\b", r"\btao te ching\b", r"\bdao de jing\b"],
    "Zhuangzi": [r"\bzhuangzi\b", r"\bchuang tzu\b"],
    "Confucius": [r"\bconfucius\b", r"\bconfucian\b"],
    "Sun Tzu": [r"\bsun tzu\b", r"\bart of war\b"],
    "Buddha": [r"\bthe buddha\b", r"\bbuddhis[mt]\b", r"\bfour noble truths\b", r"\bnoble eightfold path\b"],
    "Chesterton": [r"\bchesterton\b"],
    "Alasdair MacIntyre": [r"\bmacintyre\b", r"\bafter virtue\b"],
    "Bernard Williams": [r"\bbernard williams\b", r"\bmoral luck\b"],
    "Philippa Foot": [r"\bphilippa foot\b", r"\btrolley problem\b"],
}

CONCEPTS = {
    "categorical imperative": [r"\bcategorical imperative\b"],
    "veil of ignorance": [r"\bveil of ignorance\b"],
    "original position": [r"\boriginal position\b"],
    "utilitarianism": [r"\butilitarian", r"\bgreatest (?:good|happiness|number)\b"],
    "deontology": [r"\bdeontolog", r"\bduty ethics\b"],
    "consequentialism": [r"\bconsequential"],
    "virtue ethics": [r"\bvirtue ethics\b", r"\bvirtue theor"],
    "golden mean": [r"\bgolden mean\b", r"\baristotelian mean\b"],
    "social contract": [r"\bsocial contract\b"],
    "state of nature": [r"\bstate of nature\b"],
    "empiricism": [r"\bempiricis[mt]\b", r"\ba posteriori\b"],
    "rationalism": [r"\brationalis[mt]\b", r"\ba priori\b"],
    "idealism": [r"\bidealism\b", r"\bidealist\b"],
    "materialism": [r"\bmaterialis[mt]\b", r"\bphysicalism\b"],
    "mind-body dualism": [r"\bdualis[mt]\b", r"\bmind[- ]body problem\b", r"\bsubstance dualism\b"],
    "free will vs determinism": [r"\bfree will\b", r"\bdeterminis[mt]\b", r"\bcompatibilis[mt]\b", r"\bfatalis[mt]\b"],
    "personal identity": [r"\bpersonal identity\b", r"\bship of theseus\b", r"\bteletransport\w*\b", r"\bwhat makes me\b"],
    "ship of Theseus": [r"\bship of theseus\b", r"\btheseus'? ship\b"],
    "existentialism": [r"\bexistentialis[mt]\b", r"\bexistential\b"],
    "the absurd": [r"\bthe absurd\b", r"\babsurdism\b", r"\babsurd hero\b"],
    "authenticity": [r"\bauthenticit(?:y|ies)\b", r"\binauthentic\b"],
    "bad faith": [r"\bbad faith\b"],
    "nihilism": [r"\bnihilis[mt]\b"],
    "will to power": [r"\bwill to power\b"],
    "eternal recurrence": [r"\beternal recurrence\b"],
    "amor fati": [r"\bamor fati\b"],
    "Überman/overman": [r"\bübermensch\b", r"\boverman\b", r"\bubermensch\b"],
    "stoicism": [r"\bstoic(?:ism)?\b"],
    "hedonism": [r"\bhedonis[mt]\b"],
    "the cave allegory": [r"\bcave\b.{0,40}\bshadows?\b", r"\ballegory of the (?:cave|den)\b"],
    "form/matter": [r"\btheory of forms?\b", r"\bplatonic forms?\b"],
    "four causes": [r"\bfour causes\b"],
    "telos": [r"\btelos\b", r"\bteleolog"],
    "monad": [r"\bmonads?\b"],
    "simulation/simulacra": [r"\bsimulacr\w+\b", r"\bhyperreal\w*\b", r"\bsimulation hypothesis\b", r"\bzion\b.{0,30}simulation"],
    "panopticon/surveillance": [r"\bpanoptic\w*\b", r"\bsurveillan", r"\bdisciplinary power\b"],
    "deconstruction": [r"\bdeconstruct\w*\b"],
    "death of the author": [r"\bdeath of the author\b"],
    "hermeneutics": [r"\bhermeneutic\w*\b"],
    "phenomenology": [r"\bphenomenolog"],
    "embodiment": [r"\bembodiment\b", r"\bembodied\b"],
    "intentionality": [r"\bintentionality\b"],
    "qualia": [r"\bqualia\b"],
    "hard problem of consciousness": [r"\bhard problem\b"],
    "Chinese room": [r"\bchinese room\b"],
    "brain in a vat": [r"\bbrain[s]? in a vat\b", r"\bbots? in a vat\b"],
    "experience machine": [r"\bexperience machine\b"],
    "trolley problem": [r"\btrolley (?:problem|dilemma)\b"],
    "thought experiment": [r"\bthought experiment"],
    "moral luck": [r"\bmoral luck\b"],
    "ethics of care": [r"\bethics of care\b", r"\bcare ethics\b"],
    "moral relativism": [r"\brelativis[mt]\b"],
    "moral realism": [r"\bmoral realism\b", r"\bmoral realis[mt]\b"],
    "just war": [r"\bjust war\b"],
    "natural rights": [r"\bnatural rights?\b"],
    "autonomy": [r"\bautonom(?:y|ous)\b"],
    "dignity": [r"\bdignity\b"],
    "the Other": [r"\bothering\b", r"\bwholly other\b"],
    "pragmatism": [r"\bpragmatis(?:m|t)\b"],
    "falsifiability": [r"\bfalsifiab", r"\bpopperian\b"],
    "paradigm shift": [r"\bparadigm shift\b"],
    "Occam's razor": [r"\boccam'?s razor\b"],
    "Tao/wu wei": [r"\bwu wei\b", r"\bthe tao\b", r"\bthe dao\b"],
    "karma": [r"\bkarma\b"],
    "Zen": [r"\bzen\b"],
    "soul": [r"\bthe soul\b", r"\bimmortal soul\b"],
    "the good life": [r"\bthe good life\b"],
    "justice": [r"\bjustice\b"],
    "the examined life": [r"\bexamined life\b"],
    "know thyself": [r"\bknow thyself\b"],
    "grand narrative": [r"\bgrand narrative", r"\bmetanarrative\b"],
    "gender performativity": [r"\bperformativ"],
    "postmodernism": [r"\bpostmodern"],
    "alienation": [r"\balienat"],
    "utopia/dystopia": [r"\bdystopi", r"\butopi"],
    "Orwellian": [r"\borwellian\b", r"\bbig brother\b", r"\bthoughtcrime\b", r"\bdoublethink\b"],
    "collective intentionality": [r"\bcollective intentionality\b"],
    "moral panic": [r"\bmoral panic\b"],
    "the meaning of life": [r"\bmeaning of life\b"],
    "What would X do (virtue exemplars)": [r"\brole model", r"\bmoral exemplar"],
    "moral responsibility": [r"\bmoral responsibility\b"],
    "compassion": [r"\bcompassion\b"],
    "loyalty": [r"\bloyalt"],
    "friendship (philia)": [r"\bphilia\b", r"\bfriendship\b"],
    "love (eros/agape)": [r"\beros\b", r"\bagape\b", r"\bphilia\b"],
    "death & mortality": [r"\bmortalit", r"\bdeath\b"],
    "the sublime": [r"\bthe sublime\b"],
    "aesthetics": [r"\baesthetic"],
    "allegory": [r"\ballegor"],
    "metaphysics": [r"\bmetaphysic"],
    "epistemology": [r"\bepistemolog"],
    "ethics (general)": [r"\bethics\b", r"\bethical\b", r"\bmoralit"],
    "political philosophy": [r"\bpolitical philosoph", r"\bthe state\b", r"\bgovernance\b"],
}


def build_matchers(lexicon: dict) -> list[tuple[str, re.Pattern]]:
    out = []
    for canonical, variants in lexicon.items():
        parts = "|".join(f"(?:{v})" for v in variants)
        out.append((canonical, re.compile(parts, re.IGNORECASE)))
    return out


PH_MATCHERS = build_matchers(PHILOSOPHERS)
CO_MATCHERS = build_matchers(CONCEPTS)

WORD_RE = re.compile(r"[A-Za-z']+")


def excerpt_of(text: str) -> str:
    """First informative paragraph, trimmed to ~2 sentences / 320 chars."""
    # drop markdown headers, source lines, and blank separators
    lines = [ln for ln in text.splitlines()
             if ln.strip() and not ln.startswith(("#", "*", ">", "- "))]
    paras, cur = [], []
    for ln in lines:
        cur.append(ln.strip())
        if len(" ".join(cur).split()) > 60:
            paras.append(" ".join(cur))
            cur = []
    if cur:
        paras.append(" ".join(cur))
    if not paras:
        return ""
    p = max(paras, key=lambda x: 0)  # first paragraph
    for cand in paras:
        if len(cand.split()) >= 25:
            p = cand
            break
    sentences = re.split(r"(?<=[.!?])\s+", p)
    keep, length = [], 0
    for s in sentences:
        keep.append(s)
        length += len(s)
        if length > 260 and len(keep) >= 2:
            break
    out = " ".join(keep)
    return out[:400].rsplit(" ", 1)[0] + ("…" if len(out) > 400 else "")


def top_items(counter: Counter, n: int = 6) -> str:
    if not counter:
        return "—"
    return ", ".join(f"{k} ({v})" for k, v in counter.most_common(n) if v >= 1)


def analyze_book(book_dir: Path) -> None:
    meta = json.loads((book_dir / "_meta.json").read_text(encoding="utf-8"))
    book_title = meta["book"]
    num = book_title.split(" - ")[0]
    lines = [f"# {book_title}", "",
             f"*Auto-generated philosopher/concept map — {len(meta['chapters'])} chapters. "
             f"Numbers in parentheses are mention counts.*", ""]
    for ch in meta["chapters"]:
        f = book_dir / ch["file"]
        text = f.read_text(encoding="utf-8")
        front_matter = (ch["title"] + " " + text[:400]).lower()
        if any(k in front_matter for k in (
                "table of contents", "series editor:", "_toc_r1", "also available",
                "volume 1 seinfeld", "volume 1 the simpsons")):
            continue
        ph = Counter()
        for name, rx in PH_MATCHERS:
            hits = rx.findall(text)
            if hits:
                ph[name] = len(hits)
        co = Counter()
        for name, rx in CO_MATCHERS:
            hits = rx.findall(text)
            if hits:
                co[name] = len(hits)
        exc = excerpt_of(text.split("\n", 3)[-1] if text.startswith("#") else text)
        lines += [f"## Ch.{ch['n']:02d} — {ch['title']}", "",
                  f"**Overview:** {exc}", "",
                  f"**Philosophers:** {top_items(ph)}", "",
                  f"**Concepts:** {top_items(co, 8)}", ""]
        chapter_records.append({
            "book_num": num,
            "book": book_title,
            "ch": ch["n"],
            "title": ch["title"],
            "words": ch["words"],
            "philosophers": dict(ph),
            "concepts": dict(co),
            "excerpt": exc,
        })

    out = AN_ROOT / book_dir.name
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.md").write_text("\n".join(lines), encoding="utf-8")


chapter_records: list = []


def main() -> None:
    AN_ROOT.mkdir(parents=True, exist_ok=True)
    books = sorted(MD_ROOT.iterdir())
    for d in books:
        if d.is_dir() and (d / "_meta.json").exists():
            analyze_book(d)
            print(f"analyzed {d.name}", flush=True)

    (BATCH / "chapter_index.json").write_text(
        json.dumps(chapter_records, indent=1, ensure_ascii=False), encoding="utf-8")

    # aggregation
    ph_books = defaultdict(set)
    co_books = defaultdict(set)
    ph_ch = Counter()
    co_ch = Counter()
    co_book_subjects = defaultdict(lambda: defaultdict(int))
    for rec in chapter_records:
        for name in rec["philosophers"]:
            ph_books[name].add(rec["book_num"])
            ph_ch[name] += 1
        for name in rec["concepts"]:
            co_books[name].add(rec["book_num"])
            co_ch[name] += 1
            co_book_subjects[name][rec["book"]] += 1
    agg = {
        "books": len({r["book_num"] for r in chapter_records}),
        "chapters": len(chapter_records),
        "philosopher_breadth": sorted(
            [{"name": k, "books": len(v), "chapters": ph_ch[k]} for k, v in ph_books.items()],
            key=lambda x: -x["books"]),
        "concept_breadth": sorted(
            [{"name": k, "books": len(v), "chapters": co_ch[k]} for k, v in co_books.items()],
            key=lambda x: -x["books"]),
        "concept_subjects": {k: dict(sorted(v.items(), key=lambda x: -x[1])[:30])
                             for k, v in list(co_book_subjects.items())},
    }
    (BATCH / "aggregate.json").write_text(json.dumps(agg, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\naggregate: {agg['books']} books, {agg['chapters']} chapters", flush=True)
    print("top philosophers by books:", flush=True)
    for e in agg["philosopher_breadth"][:15]:
        print(f"  {e['name']}: {e['books']} books / {e['chapters']} chapters", flush=True)
    print("top concepts by books:", flush=True)
    for e in agg["concept_breadth"][:15]:
        print(f"  {e['name']}: {e['books']} books / {e['chapters']} chapters", flush=True)


if __name__ == "__main__":
    main()

# standalone concept added after Merleau-Ponty fix
CONCEPTS["embodiment"] = [r"embodiment", r"embodied"]
