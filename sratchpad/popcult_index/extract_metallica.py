"""Extract the Metallica and Philosophy PDF into corpus-standard markdown.

Source: sratchpad/William Irwin - Metallica and Philosophy_ ... (2007) - libgen.li.pdf
Output: philosophy_pop_culture/markdown/183 - Metallica and Philosophy - A Crash
Course in Brain Surgery/chNN - Title.md in the extractor's header format.
The PDF has no embedded TOC and its decorative chapter title pages extract no
text, so boundaries use the printed contents pages' book-page numbers with the
verified offset (book page N >= 5 -> pdf index N + 10).
"""
import re
from pathlib import Path

import fitz

BASE = Path(r"B:\ai_philosophy\sratchpad\popcult_index").resolve()
PDF_PATH = Path(
    r"B:\ai_philosophy\sratchpad\William Irwin - Metallica and Philosophy_ "
    r"A Crash Course in Brain Surgery (The Blackwell Philosophy and Pop Culture "
    r"Series) (2007) - libgen.li.pdf"
).resolve()
OUT_DIR = Path(
    r"B:\ai_philosophy\philosophy_pop_culture\markdown"
    r"\183 - Metallica and Philosophy - A Crash Course in Brain Surgery"
).resolve()
BOOK = "183 - Metallica and Philosophy - A Crash Course in Brain Surgery"

LIG = {"\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi",
       "\ufb04": "ffl", "\u2019": "'", "\u2018": "'", "\u201c": '"',
       "\u201d": '"', "\u2014": "---", "\u2013": "--", "\u2026": "..."}

# (n, title, author, pdf_start_page) — from the printed contents; front/back
# matter located directly. End of each item = next item's start (or last page).
ITEMS = [
    (1, "Heroes of the Day: Acknowledgments", "", 8),
    (2, "Hit the Lights", "William Irwin", 11),
    (3, "On Through the Never", "", 13),
    (4, "Whisper Things Into My Brain: Metallica, Emotion, and Morality",
     "Robert Fudge", 15),
    (5, "This Search Goes On: Christian, Warrior, Buddhist", "William Irwin", 26),
    (6, "Alcoholica: When Sweet Amber Becomes the Master of Puppets",
     "Bart Engelen", 39),
    (7, "Through the Mist and the Madness: Metallica's Message of "
     "Nonconformity, Individuality, and Truth", "Thomas Nys", 51),
    (8, "Existensica: Metallica Meets Existentialism", "", 63),
    (9, "The Metal Militia and the Existentialist Club",
     "J. Jeremy Wisnewski", 65),
    (10, "The Struggle Within: Hetfield, Kierkegaard, and the Pursuit of "
     "Authenticity", "Philip Lindholm", 75),
    (11, "Metallica, Nietzsche, and Marx: The Immorality of Morality",
     "Peter S. Fosl", 84),
    (12, "Metallica's Existential Freedom: From We to I and Back Again",
     "Rachael Sotos", 95),
    (13, "Living and Dying, Laughing and Crying", "", 109),
    (14, "To Live is to Die: Metallica and the Meaning of Life", "Scott Calef",
     111),
    (15, "Madness in the Mirror of Reason: Metallica and Foucault on Insanity "
     "and Confinement", "Brian K. Cameron", 127),
    (16, "Ride the Lightning: Why Not Execute Killers?", "Thom Brooks", 137),
    (17, "Living and Dying as One: Suffering and the Ethics of Euthanasia",
     "Jason T. Eberl", 145),
    (18, "Fade to Black: Absurdity, Suicide, and the Downward Spiral",
     "Justin Donhauser and Kimberly A. Blessing", 158),
    (19, "Metaphysica, Epistemologica, Metallica", "", 171),
    (20, "Believer, Deceiver: Metallica, Perception, and Reality",
     "Robert Arp", 173),
    (21, "Trapped in Myself: \"One\" and the Mind-Body Problem",
     "Joanna Corwin", 183),
    (22, "Is It Still Metallica? On the Identity of Rock Bands Over Time",
     "Manuel Bremer and Daniel Cohnitz", 193),
    (23, "Fans and the Band", "", 207),
    (24, "Metallica Drops a Load: What Do Bands and Fans Owe Each Other?",
     "Mark D. White", 209),
    (25, "The Unsocial Sociability of Humans and Metal Gods", "Niall Scott", 220),
    (26, "Boys Interrupted: The Drama of Male Bonding in Some Kind of Monster",
     "Judith Grant", 229),
    (27, "Justice for All? Metallica's Argument Against Napster and Internet "
     "File Sharing", "Robert A. Delfino", 242),
    (28, "Who's Who in the Metal Militia", "", 255),
    (29, "The Phantom Lord's Index", "", 260),
]

PART_DIVIDERS = {3, 8, 13, 19, 23}
FRONT_NOTES = {1, 28, 29}


def clean(text):
    for k, v in LIG.items():
        text = text.replace(k, v)
    lines = text.split("\n")
    joined = []
    for ln in lines:
        ln = ln.rstrip()
        if joined and joined[-1].endswith("-") and ln and ln[0].islower():
            joined[-1] = joined[-1][:-1] + ln
        else:
            joined.append(ln)
    text = "\n".join(joined)
    blocks, cur = [], []
    for ln in text.split("\n"):
        if ln.strip():
            cur.append(ln.strip())
        elif cur:
            blocks.append(" ".join(cur))
            cur = []
    if cur:
        blocks.append(" ".join(cur))
    return "\n\n".join(blocks)


def safe_stem(title):
    stem = re.sub(r'[<>:"/\\|?*]+', "", title).strip()
    if stem in (".", ".."):
        raise ValueError("bad stem")
    return stem


def main():
    doc = fitz.open(str(PDF_PATH))
    pages = [p.get_text() for p in doc]
    flat = [clean(t) for t in pages]

    starts = [it[3] for it in ITEMS]
    if starts != sorted(starts):
        raise SystemExit("item start pages not monotonic")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = []
    for idx, (n, title, author, a) in enumerate(ITEMS):
        b = starts[idx + 1] if idx + 1 < len(starts) else len(pages)
        body = "\n\n".join(flat[a:b])
        if author:
            body = "*by %s*\n\n%s" % (author, body)
        words = len(body.split())
        fname = "ch%02d - %s.md" % (n, safe_stem(title))
        header = "# %s\n\n*Source: %s — chapter %d*\n\n" % (title, BOOK, n)
        (OUT_DIR / fname).write_text(header + body + "\n", encoding="utf-8")
        report.append((n, fname, words))
        print("ch%02d  pdf pages %3d-%3d  %6d words  %s"
              % (n, a, b - 1, words, fname))
    print("total words:", sum(r[2] for r in report))


if __name__ == "__main__":
    main()
