"""Audit every pop-culture book's markdown extraction against its EPUB.

Flags:
  spine_mismatch   md file count != epub html spine doc count
  ratio_low        md total words / epub spine words < 0.80 (content loss)
  blob_syndrome    <=10 content chapters AND one file >=12000 words
                   (the book-002 calibre split-part failure mode)
  oversize_chapter max chapter >18000 words (likely merged chapters)
  empty_book       <500 content words (scan with no text layer)
  pdf_book         no epub on disk (hand-extracted PDF; structural checks only)
  truncate_hots    share of content chapters whose last line lacks terminal
                   punctuation (soft signal, reported for flagged books only)
  html_residue     md body still contains raw HTML tags

Writes report.json next to this script and prints a summary.
"""
import json
import re
from pathlib import Path

POP = Path(r"B:\ai_philosophy\scratchpad\popcult_index").resolve()
import sys
sys.path.insert(0, str(POP))
import epub_lib

ROOT = Path(r"B:\ai_philosophy\data\philosophy_pop_culture").resolve()
EPUB_DIR = ROOT / "epub"
MD_DIR = ROOT / "markdown"
REPORT = Path(r"B:\ai_philosophy\scratchpad\audit_md\report.json").resolve()

CH_RE = re.compile(r"^ch(\d+) - (.*?)\.md$", re.I)
WORD_RE = re.compile(r"[A-Za-z\u00C0-\u024F']+")
HEADER_RE = re.compile(r"^#[^\n]*\n(?:\s*\n)*\*Source:[^\n]*\n(?:\s*\n)*")
TERMINAL = tuple(".!?”\"’)]")


def chapter_words_and_tail(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    body = HEADER_RE.sub("", text, count=1)
    words = len(WORD_RE.findall(body))
    tail = body.strip()[-120:] if body.strip() else ""
    return words, tail, body


def main():
    epubs = {}
    for p in sorted(EPUB_DIR.iterdir()):
        if p.name.lower().endswith(".epub"):
            epubs[p.name[:-5]] = p
    report = []
    for book_dir in sorted(MD_DIR.iterdir()):
        if not book_dir.is_dir():
            continue
        chapters = []
        html_residue = 0
        no_terminal = 0
        for f in sorted(book_dir.iterdir()):
            m = CH_RE.match(f.name)
            if not m:
                continue
            words, tail, body = chapter_words_and_tail(f)
            if re.search(r"<(p|div|span|br|h[1-6])[\s>/]", body[:20000], re.I):
                html_residue += 1
            chapters.append({"n": int(m.group(1)), "file": f.name,
                             "title": m.group(2), "words": words, "tail": tail})
        chapters.sort(key=lambda c: c["n"])
        content = [c for c in chapters if c["words"] >= 200]
        total_words = sum(c["words"] for c in chapters)
        max_words = max((c["words"] for c in chapters), default=0)
        for c in content:
            if c["tail"] and not c["tail"].rstrip().endswith(TERMINAL):
                no_terminal += 1
        entry = {
            "book": book_dir.name,
            "md_files": len(chapters),
            "content_chapters": len(content),
            "content_words": sum(c["words"] for c in content),
            "total_words": total_words,
            "max_words": max_words,
            "html_residue_files": html_residue,
            "truncation_hot_ratio": round(no_terminal / len(content), 2) if content else None,
            "flags": [],
        }
        ep = epubs.get(book_dir.name)
        if ep is None:
            entry["pdf_book"] = True
            if entry["content_words"] < 500:
                entry["flags"].append("empty_book")
            report.append(entry)
            continue
        try:
            stats = epub_lib.book_stats(ep)
        except Exception as e:
            entry["flags"].append("epub_unreadable")
            entry["epub_error"] = repr(e)[:120]
            report.append(entry)
            continue
        spine_words = sum(d["words"] for d in stats)
        entry["epub_spine_html"] = len(stats)
        entry["epub_words"] = spine_words
        if len(chapters) != len(stats):
            entry["flags"].append("spine_mismatch")
        if spine_words > 1000 and total_words / spine_words < 0.80:
            entry["flags"].append("ratio_low")
        if entry["content_words"] < 500:
            entry["flags"].append("empty_book")
        if len(content) <= 10 and max_words >= 12000:
            entry["flags"].append("blob_syndrome")
        if max_words > 18000:
            entry["flags"].append("oversize_chapter")
        if html_residue:
            entry["flags"].append("html_residue")
        report.append(entry)

    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    flagged = [e for e in report if e["flags"]]
    print(f"books audited: {len(report)} | flagged: {len(flagged)}")
    for e in flagged:
        print(f"- {e['book'][:70]}")
        print(f"    md_files={e['md_files']} content={e['content_chapters']} "
              f"content_words={e['content_words']} max_words={e['max_words']} "
              f"flags={e['flags']}"
              + (f" spine={e.get('epub_spine_html')} epub_words={e.get('epub_words')}" 
                 if "epub_spine_html" in e else ""))


if __name__ == "__main__":
    main()
