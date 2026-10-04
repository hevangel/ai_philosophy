"""Generate the final hole-driven taxonomy extension.

Reads merged_index.json holes, applies the curated accept list (curated by
hand from the frequency-sorted candidates), and writes:
  ext_block.py.txt   — P/C dict literal lines to paste into build_taxonomy.py
  bindings.json      — [(unit, ch, slug, type)] for binding hole chapters
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(r"B:\ai_philosophy\sratchpad\popcult_index").resolve()
m = json.loads((BASE / "merged_index.json").read_text(encoding="utf-8"))

# slug -> (type, display name, tied-philosopher-or-"", domain)
ACCEPTED = {
    # --- philosophers ---
    "cs-lewis": ("philosopher", "C.S. Lewis", "", "religion-meaning"),
    "ayn-rand": ("philosopher", "Ayn Rand", "", "political-social"),
    "charles-taylor": ("philosopher", "Charles Taylor", "", "political-social"),
    "bakhtin": ("philosopher", "Mikhail Bakhtin", "", "political-social"),
    "max-weber": ("philosopher", "Max Weber", "", "political-social"),
    "voltaire": ("philosopher", "Voltaire", "", "medieval-early-modern"),
    "zizek": ("philosopher", "Slavoj Žižek", "", "political-social"),
    "kristeva": ("philosopher", "Julia Kristeva", "", "mind-language-metaphysics"),
    "donald-davidson": ("philosopher", "Donald Davidson", "", "mind-language-metaphysics"),
    "whitehead": ("philosopher", "Alfred North Whitehead", "", "pragmatism-american"),
    "george-herbert-mead": ("philosopher", "George Herbert Mead", "", "pragmatism-american"),
    "haraway": ("philosopher", "Donna Haraway", "", "feminism-gender-race"),
    "schelling": ("philosopher", "F.W.J. Schelling", "", "kant-german-idealism"),
    "john-hick": ("philosopher", "John Hick", "", "religion-meaning"),
    "langer": ("philosopher", "Susanne Langer", "", "mind-language-metaphysics"),
    "becker-denial-of-death": ("philosopher", "Ernest Becker", "", "existentialism-phenomenology"),
    "carroll-aesthetics": ("philosopher", "Noël Carroll", "", "mind-language-metaphysics"),
    "warren-personhood": ("philosopher", "Mary Anne Warren", "", "ethics-moral-psychology"),
    "roland-barthes": ("philosopher", "Roland Barthes", "", "political-social"),
    "clifford": ("philosopher", "W.K. Clifford", "", "knowledge-science-reality"),
    "bourdieu": ("philosopher", "Pierre Bourdieu", "", "political-social"),
    "richard-taylor": ("philosopher", "Richard Taylor", "", "mind-language-metaphysics"),
    "dostoevsky": ("philosopher", "Fyodor Dostoevsky", "", "nineteenth-century"),
    "paulo-freire": ("philosopher", "Paulo Freire", "", "political-social"),
    "annette-baier": ("philosopher", "Annette Baier", "", "ethics-moral-psychology"),
    "melanie-klein": ("philosopher", "Melanie Klein", "", "mind-language-metaphysics"),
    "galen-strawson": ("philosopher", "Galen Strawson", "", "mind-language-metaphysics"),
    "carl-schmitt": ("philosopher", "Carl Schmitt", "", "political-social"),
    "vico": ("philosopher", "Giambattista Vico", "", "medieval-early-modern"),
    "empedocles": ("philosopher", "Empedocles", "", "ancient"),
    "edmund-burke": ("philosopher", "Edmund Burke", "", "medieval-early-modern"),
    "clausewitz": ("philosopher", "Carl von Clausewitz", "", "political-social"),
    "darwin": ("philosopher", "Charles Darwin", "", "knowledge-science-reality"),
    "mcluhan": ("philosopher", "Marshall McLuhan", "", "political-social"),
    "derrick-bell": ("philosopher", "Derrick Bell", "", "feminism-gender-race"),
    "cavell": ("philosopher", "Stanley Cavell", "", "pragmatism-american"),
    "joseph-campbell": ("philosopher", "Joseph Campbell", "", "religion-meaning"),
    "horkheimer": ("philosopher", "Max Horkheimer", "", "political-social"),
    "j-l-austin": ("philosopher", "J.L. Austin", "", "mind-language-metaphysics"),
    "rudolf-carnap": ("philosopher", "Rudolf Carnap", "", "mind-language-metaphysics"),
    "tocqueville": ("philosopher", "Alexis de Tocqueville", "", "political-social"),
    "tolstoy": ("philosopher", "Leo Tolstoy", "", "political-social"),
    "giorgio-agamben": ("philosopher", "Giorgio Agamben", "", "political-social"),
    "milton-friedman": ("philosopher", "Milton Friedman", "", "political-social"),
    "josiah-royce": ("philosopher", "Josiah Royce", "", "pragmatism-american"),
    "goffman": ("philosopher", "Erving Goffman", "", "political-social"),
    "graham-priest": ("philosopher", "Graham Priest", "", "mind-language-metaphysics"),
    "gaston-bachelard": ("philosopher", "Gaston Bachelard", "", "existentialism-phenomenology"),
    "georges-bataille": ("philosopher", "Georges Bataille", "", "political-social"),
    "iris-murdoch": ("philosopher", "Iris Murdoch", "", "ethics-moral-psychology"),
    "simone-weil": ("philosopher", "Simone Weil", "", "religion-meaning"),
    "max-scheler": ("philosopher", "Max Scheler", "", "existentialism-phenomenology"),
    "benatar": ("philosopher", "David Benatar", "", "ethics-moral-psychology"),
    "hierocles": ("philosopher", "Hierocles", "", "ancient"),
    "kropotkin": ("philosopher", "Pyotr Kropotkin", "", "political-social"),
    "girard": ("philosopher", "René Girard", "", "ethics-moral-psychology"),
    "audre-lorde": ("philosopher", "Audre Lorde", "", "feminism-gender-race"),
    "kendall-walton": ("philosopher", "Kendall Walton", "", "mind-language-metaphysics"),
    "irigaray": ("philosopher", "Luce Irigaray", "", "feminism-gender-race"),
    "byung-chul-han": ("philosopher", "Byung-Chul Han", "", "political-social"),
    "jameson": ("philosopher", "Fredric Jameson", "", "political-social"),
    "umberto-eco": ("philosopher", "Umberto Eco", "", "political-social"),
    "huizinga": ("philosopher", "Johan Huizinga", "", "mind-language-metaphysics"),
    "bernard-suits": ("philosopher", "Bernard Suits", "", "ethics-moral-psychology"),
    "p-f-strawson": ("philosopher", "P.F. Strawson", "", "ethics-moral-psychology"),
    "h-richard-niebuhr": ("philosopher", "H. Richard Niebuhr", "", "religion-meaning"),
    "guy-debord": ("philosopher", "Guy Debord", "", "political-social"),
    # --- concepts ---
    "paradox-of-fiction": ("concept", "The Paradox of Fiction", "", "mind-language-metaphysics"),
    "catharsis": ("concept", "Catharsis (tragic purgation)", "aristotle", "ancient"),
    "narrative-identity": ("concept", "Narrative Identity", "", "mind-language-metaphysics"),
    "supererogation": ("concept", "Supererogation (beyond the call of duty)", "", "ethics-moral-psychology"),
    "transhumanism": ("concept", "Transhumanism", "", "ethics-moral-psychology"),
    "nihilism": ("concept", "Nihilism", "", "nineteenth-century"),
    "informal-fallacies": ("concept", "Informal Fallacies", "", "knowledge-science-reality"),
    "functionalism": ("concept", "Functionalism (philosophy of mind)", "", "mind-language-metaphysics"),
    "family-resemblance": ("concept", "Family Resemblance", "wittgenstein", "mind-language-metaphysics"),
    "scientism": ("concept", "Scientism", "", "knowledge-science-reality"),
    "posthumanism": ("concept", "Posthumanism", "", "mind-language-metaphysics"),
    "game-theory": ("concept", "Game Theory", "", "political-social"),
    "problem-of-other-minds": ("concept", "The Problem of Other Minds", "", "mind-language-metaphysics"),
    "mimesis": ("concept", "Mimesis (art as imitation)", "aristotle", "ancient"),
    "gnosticism": ("concept", "Gnosticism (gnosis)", "", "religion-meaning"),
    "dirty-hands": ("concept", "The Problem of Dirty Hands", "", "political-social"),
    "religious-pluralism": ("concept", "Religious Pluralism", "john-hick", "religion-meaning"),
    "the-uncanny": ("concept", "The Uncanny (das Unheimliche)", "freud", "mind-language-metaphysics"),
    "bushido": ("concept", "Bushido (the way of the warrior)", "", "eastern-world"),
    "logical-positivism": ("concept", "Logical Positivism (verifiability theory)", "", "knowledge-science-reality"),
    "truth-in-fiction": ("concept", "Truth in Fiction", "kendall-walton", "mind-language-metaphysics"),
    "memetics": ("concept", "Memetics (cultural evolution)", "", "knowledge-science-reality"),
    "ethics-of-belief": ("concept", "The Ethics of Belief (evidentialism)", "clifford", "knowledge-science-reality"),
    "philosophy-of-play": ("concept", "Philosophy of Play", "huizinga", "ethics-moral-psychology"),
    "corporate-personhood": ("concept", "Corporate Moral Personhood", "", "political-social"),
    "moral-particularism": ("concept", "Moral Particularism", "", "ethics-moral-psychology"),
    "relational-autonomy": ("concept", "Relational Autonomy", "", "feminism-gender-race"),
    "philosophy-of-humor": ("concept", "Philosophy of Humor", "", "ethics-moral-psychology"),
    "eliminative-materialism": ("concept", "Eliminative Materialism", "", "mind-language-metaphysics"),
    "fascism": ("concept", "Fascism", "", "political-social"),
    "incongruity-theory-humor": ("concept", "Incongruity Theory of Humor", "kant", "kant-german-idealism"),
    "personalism": ("concept", "Personalism", "", "ethics-moral-psychology"),
    "standard-of-taste": ("concept", "The Standard of Taste", "hume", "medieval-early-modern"),
    "abduction": ("concept", "Inference to the Best Explanation (abduction)", "", "pragmatism-american"),
    "prisoners-dilemma": ("concept", "The Prisoner's Dilemma and Tit-for-Tat", "", "political-social"),
    "maslow-hierarchy-of-needs": ("concept", "Maslow's Hierarchy of Needs", "", "ethics-moral-psychology"),
    "underdetermination": ("concept", "Underdetermination of Theory by Evidence", "", "knowledge-science-reality"),
    "the-sublime": ("concept", "The Sublime", "", "kant-german-idealism"),
    "correspondence-theory-of-truth": ("concept", "Correspondence Theory of Truth", "", "knowledge-science-reality"),
    "tragedy-of-the-commons": ("concept", "The Tragedy of the Commons", "", "political-social"),
    "personhood": ("concept", "Personhood (vs genetic humanity)", "", "ethics-moral-psychology"),
    "imaginative-resistance": ("concept", "Imaginative Resistance", "", "mind-language-metaphysics"),
    "art-horror": ("concept", "Art-Horror", "carroll-aesthetics", "mind-language-metaphysics"),
    "great-chain-of-being": ("concept", "The Great Chain of Being", "", "medieval-early-modern"),
    "oedipus-complex": ("concept", "The Oedipus Complex", "freud", "mind-language-metaphysics"),
    "legal-positivism": ("concept", "Legal Positivism (law and morality separable)", "", "political-social"),
    "self-deception": ("concept", "Self-Deception", "", "ethics-moral-psychology"),
    "constitutive-rules": ("concept", "Constitutive Rules (rules that define games)", "", "mind-language-metaphysics"),
    "argument-from-reason": ("concept", "The Argument from Reason", "cs-lewis", "religion-meaning"),
    "metabolic-rift": ("concept", "Metabolic Rift", "marx", "nineteenth-century"),
    "epistemology-of-testimony": ("concept", "Epistemology of Testimony", "", "knowledge-science-reality"),
    "institutional-theory-of-art": ("concept", "Institutional Theory of Art", "", "mind-language-metaphysics"),
    "natural-kinds": ("concept", "Natural Kinds vs Nominal Kinds", "", "knowledge-science-reality"),
    "situationism": ("concept", "Situationism (situationist social psychology)", "", "ethics-moral-psychology"),
    "soul-making-theodicy": ("concept", "Soul-Making Theodicy", "john-hick", "religion-meaning"),
    "cyborg": ("concept", "The Cyborg", "haraway", "feminism-gender-race"),
    "purity-and-danger": ("concept", "Purity and Danger (dirt as matter out of place)", "", "political-social"),
    "eugenics": ("concept", "Eugenics", "", "ethics-moral-psychology"),
    "liar-paradox": ("concept", "The Liar Paradox", "", "mind-language-metaphysics"),
    "dialetheism": ("concept", "Dialetheism (true contradictions)", "graham-priest", "mind-language-metaphysics"),
    "romanticism": ("concept", "Romanticism (imagination and the infinite)", "", "nineteenth-century"),
    "abjection": ("concept", "Abjection (the abject)", "kristeva", "political-social"),
    "philosophy-of-music": ("concept", "Philosophy of Music", "", "kant-german-idealism"),
    "aestheticism": ("concept", "Aestheticism (art for art's sake)", "", "nineteenth-century"),
    "political-realism": ("concept", "Political Realism (power over morality)", "carl-schmitt", "political-social"),
    "anti-natalism": ("concept", "Anti-Natalism", "benatar", "ethics-moral-psychology"),
    "ethics-of-lying": ("concept", "The Ethics of Lying and Deception", "", "ethics-moral-psychology"),
    "physicalism": ("concept", "Physicalism", "", "mind-language-metaphysics"),
    "moral-dilemmas": ("concept", "Moral Dilemmas (non-negotiable duties)", "", "ethics-moral-psychology"),
    "philosophy-of-art": ("concept", "Philosophy of Art (artistic value)", "", "kant-german-idealism"),
    "biopower": ("concept", "Biopower", "foucault", "political-social"),
    "uncanny-valley": ("concept", "The Uncanny Valley", "", "mind-language-metaphysics"),
    "society-of-the-spectacle": ("concept", "The Society of the Spectacle", "guy-debord", "political-social"),
    "aspect-perception": ("concept", "Aspect Perception (seeing-as)", "wittgenstein", "mind-language-metaphysics"),
    "stakeholder-theory": ("concept", "Stakeholder Theory (vs stockholder theory)", "", "ethics-moral-psychology"),
    "moral-dilemmas": ("concept", "Moral Dilemmas (non-negotiable duties)", "", "ethics-moral-psychology"),
    "death-of-the-author": ("concept", "The Death of the Author", "roland-barthes", "political-social"),
    "pacifism": ("concept", "Pacifism", "", "political-social"),
    "film-as-philosophy": ("concept", "Film as Philosophy", "", "knowledge-science-reality"),
    "ontology-of-fiction": ("concept", "Ontology of Fictional Characters", "", "mind-language-metaphysics"),
}

# alias merges within proposals -> canonical accepted slug
ALIAS = {
    "sigmund-freud": "freud", "carl-jung": "jung", "mikhail-bakhtin": "bakhtin",
    "c-s-lewis": "cs-lewis", "clive-staples-lewis": "cs-lewis",
    "edmund-burke": "edmund-burke", "burke": "edmund-burke",
    "inference-to-best-explanation": "abduction",
    "aristotle-poetics": "catharsis", "aristotle-catharsis": "catharsis",
    "austin": "j-l-austin", "charles-darwin": "darwin",
    "alfred-north-whitehead": "whitehead", "max-horkheimer": "horkheimer",
    "donna-haraway": "haraway", "barthes": "roland-barthes",
    "marshall-mcluhan": "mcluhan", "slavoj-zizek": "zizek",
    "wk-clifford": "clifford", "benatar": "benatar",
    "strawson": "p-f-strawson", "jameson": "jameson",
}

# aggregate binding map: (unit, ch) -> [(slug, type)]
bindings = defaultdict(set)
agg = defaultdict(lambda: {"units": []})
for h in m["holes"]:
    slug = re.sub(r"[^a-z0-9-]", "", h.get("suggested_slug", "").lower().strip())
    if not slug:
        continue
    slug = ALIAS.get(slug, slug)
    if slug not in ACCEPTED:
        continue
    bindings[(h["unit"], h["ch"])].add(
        (slug, ACCEPTED[slug][0]))
    agg[slug]["units"].append(h["unit"])

# taxonomy block
plines, clines = [], []
for slug, (typ, name, phil, dom) in sorted(ACCEPTED.items()):
    if typ == "philosopher":
        plines.append('    "%s": ["%s", "", "%s"],' % (slug, name, dom))
    else:
        clines.append('    "%s": ["%s", "%s", "%s"],' % (slug, name, phil, dom))
block = "\n".join(plines) + "\n\n#HOLEXT\n" + "\n".join(clines)
(BASE / "ext_block.py.txt").write_text(block, encoding="utf-8")

bjson = [{"unit": u, "ch": c, "slug": s, "type": t}
         for (u, c), slugs in sorted(bindings.items()) for (s, t) in sorted(slugs)]
(BASE / "bindings.json").write_text(json.dumps(bjson, ensure_ascii=False, indent=1),
                                    encoding="utf-8")
n_phil = sum(1 for v in ACCEPTED.values() if v[0] == "philosopher")
n_con = len(ACCEPTED) - n_phil
print("accepted: %d philosophers + %d concepts = %d" % (n_phil, n_con, len(ACCEPTED)))
print("binding entries: %d across %d (unit,ch) pairs"
      % (len(bjson), len(bindings)))
