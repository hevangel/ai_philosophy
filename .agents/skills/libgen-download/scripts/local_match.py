"""Match a books.json list against a local ebook library index and copy matches.

Skips downloads for books you already own: reads a plain-text index of file
paths (one per line, e.g. `find /e/ebook -iname '*.epub' > index.txt`), fuzzy-
matches normalized filenames against each book's title, resolves conflicts (a
file claimed by several books goes to the best score), copies matches into the
destination folder under their final numbered names, and writes a
match_report.json usable as --skip-report by batch_download.py / chunk_loop.py.

Usage:
  py -3 local_match.py --books books.json --index library_index.txt --dest ./corpus
"""
import argparse
import json
import re
import shutil
import unicodedata
from pathlib import Path


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("&", " and ").replace("'", "").replace("\u2019", "")
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


NOISE = [
    r"\(z[- ]?lib[^)]*\)", r"\(libgen[^)]*\)", r"\(b[- ]?ok[^)]*\)",
    r"\[.*?\]", r"\(1\)$", r"\(2\)$", r"\(3\)$", r"\(ok\)$", r"\(fix\)$",
    r"\(fixed\)$", r"\(converted\)$", r"\(epub\)$", r"\(compressed\)$",
]


def file_title_part(path: str) -> str:
    """Best-effort extraction of the title portion from a library file path."""
    name = Path(path).name
    name = re.sub(r"\.\w+$", "", name)  # drop extension
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


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--books", type=Path, required=True)
    ap.add_argument("--index", type=Path, required=True,
                    help="plain-text file of local library paths, one per line")
    ap.add_argument("--dest", required=True, help="folder to copy matched files into")
    ap.add_argument("--report", type=Path,
                    help="report json (default: match_report.json next to --books)")
    args = ap.parse_args()

    books = json.loads(args.books.read_text(encoding="utf-8"))
    dest = Path(args.dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    report_path = args.report or args.books.with_name("match_report.json")

    index = args.index.read_text(encoding="utf-8").splitlines()
    index = [l.strip() for l in index if l.strip()]
    # normalize git-bash style paths (/e/foo) to windows (E:/foo)
    index = [re.sub(r"^/([a-z])/", lambda m: m.group(1).upper() + ":/", l) for l in index]

    # Build pair scores
    pairs = []  # (score, book_num, file_idx)
    for book in books:
        bn_main = norm(book["title"])
        bn_full = norm(book.get("full_title") or book["title"])
        for fi, f in enumerate(index):
            fn = norm(file_title_part(f))
            s = score_match(bn_main, bn_full, fn)
            if s > 0:
                pairs.append((s, book["num"], fi))

    # Resolve conflicts: a file claimed by multiple books goes to the highest score,
    # ties broken by longer book title (more specific entry wins).
    by_file = {}
    for s, num, fi in pairs:
        by_file.setdefault(fi, []).append((s, num))

    full_by_num = {b["num"]: (b.get("full_title") or b["title"]) for b in books}
    file_owner = {}
    for fi, cands in by_file.items():
        cands.sort(key=lambda t: (-t[0], -len(full_by_num[t[1]])))
        file_owner[fi] = cands[0]

    # Best file per book among files it owns
    best = {}  # num -> (score, file_idx)
    for fi, (s, num) in file_owner.items():
        if num not in best or s > best[num][0]:
            best[num] = (s, fi)

    report = []
    copied = 0
    for book in books:
        num = book["num"]
        title = book.get("full_title") or book["title"]
        entry = {"num": num, "title": title, "status": "no_match", "file": None}
        if num in best:
            s, fi = best[num]
            src = Path(index[fi])
            safe = lambda t: re.sub(r'[\\/:*?"<>|]', "", t).strip()
            final_name = (f"{num:03d} - {safe(book['title'])}"
                          + (f" - {safe(book['subtitle'])}" if book.get("subtitle") else "")
                          + src.suffix.lower())
            dst = dest / final_name
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

    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    n_failed = sum(1 for r in report if r["status"] == "copy_failed")
    print(f"Copied {copied} books from local library -> {dest}")
    print(f"No local match: {len(books) - copied - n_failed} (will need download)")
    if n_failed:
        print(f"Copy failures: {n_failed}")

    # Show a sample of matches for spot checking
    print("\nSample matches:")
    for r in [r for r in report if r["status"] == "copied"][:10]:
        print(f"  #{r['num']:03d} [{r.get('score')}] {r['title'][:60]}  <-  {Path(r['source']).name[:50]}")


if __name__ == "__main__":
    main()
