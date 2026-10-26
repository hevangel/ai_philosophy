"""Validate downloaded PDFs are actually books, not journal articles.

For every pdf in data/philosophy_readings/pdf: open with PyMuPDF, report
page count, text-layer presence, and first-page snippet. Flags anything
with < 60 pages as a probable article (observed junk: 2/3/6/12/19 pages;
the 100-page fake was a magazine — anything under 60 is auto-suspect,
60-130 is flagged for review). Does NOT delete anything; prints a verdict
table and writes pdf_validation.json next to the corpus manifest.
"""
import json
from pathlib import Path

import fitz

PDF_DIR = Path(r"B:\ai_philosophy\data\philosophy_readings\pdf")
REPORT = Path(r"B:\ai_philosophy\sratchpad\textbook_index\pdf_validation.json")


def main():
    rows = []
    for p in sorted(PDF_DIR.glob("*.pdf")):
        entry = {"file": p.name, "size_kb": p.stat().st_size // 1024}
        try:
            doc = fitz.open(str(p))
            n = len(doc)
            entry["pages"] = n
            text = ""
            for i in range(min(3, n)):
                text += doc[i].get_text()
            entry["text_chars_first3"] = len(text)
            entry["first_page"] = " ".join(text.split())[:220]
            doc.close()
            if n < 60:
                entry["verdict"] = "ARTICLE (auto: <60 pages)"
            elif n < 130:
                entry["verdict"] = "REVIEW (60-129 pages)"
            else:
                entry["verdict"] = "book-sized"
        except Exception as e:
            entry["pages"] = None
            entry["verdict"] = "UNREADABLE: %r" % e
        rows.append(entry)
        print("%-70s %6d kB  %s" % (p.name[:70], entry["size_kb"], entry["verdict"]))
        if entry.get("first_page"):
            print("    p1: %s" % entry["first_page"][:150])
    REPORT.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    print("report -> %s" % REPORT)


if __name__ == "__main__":
    main()
