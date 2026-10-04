"""Verify markdown/ folders are complete extractions of epub/ files.

Checks per book: folder exists, chapter file count == spine doc count,
per-chapter word volume multiset match, book-level word ratio.
Every read goes through checked_path(), which resolves the location and
verifies containment inside the corpus root before any read happens.
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from epub_lib import book_stats

ROOT = Path(r"B:\ai_philosophy\philosophy_pop_culture").resolve()
EPUB_DIR = ROOT / "epub"
MD_DIR = ROOT / "markdown"
REPORT_PATH = Path(r"B:\ai_philosophy\sratchpad\popcult_index\report.json").resolve()

CH_RE = re.compile(r"^ch(\d+)")
WORD_RE = re.compile(r"[A-Za-z\u00C0-\u024F']+")


def checked_path(base, rel):
    p = (base / rel).resolve()
    b = base.resolve()
    if os.path.commonpath([str(p), str(b)]) != str(b):
        raise ValueError("resolved path outside allowed root: %s" % p)
    return p


def safe_stem(stem):
    if not stem or stem in (os.curdir, os.pardir):
        raise ValueError("unsafe book stem: %r" % stem)
    if any(mark and mark in stem for mark in (os.sep, os.altsep or "", ":")):
        raise ValueError("unsafe book stem: %r" % stem)
    return stem


def md_chapters(md_dir, stem):
    folder = checked_path(md_dir, safe_stem(stem))
    out = []
    for entry in sorted(folder.iterdir()):
        m = CH_RE.match(entry.name)
        if m and entry.name.lower().endswith(".md"):
            text = entry.read_text(encoding="utf-8", errors="replace")
            body = re.sub(r"^#[^\n]*\n(?:\s*\n)*\*Source:[^\n]*\n(?:\s*\n)*",
                          "", text, count=1)
            out.append({"n": int(m.group(1)), "file": entry.name,
                        "words": len(WORD_RE.findall(body))})
    out.sort(key=lambda d: d["n"])
    return out


def close_multisets(a, b, tol=0.75, abs_tol=12):
    a = sorted(a)
    b = sorted(b)
    i = j = matched = 0
    while i < len(a) and j < len(b):
        if abs(a[i] - b[j]) <= max((1 - tol) * max(a[i], b[j], 1), abs_tol):
            matched += 1
            i += 1
            j += 1
        elif b[j] < a[i]:
            j += 1
        else:
            i += 1
    return matched


def main():
    epubs = sorted(p for p in EPUB_DIR.iterdir() if p.name.lower().endswith(".epub"))
    report = []
    n_fail = 0
    for ep in epubs:
        stem = safe_stem(ep.name[:-5])
        entry = {"book": stem, "status": "ok", "problems": []}
        try:
            docs = book_stats(checked_path(EPUB_DIR, ep.name))
        except Exception as e:
            entry["status"] = "epub-error"
            entry["problems"].append("epub parse failed: %r" % e)
            report.append(entry)
            n_fail += 1
            continue
        entry["spine_docs"] = len(docs)
        entry["epub_words"] = sum(d["words"] for d in docs)
        try:
            chapters = md_chapters(MD_DIR, stem)
        except (ValueError, OSError) as e:
            entry["status"] = "no-folder"
            entry["problems"].append("markdown unreadable: %s" % e)
            report.append(entry)
            n_fail += 1
            continue
        entry["md_files"] = len(chapters)
        entry["md_words"] = sum(c["words"] for c in chapters)
        ratio = entry["md_words"] / entry["epub_words"] if entry["epub_words"] else 0
        entry["word_ratio"] = round(ratio, 3)
        if entry["md_files"] != entry["spine_docs"]:
            entry["problems"].append(
                "chapter count %d != spine docs %d" % (entry["md_files"], entry["spine_docs"]))
        if ratio < 0.90:
            entry["problems"].append("book word ratio %.3f" % ratio)
        matched = close_multisets([d["words"] for d in docs], [c["words"] for c in chapters])
        entry["paired_chapters"] = matched
        if matched < 0.95 * entry["spine_docs"]:
            entry["problems"].append(
                "only %d/%d chapters match epub word volume" % (matched, entry["spine_docs"]))
        if entry["problems"]:
            entry["status"] = "incomplete"
            n_fail += 1
        report.append(entry)
    REPORT_PATH.write_text(json.dumps(report, indent=1), encoding="utf-8")
    print("books checked: %d  failures: %d" % (len(report), n_fail))
    for e in report:
        if e["status"] != "ok":
            print("FAIL %-70s %s" % (e["book"][:70], "; ".join(e["problems"])))


if __name__ == "__main__":
    main()
