"""Match bibliography books against the local E:\ebook epub index and copy matches.

Writes match_report.json with per-book decision: copied / ambiguous / no match.
"""
import json
import re
import shutil
import unicodedata
from pathlib import Path

BATCH = Path(r"B:\ai_philosophy\sratchpad\libgen_batch")
DEST = Path(r"B:\ai_philosophy\philosophy_pop_culture")

books = json.loads((BATCH / "books.json").read_text(encoding="utf-8"))
index = (BATCH.parent / "ebook_library_index.txt").read_text(encoding="utf-8").splitlines()
index = [l.strip() for l in index if l.strip()]
# normalize git-bash style paths (/e/foo) to windows (E:/foo)
index = [re.sub(r"^/([a-z])/", lambda m: m.group(1).upper() + ":/", l) for l in index]

NOISE = [
    r"\(z[- ]?lib[^)]*\)", r"\(libgen[^)]*\)", r"\(b[- ]?ok[^)]*\)",
    r"\[.*?\]", r"\(1\)$", r"\(2\)$", r"\(3\)$", r"\(ok\)$", r"\(fix\)$",
    r"\(fixed\)$", r"\(converted\)$", r"\(epub\)$", r"\(compressed\)$",
]


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("&", " and ").replace("'", "").replace("’", "")
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def file_title_part(path: str) -> str:
    """Best-effort extraction of the title portion from a library file path."""
    name = Path(path).name
    name = re.sub(r"\.epub$", "", name, flags=re.I)
    name = re.sub(r"\s*-\s*libgen[^-]*$", "", name, flags=re.I)
    for pat in NOISE:
        name = re.sub(pat, "", name, flags=re.I)
    # "Title - Author" pattern: split on ' - ' and keep first chunk if the rest looks like a name
    parts = name.split(" - ")
    if len(parts) > 1:
        # if later chunks look like author names (short, no colon), drop them
        keep = [parts[0]]
        for p in parts[1:]:
            if ":" in p or len(p) > 60:
                keep.append(p)
            else:
                break
        name = " - ".join(keep)
    # Calibre style: "Title (Series Name)" — drop the parenthetical for matching
    name = re.sub(r"\s*\([^)]*\)\s*$", "", name)
    return name.strip()


def score_match(book_norm_main: str, book_norm_full: str, file_norm: str) -> int:
    """Score how well a normalized filename matches a book. 0 = no match."""
    if not book_norm_main:
        return 0
    if book_norm_full and len(book_norm_full) > len(book_norm_main):
        if book_norm_full == file_norm or re.search(r"(^| )" + re.escape(book_norm_full) + r"( |$)", file_norm):
            return 100
    # main title as prefix with clean boundary, or exact whole match
    if file_norm == book_norm_main:
        return 90
    m = re.search(r"(^| )" + re.escape(book_norm_main) + r"( |$|:|-|\()", file_norm)
    if m:
        return 60
    return 0


# Build pair scores
pairs = []  # (score, book_num, file_idx)
for bi, book in enumerate(books):
    bn_main = norm(book["title"])
    bn_full = norm(book["full_title"])
    for fi, f in enumerate(index):
        fn = norm(file_title_part(f))
        s = score_match(bn_main, bn_full, fn)
        if s > 0:
            pairs.append((s, book["num"], fi, bn_main, bn_full, fn))

# Resolve conflicts: a file claimed by multiple books goes to the highest score,
# ties broken by longer book title (more specific entry wins).
by_file = {}
for s, num, fi, *rest in pairs:
    by_file.setdefault(fi, []).append((s, num))

file_owner = {}
for fi, cands in by_file.items():
    cands.sort(key=lambda t: (-t[0], -len(next(b["full_title"] for b in books if b["num"] == t[1]))))
    file_owner[fi] = cands[0]

# Best file per book among files it owns
best = {}  # num -> (score, file)
for fi, (s, num) in file_owner.items():
    if num not in best or s > best[num][0]:
        best[num] = (s, fi)

DEST.mkdir(parents=True, exist_ok=True)

report = []
copied = 0
for book in books:
    num = book["num"]
    entry = {"num": num, "title": book["full_title"], "status": "no_match", "file": None}
    if num in best:
        s, fi = best[num]
        src = Path(index[fi])
        safe_main = re.sub(r'[\\/:*?"<>|]', "", book["title"]).strip()
        safe_sub = re.sub(r'[\\/:*?"<>|]', "", book["subtitle"]).strip()
        final_name = f"{num:03d} - {safe_main}" + (f" - {safe_sub}" if safe_sub else "") + src.suffix.lower()
        dst = DEST / final_name
        try:
            if not dst.exists():
                shutil.copy2(src, dst)
            entry["status"] = "copied"
            entry["file"] = final_name
            entry["source"] = str(src)
            entry["score"] = s
            copied += 1
        except Exception as e:
            entry["status"] = "copy_failed"
            entry["error"] = str(e)
    report.append(entry)

(BATCH / "match_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

n_copied = sum(1 for r in report if r["status"] == "copied")
n_failed = sum(1 for r in report if r["status"] == "copy_failed")
print(f"Copied {copied} books from local library -> {DEST}")
print(f"No local match: {len(books) - n_copied - n_failed} (will need download)")
if n_failed:
    print(f"Copy failures: {n_failed}")

# Show a sample of matches for spot checking
print("\nSample matches:")
for r in [r for r in report if r["status"] == "copied"][:10]:
    print(f"  #{r['num']:03d} [{r.get('score')}] {r['title'][:60]}  <-  {Path(r['source']).name[:50]}")
