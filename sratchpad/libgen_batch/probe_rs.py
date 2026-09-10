"""Probe libgen.rs book page through the SSH tunnel (remote DNS via socks5h)."""
import re

import requests
from proxy_pool import ProxyPool

MD5 = "8d23f0442eaa96b5d7e8641d984ad4ff"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
ALLOWED = {"libgen.rs", "libgen.li", "lr459.1libgen.com", "31.42.184.140"}


def main() -> None:
    with ProxyPool(["oc1.hevangel.com"]) as pool:
        if not pool.urls:
            return
        port = pool.urls[0].rsplit(":", 1)[1]
        s = requests.Session()
        s.headers.update({"User-Agent": UA})
        s.proxies.update({"http": f"socks5h://127.0.0.1:{port}",
                          "https": f"socks5h://127.0.0.1:{port}"})
        url = f"https://libgen.rs/book/index.php?md5={MD5}"
        host = urlsplit_host(url)
        if host not in ALLOWED or not url.startswith("https://"):
            print("blocked by allowlist")
            return
        r = s.get(url, timeout=40, allow_redirects=False)
        print("libgen.rs book page:", r.status_code, len(r.text), "bytes")
        # direct download links on libgen.rs book pages
        links = re.findall(r'href="(http[^"]+)"', r.text)
        seen = []
        for l in links:
            if any(k in l for k in ("main.php", "get.php", "ipfs", "/lgd", "1libgen.com", "31.42")) and l not in seen:
                seen.append(l)
        for l in seen[:6]:
            print("   dl:", l[:120])
        if not seen:
            print("   (no direct links; page head):", re.sub(r"\s+", " ", r.text[:400]))


def urlsplit_host(url: str) -> str:
    from urllib.parse import urlsplit
    return urlsplit(url).hostname or ""


if __name__ == "__main__":
    main()
