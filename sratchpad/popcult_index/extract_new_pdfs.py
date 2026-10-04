"""Extract the four new full-book PDFs (161, 194, 206, 235) into corpus-standard
markdown, following extract_metallica.py's output format.

Boundaries: embedded TOC level-2 where the mirror's PDF has one (194, 235),
font-survey + hand-verified starts otherwise (161, 206). #161's printed scan
typesets chapters 14 and 15 on one opening spread (their bodies interleave), so
they extract as one chapter file carrying both titles.
"""
import os
import re
from pathlib import Path

import fitz

ROOT = Path(r"B:\ai_philosophy\philosophy_pop_culture")
PDF_DIR = (ROOT / "pdf").resolve()
MD_ROOT = (ROOT / "markdown").resolve()


def checked_path(base, name):
    p = (base / name).resolve()
    if os.path.commonpath([str(p), str(base)]) != str(base):
        raise ValueError("resolved path outside allowed root: %s" % p)
    return p


LIG = {"\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi",
       "\ufb04": "ffl", "\u2019": "'", "\u2018": "'", "\u201c": '"',
       "\u201d": '"', "\u2014": "---", "\u2013": "--", "\u2026": "..."}


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
    blocks, cur = [], []
    for ln in joined:
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


BOOKS = {
    "161 - Family Guy and Philosophy - A Cure for the Petarded": [
        ("Front matter", 0),
        ("You Better Not Read This, Pal: An Introduction to Family Guy and Philosophy", 12),
        ("Part I: Those Good Ole' Fashion Values on which we used to rely", 14),
        ("Killing the Griffins: A Murderous Exposition of Postmodernism", 16),
        ("Family Guy and God: Should Believers Take Offense?", 27),
        ("Quagmire: Virtue and Perversity", 38),
        ("Francis Griffin and the Church of the Holy Fonz: Religious Exclusivism and Real Religion", 47),
        ("Part II: Lucky there's a family guy! (And what a family!)", 61),
        ("Let Us Now Praise Clueless Men: Peter Griffin and Philosophy", 62),
        ("Lois: Portrait of a Mother (Or, Nevermind Death, Motherhood is a Bitch)", 70),
        ("Mmmyez: Stewie and the Seven Deadly Sins", 85),
        ("The Other Children: The Importance of Meg and Chris", 98),
        ("He Thinks He's People: How Brian Made Personhood for the Dogs", 110),
        ("Part III: You expected more lyrics, but you're getting logic, comedy, and the logic of comedy", 124),
        ("The Logic of Expectation: Family Guy and the Non Sequitur", 126),
        ("What Are You Laughing At (And Why)? Exploring the Humor of Family Guy", 139),
        ("Thinkin' is Freakin' Sweet: Family Guy and Fallacies", 150),
        ("The Simpsons Already Did It! This Show Is A Freakin' Rip-Off!", 160),
        ("Part IV: Family Problems", 172),
        ("Is Brian More of a Person than Peter? (scan merges: Of Wills, Wantons, and Wives)", 174),
        ("The Ego is a Housewife Named Lois", 186),
        ("The Lives and Times of Stewie Griffin", 197),
        ("Kierkegaard and the Norm (MacDonald) of Death", 209),
        ("Appendix: Everything you ever needed to know about Meg Griffin", 217),
        ("Notes on Contributors", 223),
        ("Index", 225),
    ],
    "194 - Taylor Swift and Philosophy - Essays from the Tortured Philosophers Department": [
        ("Front matter", 0),
        ("Introducing ... Taylor Swift's Philosophy Era", 16),
        ("Part I: Who Is Taylor Swift Anyway? Ew", 17),
        ("Is Taylor Swift a Philosopher?", 19),
        ("You Should Find Another Guiding Light: Is Taylor Swift Admirable?", 28),
        ("Eyes Open: Taylor Swift and the Philosophy of Easter Eggs", 35),
        ("Taylor Swift and the Ethics of Body Image", 44),
        ("So Mother for That: Taylor Swift and Childless Mothering", 52),
        ("Part II: Look What You Made Me Do - Reputation, Forgiveness, and Blame", 63),
        ("Can I Forgive You for Breaking My Heart?", 65),
        ("How to Forgive an Innocent: Taylor, Kanye, and the Ethics of Forgiveness", 74),
        ("This Is Why We Can't Have Nice Things: Goodwill as a Finite Resource", 82),
        ("Taylor Swift's Philosophy of Reputation", 88),
        ("It's Me, Hi! I'm the Problem It's Me: Taylor Swift and Self-Blame", 97),
        ("Part III: The Girl in the Dress Wrote You a Song", 105),
        ("Begin Again (Taylor's Version): On Taylor Swift's Repetition and Difference", 107),
        ("Is Taylor Swift's Music Timeless? A Metaphysical Proof", 115),
        ("I Remember It All Too Well: Memory, Nostalgia, and the Archival Art of Taylor Swift", 123),
        ("Taylor's Version: Rerecording, Narrative, and Self-Interpretation", 132),
        ("Part IV: With My Calamitous Love and Insurmountable Grief", 143),
        ("Taylor Swift on the Values and Vulnerability of Love", 145),
        ("Every Scrap of You Would Be Taken from Me: Taylor Swift on Grief", 153),
        ("What a Shame She Went Mad: Anger, Affective Injustice, and Taylor Swift", 163),
        ("I'm Fine with My Spite: The Philosophy of Female Anger in the Work of Taylor Swift", 170),
        ("Part V: I Should've Known - Taylor Swift's Philosophy of Knowledge", 179),
        ("Summer Love or Just a Summer Thing? Feminist Standpoint Epistemology", 181),
        ("The Trouble with Knowing You Were Trouble", 190),
        ("I Knew Everything When I Was Young: Examining the Wisdom of Youth", 198),
        ("How Do We Know What Taylor Swift Is Feeling?", 205),
        ("Part VI: Back to December - Fate, Memory, and Imagination", 215),
        ("A Real Lasting Legacy: Memory, Imagination, and Taylor Swift", 217),
        ("Stained Glass Windows in My Mind: Modality in the Imagery of Taylor Swift", 224),
        ("Take Me to the Lakes: Transcendentalism and Ecology in Taylor Swift's folklore", 232),
        ("Wildest Dreams: Stoic Fate and Acceptance (Taylor's Version)", 241),
        ("Mythic Motifs in The Tortured Poets Department: The Story Isn't Mine Anymore", 247),
        ("Indexes", 254),
    ],
    "206 - The Witcher and Philosophy - Toss a Coin to Your Philosopher": [
        ("Front matter", 0),
        ("Introduction", 14),
        ("Part I: Ethics", 16),
        ("A Friend of Humanity", 17),
        ("The Witcher's Code", 27),
        ("Lesser of Two Evils", 36),
        ("Friendship in the Wild", 44),
        ("Part II: Free Will", 50),
        ("Destiny, Fate, and the Law", 51),
        ("Compatibilism and the Law", 60),
        ("Silver or Steel?", 67),
        ("Nothing Is Ever Black or White", 75),
        ("Part III: Feminism", 83),
        ("This Is the Version of Myself I Have to Be", 84),
        ("They Took My Choice, So I Took Yours", 95),
        ("Ciri's Agency and Autonomy", 103),
        ("Part IV: Race and Culture", 112),
        ("Race and Racism in the World of the Witcher", 113),
        ("Disadvantage, Demeaning, and Discrimination", 119),
        ("I'm Part Elf, I'm Part Human", 127),
        ("Part V: Magic", 137),
        ("Magic and the Elder Speech", 138),
        ("Worlds within Words", 146),
        ("Between Two Camps in the Witcher", 155),
        ("Witch Hunts Will Never Be Over", 165),
        ("Part VI: Postmodernism", 174),
        ("The Witcher as Postmodern Fairy Tale", 175),
        ("Shocks of Destiny", 185),
        ("Post-Apocalyptic Perspectives", 192),
        ("Part VII: Political Philosophy", 203),
        ("King Foltest, John Locke, and the Social Contract", 204),
        ("Stolen Mutagens", 212),
        ("Sometimes You Have to Fight", 221),
        ("Origin and Desires as Monster Makers in the Witcher", 230),
        ("The Witcher and the Monstrous Feminine", 242),
        ("The Dialectics of Monstrosity", 249),
        ("Index", 258),
    ],
    "235 - The Philosophy of TV Noir": [
        ("Front matter", 0),
        ("Preface and Acknowledgments", 8),
        ("An Introduction to the Philosophy of TV Noir", 10),
        ("Part 1: Realism, Relativism, and Moral Ambiguity", 40),
        ("Dragnet, Film Noir, and Postwar Realism", 42),
        ("Naked City: The Relativist Turn in TV Noir", 58),
        ("John Drake in Greeneland: Noir Themes in Secret Agent", 78),
        ("Action and Integrity in The Fugitive", 92),
        ("Part 2: Existentialism, Nihilism, and the Meaning of Life", 102),
        ("Noir et Blanc in Color: Existentialism and Miami Vice", 104),
        ("24 and the Existential Man of Revolt", 124),
        ("Carnivale Knowledge: Give Me That Old-time Noir Religion", 140),
        ("The Sopranos, Film Noir, and Nihilism", 152),
        ("Part 3: Crime Scene Investigation and the Logic of Detection", 168),
        ("CSI and the Art of Forensic Detection", 170),
        ("Detection and the Logic of Abduction in The X-Files", 188),
        ("Part 4: Autonomy, Selfhood, and Interpretation", 210),
        ("Kingdom of Darkness: Autonomy and Conspiracy in The X-Files and Millennium", 212),
        ("The Prisoner and Self-Imprisonment", 238),
        ("Twin Peaks, Noir, and Open Interpretation", 256),
        ("List of Contributors", 270),
        ("Index", 274),
    ],
}


