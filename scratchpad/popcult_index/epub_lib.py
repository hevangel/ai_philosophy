"""Shared helpers: parse EPUB spine/TOC, strip HTML to text."""
import re
import zipfile
import xml.etree.ElementTree as ET

NS = {
    "ocf": "urn:oasis:names:tc:opendocument:xmlns:container",
    "opf": "http://www.idpf.org/2007/opf",
    "ncx": "http://www.daisy.org/z3986/2005/ncx/",
}

MAX_XML_BYTES = 4 * 1024 * 1024
DTD_RE = re.compile(rb"<!DOCTYPE|<!ENTITY", re.I)


def safe_fromstring(data):
    """Parse XML only after rejecting DTD/entity declarations (billion-laughs guard)."""
    if len(data) > MAX_XML_BYTES:
        raise ValueError("xml too large")
    if DTD_RE.search(data):
        raise ValueError("xml contains DOCTYPE/ENTITY; refusing to parse")
    return ET.fromstring(data)


def url_unquote(s):
    from urllib.parse import unquote
    return unquote(s)


def load_opf(zf):
    container = zf.read("META-INF/container.xml")
    root = safe_fromstring(container)
    opf_path = None
    for rf in root.iter("{%s}rootfile" % NS["ocf"]):
        opf_path = rf.get("full-path")
        break
    if opf_path is None:
        raise ValueError("no rootfile in container.xml")
    opf_dir = opf_path.rsplit("/", 1)[0] + "/" if "/" in opf_path else ""
    opf_root = safe_fromstring(zf.read(opf_path))
    manifest = {}
    for item in opf_root.iter("{%s}item" % NS["opf"]):
        manifest[item.get("id")] = {
            "href": url_unquote(item.get("href")),
            "media-type": item.get("media-type", ""),
            "properties": item.get("properties", "") or "",
        }
    spine = []
    for itemref in opf_root.iter("{%s}itemref" % NS["opf"]):
        if itemref.get("linear") == "no":
            continue
        idref = itemref.get("idref")
        if idref in manifest:
            spine.append(manifest[idref])
    return opf_dir, manifest, spine


def load_toc_titles(zf, opf_dir, manifest):
    """Return {href_basename: title} from toc.ncx or nav.xhtml, best effort."""
    titles = {}
    # EPUB2 toc.ncx
    ncx_id = None
    for iid, m in manifest.items():
        if m["media-type"] == "application/x-dtbncx+xml":
            ncx_id = iid
            break
    if ncx_id:
        try:
            root = safe_fromstring(zf.read(opf_dir + manifest[ncx_id]["href"]))
            for np in root.iter("{%s}navPoint" % NS["ncx"]):
                label = None
                for nl in np.iter("{%s}text" % NS["ncx"]):
                    label = nl.text
                    break
                content = np.find("{%s}content" % NS["ncx"])
                if content is not None and label:
                    src = content.get("src", "").split("#")[0]
                    titles[url_unquote(src).rsplit("/", 1)[-1]] = label.strip()
        except Exception:
            pass
    # EPUB3 nav (regex-based, no entity expansion)
    for iid, m in manifest.items():
        if "nav" in m["properties"]:
            try:
                raw = zf.read(opf_dir + m["href"]).decode("utf-8", "replace")
            except Exception:
                continue
            for mt in re.finditer(r"<a[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>",
                                  raw, re.S | re.I):
                href, text = mt.group(1), mt.group(2)
                text = re.sub(r"<[^>]+>", " ", text)
                text = html_unescape(text).strip()
                key = url_unquote(href.split("#")[0]).rsplit("/", 1)[-1]
                if text and key and key not in titles:
                    titles[key] = text
    return titles


def html_unescape(s):
    import html as _html
    return _html.unescape(s)


TAG_RE = re.compile(r"<[^>]+>")


def doc_text(zf, opf_dir, href):
    """Extract text word count + raw body HTML from a spine doc."""
    path = opf_dir + href
    try:
        raw = zf.read(path)
    except KeyError:
        return None
    try:
        html = raw.decode("utf-8")
    except UnicodeDecodeError:
        html = raw.decode("latin-1", "replace")
    body_m = re.search(r"<body[^>]*>(.*)</body>", html, re.S | re.I)
    if body_m is None:
        return None
    body = body_m.group(1)
    # Remove scripts/styles/svg and comments
    body = re.sub(r"<(script|style|svg)[^>]*>.*?</\1>", " ", body, flags=re.S | re.I)
    body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    text = html_unescape(TAG_RE.sub(" ", body))
    words = re.findall(r"[A-Za-z\u00C0-\u024F']+", text)
    return {"words": len(words), "raw": body}


def book_stats(epub_path):
    """Return per-spine-doc word counts and toc titles for an epub."""
    zf = zipfile.ZipFile(epub_path)
    opf_dir, manifest, spine = load_opf(zf)
    titles = load_toc_titles(zf, opf_dir, manifest)
    docs = []
    for m in spine:
        is_html = ("html" in m["media-type"]
                   or m["href"].lower().endswith((".xhtml", ".html", ".htm")))
        if not is_html:
            continue
        href_base = m["href"].rsplit("/", 1)[-1]
        info = doc_text(zf, opf_dir, m["href"])
        if info is None:
            continue
        docs.append({
            "href": m["href"],
            "base": href_base,
            "title": titles.get(href_base, ""),
            "words": info["words"],
        })
    zf.close()
    return docs
