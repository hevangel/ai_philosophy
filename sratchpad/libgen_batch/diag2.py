"""Capture get.php error body via oc1, and libgen.rs via horace egress."""
import re
import time

import requests
from proxy_pool import ProxyPool

MD5 = "8d23f0442eaa96b5d7e8641d984ad4ff"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")


def tunneled_session(port: int) -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    s.proxies.update({"http": f"socks5h://127.0.0.1:{port}",
                      "https": f"socks5h://127.0.0.1:{port}"})
    return s


def li_flow(s: requests.Session) -> None:
    s.get(f"https://libgen.li/file.php", params={"id": "93668953"}, timeout=40)
    time.sleep(5)
    r = s.get(f"https://libgen.li/ads.php", params={"md5": MD5}, timeout=40)
    m = re.search(r'href="(get\.php\?md5=[^"]+)"', r.text)
    print(f"  ads: {r.status_code}, key: {bool(m)}", flush=True)
    if not m:
        return
    time.sleep(8)
    r2 = s.get(f"https://libgen.li/" + m.group(1).replace("&amp;", "&"),
               headers={"Referer": f"https://libgen.li/ads.php?md5={MD5}"}, timeout=60)
    print(f"  get: {r2.status_code} len={len(r2.content)}", flush=True)
    if r2.status_code != 200:
        print(f"  body: {r2.text[:300]!r}", flush=True)
    else:
        print(f"  head: {r2.content[:8]!r}", flush=True)


def rs_flow(s: requests.Session) -> None:
    try:
        r = s.get(f"https://libgen.rs/book/index.php", params={"md5": MD5},
                  timeout=40, allow_redirects=False)
        print(f"  rs book page: {r.status_code} {len(r.text)}B", flush=True)
    except Exception as e:
        print(f"  rs failed: {type(e).__name__}: {str(e)[:80]}", flush=True)


with ProxyPool(["oc1.hevangel.com", "horace.org"]) as pool:
    for i, url in enumerate(pool.urls):
        port = int(url.rsplit(":", 1)[1])
        s = tunneled_session(port)
        print(f"=== egress {i} ({url}) ===", flush=True)
        if i == 0:
            li_flow(s)
        else:
            rs_flow(s)
            li_flow(s)
        time.sleep(10)
