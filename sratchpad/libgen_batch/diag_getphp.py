"""Diagnose get.php: keyed flow via tunnel egress vs local, using requests."""
import re
import time

import requests
from proxy_pool import ProxyPool

MD5 = "8d23f0442eaa96b5d7e8641d984ad4ff"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
KEY_RE = re.compile(r"^md5=[0-9a-f]{32}&key=[A-Z0-9]{6,20}$")
ALLOWED_HOST = "libgen.li"


def make_session(port: int | None) -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    if port:
        proxies = {"http": f"socks5h://127.0.0.1:{port}",
                   "https": f"socks5h://127.0.0.1:{port}"}
        s.proxies.update(proxies)
    return s


def guarded_get(s: requests.Session, url: str, **kw) -> requests.Response:
    host = re.sub(r"^https?://", "", url).split("/", 1)[0].split(":")[0]
    if host != ALLOWED_HOST or not url.startswith(("http://", "https://")):
        raise ValueError(f"blocked non-{ALLOWED_HOST} request: {host}")
    return s.get(url, timeout=60, **kw)


def keyed_flow(port: int | None, label: str) -> None:
    print(f"--- {label} ---", flush=True)
    s = make_session(port)
    warm = guarded_get(s, f"https://{ALLOWED_HOST}/file.php", params={"id": "93668953"})
    print(f"  warmup file.php: {warm.status_code}", flush=True)
    time.sleep(5)
    r = s.get(f"https://{ALLOWED_HOST}/ads.php", params={"md5": MD5})
    m = re.search(r'href="(get\.php\?md5=[^"]+)"', r.text)
    print(f"  ads.php: {r.status_code} {len(r.text)}B, key link: {bool(m)}", flush=True)
    if not m:
        return
    path_query = m.group(1).replace("&amp;", "&")
    if not KEY_RE.match(path_query.split("?", 1)[1]):
        print(f"  key failed whitelist: {path_query[:60]!r}", flush=True)
        return

    time.sleep(8)
    r2 = s.get(f"https://{ALLOWED_HOST}/{path_query}",
               headers={"Referer": f"https://{ALLOWED_HOST}/ads.php?md5={MD5}"},
               stream=True)
    head = r2.raw.read(16, decode_content=True) if r2.ok else b""
    total = r2.headers.get("content-length")
    print(f"  get.php: {r2.status_code} len={total} head={head[:8]!r} ct={r2.headers.get('content-type')}",
          flush=True)
    r2.close()


with ProxyPool(["oc1.hevangel.com"]) as pool:
    if pool.urls:
        port = int(pool.urls[0].rsplit(":", 1)[1])
        keyed_flow(port, f"tunnel{port}")

time.sleep(8)
keyed_flow(None, "direct")
