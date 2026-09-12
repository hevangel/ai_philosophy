#!/usr/bin/env python3
"""Convert a philosophy article markdown file into submission formats.

Usage (run from anywhere; paths are file paths):
  py -3 md_to_docx.py input.md output.docx [--cjk]        # DOCX via pandoc, CJK-safe fonts
  py -3 md_to_docx.py input.md output.pdf  [--cjk]        # DOCX then export PDF via MS Word COM
  py -3 md_to_docx.py input.md main.tex    --latex        # LaTeX source (for arXiv)

DOCX is the canonical journal format (Editorial Manager / ScholarOne / CN portals all take
it). PDF export requires desktop Microsoft Word (pywin32). LaTeX is only for arXiv-class
venues; philosophy journals almost never want TeX.
"""
import argparse
import re
import sys
from pathlib import Path

CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")


def clean_markdown(text: str) -> str:
    """Strip chat-export artifacts and normalize line endings."""
    text = text.replace("\r\n", "\n")
    # citeturn0af1... style tokens from chat exports
    text = re.sub(r"\bturn\d[a-z0-9]*\b", "", text)
    text = re.sub(r"\bciteturn\S*", "", text)
    # collapse 3+ blank lines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def pandoc_convert(src: Path, dst: Path, to_format: str, cjk: bool) -> None:
    import pypandoc

    args = ["--standalone"]
    if to_format == "docx":
        args += ["--from", "markdown+footnotes+smart"]
        if cjk:
            args += ["--metadata", "lang=zh-CN"]
        else:
            args += ["--metadata", "lang=en-US"]
    if to_format == "latex":
        args += ["--from", "markdown+footnotes", "--top-level-division=section"]
    pypandoc.convert_file(str(src), to_format, outputfile=str(dst), extra_args=args)


def set_docx_fonts(docx_path: Path, cjk: bool) -> None:
    """Post-pass: journal-friendly body font. Latin: Times New Roman; East Asian: SimSun."""
    from docx import Document
    from docx.oxml.ns import qn

    doc = Document(str(docx_path))
    latin = "Times New Roman"
    east = "宋体" if cjk else "Times New Roman"

    def fix_style(style):
        try:
            style.font.name = latin
        except Exception:
            return
        rpr = style.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = rpr.makeelement(qn("w:rFonts"), {})
            rpr.append(rfonts)
        rfonts.set(qn("w:ascii"), latin)
        rfonts.set(qn("w:hAnsi"), latin)
        rfonts.set(qn("w:eastAsia"), east)

    for style in doc.styles:
        fix_style(style)
    for para in doc.paragraphs:
        for run in para.runs:
            rpr = run._element.get_or_add_rPr()
            rfonts = rpr.find(qn("w:rFonts"))
            if rfonts is None:
                rfonts = rpr.makeelement(qn("w:rFonts"), {})
                rpr.append(rfonts)
            rfonts.set(qn("w:eastAsia"), east)
    doc.save(str(docx_path))


def docx_to_pdf(docx_path: Path, pdf_path: Path) -> None:
    """Export via desktop Word. Raises with an actionable message if unavailable."""
    try:
        import win32com.client
    except ImportError as e:
        raise SystemExit(
            "pywin32 not available. Export the DOCX to PDF manually in Word, or "
            "`py -3 -m pip install --user pywin32`."
        ) from e
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        document = word.Documents.Open(str(docx_path.resolve()))
        document.SaveAs2(str(pdf_path.resolve()), FileFormat=17)  # wdFormatPDF
        document.Close(False)
    finally:
        word.Quit()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--cjk", action="store_true", help="force Chinese typography (auto-detected otherwise)")
    ap.add_argument("--latex", action="store_true", help="output LaTeX instead of DOCX")
    ap.add_argument("--pdf", action="store_true", help="also produce a PDF via Word COM (DOCX kept)")
    a = ap.parse_args()

    src = Path(a.input)
    dst = Path(a.output)
    if not src.exists():
        raise SystemExit(f"input not found: {src}")

    text = clean_markdown(src.read_text(encoding="utf-8"))
    tmp = src.with_suffix(".submittmp.md")
    tmp.write_text(text, encoding="utf-8")
    try:
        cjk = a.cjk or bool(CJK_RE.search(text[:5000]))

        if a.latex:
            pandoc_convert(tmp, dst, "latex", cjk)
            print(f"wrote {dst}")
            return 0

        docx_dst = dst
        if a.pdf and dst.suffix.lower() == ".pdf":
            docx_dst = dst.with_suffix(".docx")
        if docx_dst.suffix.lower() != ".docx":
            raise SystemExit("output must be .docx (or .pdf with --pdf)")

        pandoc_convert(tmp, docx_dst, "docx", cjk)
        set_docx_fonts(docx_dst, cjk)
        print(f"wrote {docx_dst}")

        if a.pdf:
            pdf_out = dst if dst.suffix.lower() == ".pdf" else dst.with_suffix(".pdf")
            docx_to_pdf(docx_dst, pdf_out)
            print(f"wrote {pdf_out}")
    finally:
        tmp.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
