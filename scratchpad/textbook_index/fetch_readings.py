"""Fetch readings for reconstructed anthologies into corpus-standard markdown.

Input: a manifest JSON next to this script (007_readings.json / 012_readings.json):
  [{"n": 1, "file": "ch01.md", "title": "...", "author": "...",
    "status": "public_domain" | "open" | "stub",
    "url": "https://..." (text URL; empty for stub),
    "source_page": "https://..." (page the text was found from),
    "license_note": "..."}]
Readings with status "stub" or empty url become citation stubs; the rest are
downloaded (plain text/html -> markdown-ish text), validated, and written with
a provenance header.

Security: only http/https; host must be public (no localhost/private/reserved
addresses); all paths stay inside the corpus markdown root via checked_path.
"""
import ipaddress
import json
import re
import socket
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

SCRIPT_DIR = Path(__file__).resolve().parent
CORPUS_MD_ROOT = Path(r"B:\ai_philosophy\data\philosophy_readings\markdown").resolve()
BOOK_DIRS = {
    "007_readings.json": "007 - Human Knowledge - Classical and Contemporary Approaches",
    "012_readings.json": "012 - Contemporary Political Philosophy - An Anthology",
}
MAX_BYTES = 3 * 1024 * 1024
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) research-corpus-fetch"

TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.S | re.I)


def checked_path(base, rel):
    p = (base / rel).resolve()
    b = base.resolve()
    import os
    if p.anchor != b.anchor or not (str(p) == str(b)
                                    or str(p).startswith(str(b) + os.sep)):
        raise ValueError("resolved path outside allowed root: %s" % p)
    return p


def host_allowed(url):
    pu = urlparse(url)
    if pu.scheme not in ("http", "https"):
        return False, "scheme %r" % pu.scheme
    host = pu.hostname or ""
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError as e:
        return False, "dns %s" % e
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (ip.is_private or ip.is_loopback or ip.is_link_local
                or ip.is_reserved or ip.is_multicast or ip.is_unspecified):
            return False, "address %s not public" % ip
    return True, host


def fetch(url):
    ok, why = host_allowed(url)
    if not ok:
        raise ValueError("blocked url %s: %s" % (url, why))
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=60) as r:
        data = r.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("too large: %s" % url)
    return data


def to_text(data):
    if data[:5] == b"%PDF-":
        import io
        import fitz
        doc = fitz.open(stream=data, filetype="pdf")
        try:
            pages = [page.get_text("text") for page in doc]
        finally:
            doc.close()
        text = "\n\n".join(pages)
        import html as _html2
        return re.sub(r"[ \t]+", " ", _html2.unescape(text)).strip()
    if data[:5] == b"\xd0\xcf\x11\xe0":
        raise ValueError("binary office payload")
    for enc in ("utf-8", "latin-1"):
        try:
            s = data.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    s = SCRIPT_RE.sub(" ", s)
    s = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</h[1-6]>|</li>|</blockquote>", "\n\n", s)
    s = re.sub(r"(?i)<h([1-6])[^>]*>", lambda m: "\n\n" + "#" * int(m.group(1)) + " ", s)
    s = TAG_RE.sub(" ", s)
    import html as _html
    s = _html.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def gutenberg_trim(text):
    """Strip Project Gutenberg boilerplate header/footer."""
    m = re.search(r"\*\*\* ?START OF (THE|THIS) PROJECT GUTENBERG EBOOK[^*]*\*\*\*", text)
    if m:
        text = text[m.end():]
        m2 = re.search(r"\*\*\* ?END OF (THE|THIS) PROJECT GUTENBERG EBOOK", text)
        if m2:
            text = text[:m2.start()]
    return text.strip()


def write_reading(book_dir, entry, body=None):
    fname = entry.get("file") or ("ch%02d.md" % entry["n"])
    fpath = checked_path(book_dir, fname)
    header = [
        "# %s" % entry["title"],
        "",
        "*%s*" % entry["author"] if entry.get("author") else "",
        "",
    ]
    if body is None:
        header[-2] = ("*Reconstruction stub — the reading is under copyright and no"
                      " openly available copy was located. Citation: %s. Best access"
                      " point: %s" % (entry.get("citation", "see toc.md"),
                                      entry.get("source_page", "—")))
        body = entry.get("note", "")
    else:
        header += ["*Source: %s (%s; fetched %s)*" % (
            entry.get("url", ""), entry.get("license_note", "openly available"),
            "2026-10-04"), ""]
    lines = [ln for ln in header]
    fpath.write_text("\n".join(lines) + "\n" + body.strip() + "\n", encoding="utf-8")
    return fpath


def main():
    results = []
    for manifest_name, book_dir_name in BOOK_DIRS.items():
        manifest_path = checked_path(SCRIPT_DIR, manifest_name)
        if not manifest_path.exists():
            results.append("%s: manifest missing, skipped" % manifest_name)
            continue
        entries = json.loads(manifest_path.read_text(encoding="utf-8"))
        book_dir = checked_path(CORPUS_MD_ROOT, book_dir_name)
        book_dir.mkdir(parents=True, exist_ok=True)
        n_ok = n_stub = n_fail = 0
        for e in entries:
            try:
                if e.get("status") != "stub" and e.get("url"):
                    raw = fetch(e["url"])
                    text = to_text(raw)
                    if "gutenberg" in e["url"].lower():
                        text = gutenberg_trim(text)
                    if len(text) < 800:
                        raise ValueError("fetched text too short (%d chars)" % len(text))
                    write_reading(book_dir, e, body=text)
                    n_ok += 1
                    results.append("%s/%s: fetched %d chars from %s" % (
                        manifest_name, e["file"], len(text), urlparse(e["url"]).netloc))
                else:
                    write_reading(book_dir, e)
                    n_stub += 1
            except Exception as ex:
                n_fail += 1
                results.append("%s/%s: FAIL %r — wrote stub instead" % (
                    manifest_name, e.get("file"), ex))
                try:
                    write_reading(book_dir, e)
                except Exception:
                    pass
        results.append("%s: %d fetched, %d stubs, %d failed->stub" % (
            manifest_name, n_ok, n_stub, n_fail))
    print("\n".join(results))


if __name__ == "__main__":
    main()
