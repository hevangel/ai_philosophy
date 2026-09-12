"""Try book #2's full download chain against a chosen tunnel egress."""
import re
import secrets
import sys
import time
from pathlib import Path

import requests
from proxy_pool import ProxyPool

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
MD5_RE = re.compile(r"^[0-9a-f]{32}$")
KEY_RE = re.compile(r"^[A-Z0-9]{6,20}$")
rng = secrets.SystemRandom()
HOST_IDX = int(sys.argv[1]) if len(sys.argv) > 1 else 1  # 0=oc1..3=oc4, 4=horace
DEST = Path(r"B:\ai_philosophy\philosophy_pop_culture").resolve()


def parse_search_html(html: str):
    results = []
    m = re.search(r'<table[^>]*id="tablelibgen"[^>]*>(.*?)</table>', html, re.S)
    if not m:
        return results
    body = m.group(1)
    tb = re.search(r"<tbody>(.*)</tbody>", body, re.S)
    rows = re.findall(r"<tr>(.*?)</tr>", tb.group(1), re.S) if tb else []
    for row in rows:
        tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        if len(tds) < 9:
            continue
        title_m = re.search(r'href="edition\.php\?id=\d+[^"]*"[^>]*>(.*?)</a>', tds[0], re.S)
        title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip() if title_m else ""
        fileid_m = re.search(r'href="/file\.php\?id=(\d+)"', tds[6])
        md5_m = re.search(r"ads\.php\?md5=([0-9a-f]{32})", tds[8])
        ext = re.sub(r"<[^>]+>", "", tds[7]).strip().lower()
        results.append({"title": title, "ext": ext,
                        "file_id": fileid_m.group(1) if fileid_m else None,
                        "md5": md5_m.group(1) if md5_m else None})
    return results


def main() -> None:
    with ProxyPool(["oc1.hevangel.com", "oc2.hevangel.com", "oc3.hevangel.com",
                    "oc4.hevangel.com", "horace.org"]) as pool:
        port = int(pool.urls[HOST_IDX].rsplit(":", 1)[1])
        host = ["oc1", "oc2", "oc3", "oc4", "horace"][HOST_IDX]
        print(f"egress: {host} port {port}", flush=True)
        s = requests.Session()
        s.headers.update({"User-Agent": UA})
        s.proxies.update({"http": f"socks5h://127.0.0.1:{port}",
                          "https": f"socks5h://127.0.0.1:{port}"})

        r = s.get("https://libgen.li/index.php",
                  params={"req": "Simpsons and Philosophy: The D'oh! of Homer", "res": "25"},
                  timeout=60)
        res = parse_search_html(r.text)
        epubs = [x for x in res if x["md5"] and x["ext"] == "epub"]
        print(f"search: {r.status_code}, {len(res)} rows, {len(epubs)} epubs", flush=True)
        if not epubs:
            return
        book = epubs[0]
        print(f"target: {book['title'][:60]} [{book['ext']}] file_id={book['file_id']}", flush=True)

        time.sleep(rng.uniform(8, 15))
        if book["file_id"]:
            s.get("https://libgen.li/file.php", params={"id": book["file_id"]}, timeout=60)
            time.sleep(rng.uniform(3, 6))
        r0 = s.get("https://libgen.li/ads.php", params={"md5": book["md5"]}, timeout=60)
        m = re.search(r'href="get\.php\?md5=([0-9a-f]{32})&amp;key=([A-Z0-9]{6,20})"', r0.text)
        print(f"ads: {r0.status_code} {len(r0.text)}B key={'YES' if m else 'NO'}", flush=True)
        if not m:
            return
        md5_hex, key = m.group(1), m.group(2)
        if not (MD5_RE.match(md5_hex) and KEY_RE.match(key)):
            print("key whitelist failed", flush=True)
            return
        time.sleep(rng.uniform(6, 12))
        r = s.get("https://libgen.li/get.php", params={"md5": md5_hex, "key": key},
                  headers={"Referer": "https://libgen.li/ads.php"}, timeout=(30, 180))
        print(f"get: {r.status_code} {r.headers.get('content-type')} len={r.headers.get('content-length')}",
              flush=True)
        if r.status_code == 200 and len(r.content) > 15000 and r.content[:2] == b"PK":
            out = (DEST / "002 - The Simpsons and Philosophy - The Doh! of Homer.epub").resolve()
            if out.parent != DEST:
                raise ValueError("bad destination")
            out.write_bytes(r.content)
            print(f"SAVED {out.name} ({len(r.content)//1024} kB)", flush=True)


if __name__ == "__main__":
    main()
