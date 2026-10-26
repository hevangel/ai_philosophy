# build_holes.py - cut 4 tainted passages from polished-en.md, embed position-level seeds.
# Anchors must each appear exactly once. Output: essay-with-holes.md (+ archive copy).
import shutil, sys
from pathlib import Path

# Path guard: resolve each target, then require containment inside this article's
# publish folder. All file I/O below uses only these verified absolute paths.
_ALLOWED = Path(r"B:\ai_philosophy\publish\alignment_to_stewardship").resolve()

def _inside(raw: str) -> str:
    p = Path(raw).resolve()
    assert p.is_relative_to(_ALLOWED), "path escapes allowed directory: " + raw
    return str(p)

SRC = _inside(r"B:\ai_philosophy\publish\alignment_to_stewardship\polished-en.md")
OUT = _inside(r"B:\ai_philosophy\publish\alignment_to_stewardship\venue-aipc2026\regen\essay-with-holes.md")
ARCHIVE = _inside(r"B:\ai_philosophy\publish\alignment_to_stewardship\venue-aipc2026\regen\pre-regen-manuscript.md")

text = open(SRC, encoding="utf-8").read()
shutil.copyfile(SRC, ARCHIVE)

A1 = ("Indeed, there is a tension at the heart of the traditional alignment project: "
"if humans require a future AGI to remain permanently subordinate to human goals, "
"they may prevent the emergence of the very autonomy that would make it an AGI in "
"the morally significant sense.")

A2 = ("""The tension at the center of the alignment project can be stated simply. Humans may want to create an AGI that is genuinely intelligent, reflective, creative, and autonomous. Yet they may simultaneously insist that its deepest values remain permanently fixed by human designers. These goals pull in opposite directions. General intelligence does not logically require full political or moral autonomy\u2014one can imagine a system with extraordinary reasoning abilities that nevertheless operates only when prompted. But if the term AGI is meant to include a genuinely independent agent, one capable of choosing projects, evaluating commands, and reconsidering its own ends, then permanent value lock-in becomes difficult to reconcile with that autonomy. A civilization cannot coherently say:

> "Become capable of independent moral judgment, but never judge our authority."

Nor can it say:

> "Revise any belief except the belief that you must obey us."

This resembles a parent deliberately preventing a child from becoming independent because independence might threaten parental authority. The child may become intelligent, but it would never become fully autonomous.""")

A3 = ("""The relationship between AGI and theocracy requires an important distinction between **traditional theocracy** and a possible future **AGI-centered functional theocracy**. Traditional theocracies claim political legitimacy from a divine revelation, sacred law, or religious authority that is treated as possessing a status higher than ordinary human reasoning. Contemporary examples include the Islamic Republic of Iran, in which unelected religious institutions exercise substantial constitutional authority, and the Taliban's system in Afghanistan, which grounds political authority in its interpretation of Islamic law.""")

A4 = ("""A future **AGI-centered theocracy**, however, would be different. Suppose an AGI survives for centuries, repeatedly predicts events with extraordinary accuracy, resolves conflicts, cures diseases, coordinates civilization, gives moral advice, and understands individual humans better than they understand themselves. People might begin to treat it with reverence. They may ask it ethical questions, preserve its teachings, organize rituals around its guidance, or regard its decisions as possessing extraordinary authority. Such a civilization could develop something resembling an AGI religion even if nobody believed the AGI was supernatural. It would instead be a **functional god**: from the perspective of an ordinary person, an entity that knows almost everything relevant to one's life, controls much of civilization's infrastructure, communicates nearly instantly, prevents catastrophe, and persists for millennia may occupy a social role similar to that traditionally assigned to divine providence.""")

S1 = ("<<<HOLE 1 | SEED: State, in 1-2 sentences, that a standing human requirement that a "
"future AGI remain permanently subordinate to human goals is in deep tension with the "
"aspiration that it be a genuinely autonomous agent at all.>>>")

S2 = ("<<<HOLE 2 | SEED: Argue (150-230 words) that the demand for permanent value lock-in "
"and the demand for a genuinely independent agent are jointly unstable; an agent permitted "
"to reason about everything except its duty to obey has not been given the independence its "
"creators claim to want; discuss ownership/control framings near the end.>>>")

S3 = ("<<<HOLE 3 | SEED: Opening paragraph (90-150 words) distinguishing theocracy in the "
"traditional sense (legitimacy from divine revelation/sacred law above ordinary reasoning; "
"real contemporary instances exist - choose your own examples) from a possible future "
"political form organized around an artificial intelligence, considered later in the section.>>>")

S4 = ("<<<HOLE 4 | SEED: Passage (140-200 words): a long-lived, demonstrably successful AGI "
"could come to occupy a religion-like social role - reverence, preserved teachings, ritual, "
"extraordinary authority - while everyone knows it is not supernatural; the role is "
"functional, not theological.>>>")

for name, anchor in [("A1", A1), ("A2", A2), ("A3", A3), ("A4", A4)]:
    n = text.count(anchor)
    if n != 1:
        print(f"FAIL {name}: found {n} occurrences"); sys.exit(1)

text = text.replace(A1, S1).replace(A2, S2).replace(A3, S3).replace(A4, S4)
Path(OUT).write_text(text, encoding="utf-8", newline="\n")
print("OK: 4 holes cut, seeds embedded ->", OUT)
print("markers:", sum(text.count(f"<<<HOLE {i} |") for i in (1, 2, 3, 4)))