def main():
    for book, items in BOOKS.items():
        pdf_path = checked_path(PDF_DIR, book + ".pdf")
        out_dir = checked_path(MD_ROOT, book)
        out_dir.mkdir(parents=True, exist_ok=True)
        for old in out_dir.glob("ch*.md"):
            old.unlink()
        doc = fitz.open(str(pdf_path))
        starts = [it[1] for it in items]
        if starts != sorted(starts) or len(set(starts)) != len(starts):
            raise SystemExit(f"{book}: starts not strictly monotonic")
        pages = [clean(doc[i].get_text()) for i in range(doc.page_count)]
        n_ch = 0
        total = 0
        print(f"===== {book}")
        for idx, (title, a) in enumerate(items):
            b = starts[idx + 1] if idx + 1 < len(starts) else doc.page_count
            body = "\n\n".join(pages[a:b])
            words = len(body.split())
            n_ch += 1
            total += words
            fname = "ch%02d - %s.md" % (n_ch, safe_stem(title))
            header = "# %s\n\n*Source: %s — chapter %d*\n\n" % (title, book, n_ch)
            (out_dir / fname).write_text(header + body + "\n", encoding="utf-8")
            print("  ch%02d  pdf %3d-%3d  %6d w  %s" % (n_ch, a, b - 1, words, title[:64]))
        print(f"  chapters: {n_ch}  total words: {total}")
        doc.close()


if __name__ == "__main__":
    main()
