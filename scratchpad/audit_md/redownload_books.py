"""Host orchestrator: for each repair-list book, download up to 3 alternative
epub candidates via the camoufox container (Files-tab flow, md5 exclusion,
title-token match), inspect spine granularity on the host, and install the
first clean (per-chapter-granular) edition.

Granularity rule: >=15 html spine docs AND max doc <=16000 words.
Fall back to the best candidate (most docs, smallest max) if none pass, and
report it as a fallback install. For book 242 additionally reject any
candidate whose content equals 224's epub (the duplicate-download bug).
Current bad epub is backed up before replace.

Usage: py -3 redownload_books.py [--only 25,50,...]
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

POP = Path(r"B:\ai_philosophy\scratchpad\popcult_index").resolve()
sys.path.insert(0, str(POP))
import epub_lib

HERE = Path(r"B:\ai_philosophy\scratchpad\audit_md").resolve()
FLOW = HERE / "flow_files.py"
EPUB_DIR = Path(r"B:\ai_philosophy\data\philosophy_pop_culture\epub").resolve()
BAD_DIR = HERE / "bad_epubs"
CONTAINER = "kb_camoufox"

REPAIR = [
    {"num": 25, "title": "The Beatles and Philosophy",
     "subtitle": "Nothing You Can Think that Can't Be Thought",
     "match": ["nothing you can think"]},
    {"num": 50, "title": "Facebook and Philosophy",
     "subtitle": "What's on Your Mind?",
     "match": ["what's on your mind", "wittkower"]},
    {"num": 203, "title": "Watchmen and Philosophy",
     "subtitle": "A Rorschach Test",
     "match": ["rorschach test", "watchmen"]},
    {"num": 208, "title": "X-Men and Philosophy",
     "subtitle": "Astonishing Insight and Uncanny Argument in the Mutant X-Verse",
     "match": ["uncanny argument", "x-men and philosophy"]},
    {"num": 224, "title": "Philosophy of Joss Whedon",
     "subtitle": "",
     "match": ["kowalski", "whedon"]},
    {"num": 242, "title": "Joss Whedon as Philosopher",
     "subtitle": "",
     "match": ["joss whedon as philosopher", "joss whedon"],
     "skip": True},
    {"num": 243, "title": "Philosophy Christopher Nolan",
     "subtitle": "",
     "match": ["eberl", "nolan"]},
    {"num": 251, "title": "Punk Rock and Philosophy",
     "subtitle": "Research and Destroy",
     "match": ["heter", "greene"]},
    {"num": 284, "title": "College Sex - Philosophy for Everyone",
     "subtitle": "Philosophers With Benefits",
     "match": ["philosophers with benefits", "college sex"]},
    {"num": 301, "title": "Comics as Philosophy",
     "subtitle": "",
     "match": ["comics as philosophy"]},
]


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def docker_exec_stdin(script, args="", timeout=3600):
    cmd = ["docker", "exec", "-i", CONTAINER, "python", "-"]
    if args:
        cmd.extend(args.split())
    r = subprocess.run(cmd, input=script.encode("utf-8"),
                       capture_output=True, timeout=timeout)
    return r


def container_cat(path):
    r = subprocess.run(["docker", "exec", CONTAINER, "cat", path],
                       capture_output=True, timeout=120)
    if r.returncode != 0:
        return None
    return r.stdout


def find_epub(num):
    for p in EPUB_DIR.iterdir():
        if p.name.startswith(f"{num:03d} - ") and p.name.lower().endswith(".epub"):
            return p
    return None


def sha256_of(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect_candidate(data):
    tmp = HERE / "inspect_tmp.epub"
    tmp.write_bytes(data)
    try:
        docs = epub_lib.book_stats(tmp)
        sizes = [d["words"] for d in docs]
        return {"spine_html": len(docs), "max_words": max(sizes, default=0),
                "total_words": sum(sizes),
                "first_titles": [d["title"][:30] for d in docs[:4]]}
    except Exception as e:
        return {"error": repr(e)[:100]}
    finally:
        tmp.unlink(missing_ok=True)


def granular(stats):
    return stats.get("spine_html", 0) >= 15 and stats.get("max_words", 10 ** 9) <= 16000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    only = {int(x) for x in args.only.split(",")} if args.only else None

    BAD_DIR.mkdir(exist_ok=True)
    summary = []
    for book in REPAIR:
        if only and book["num"] not in only:
            continue
        if book.get("skip"):
            continue
        num = book["num"]
        cur = find_epub(num)
        if cur is None:
            log(f"#{num:03d} no epub on disk, skipping")
            continue
        cur_sha = sha256_of(cur)
        log(f"=== #{num:03d} {book['title'][:50]} (current {cur.stat().st_size} B)")

        listing = dict(book)
        listing["exclude_size"] = [cur.stat().st_size]
        books_json = json.dumps([listing], ensure_ascii=False)
        up = subprocess.run(["docker", "exec", "-i", CONTAINER, "sh", "-c",
                             "mkdir -p /tmp/libgen_r /tmp/libgen_dl"
                             " && cat > /tmp/libgen_r/books.json"],
                            input=books_json.encode("utf-8"), capture_output=True, timeout=60)
        if up.returncode != 0:
            log(f"upload failed: {up.stderr!r}")
            continue

        r = docker_exec_stdin(FLOW.read_text(encoding="utf-8"),
                              args=f"{num} 3", timeout=2700)
        out = (r.stdout or b"").decode("utf-8", "replace") + (r.stderr or b"").decode("utf-8", "replace")
        for line in out.splitlines():
            if any(k in line for k in ("candidate", "done:", "error", "timeout",
                                       "invalid", "no token", "no results")):
                log("  " + line.strip())

        best = None
        installed = False
        for i in range(3):
            data = container_cat(f"/tmp/libgen_dl/cand_{num:03d}_{i}.epub")
            if not data or data[:2] != b"PK":
                continue
            if hashlib.sha256(data).hexdigest() == cur_sha:
                log(f"  cand {i}: identical to current file, rejecting")
                continue
            stats = inspect_candidate(data)
            log(f"  cand {i}: {stats}")
            if "error" in stats:
                continue
            if num == 242:
                ref = find_epub(224)
                if ref and stats.get("total_words") == sum(
                        d["words"] for d in epub_lib.book_stats(ref)):
                    log("  cand i content identical to 224, rejecting")
                    continue
            score = (stats["spine_html"], -stats["max_words"])
            if best is None or score > (best[1]["spine_html"], -best[1]["max_words"]):
                best = (data, stats, i)
            if granular(stats):
                backup = BAD_DIR / cur.name
                if not backup.exists():
                    shutil.copy2(cur, backup)
                cur.write_bytes(data)
                log(f"  INSTALLED cand {i}: spine={stats['spine_html']} "
                    f"max={stats['max_words']} total={stats['total_words']}")
                installed = True
                break
        if not installed:
            if best:
                data, stats, i = best
                backup = BAD_DIR / cur.name
                if not backup.exists():
                    shutil.copy2(cur, backup)
                cur.write_bytes(data)
                log(f"  FALLBACK-INSTALLED cand {i}: spine={stats['spine_html']} "
                    f"max={stats['max_words']} (no fully granular candidate)")
                summary.append((num, "fallback", stats))
            else:
                log(f"  NO CANDIDATE downloaded for #{num:03d} — left as is")
                summary.append((num, "none", {}))
        else:
            summary.append((num, "granular", stats))
        subprocess.run(["docker", "exec", CONTAINER, "sh", "-c",
                        f"rm -f /tmp/libgen_dl/cand_{num:03d}_*.epub"], timeout=60)
        time.sleep(30)

    print("\n=== SUMMARY ===")
    for num, how, stats in summary:
        print(f"#{num:03d}: {how} {stats if stats else ''}")


if __name__ == "__main__":
    main()
