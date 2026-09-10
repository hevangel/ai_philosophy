"""Probe alternative libgen mirrors through the SSH tunnel (guarded)."""
import re

from proxy_pool import ProxyPool
from safe_http import guarded_get

MD5 = "8d23f0442eaa96b5d7e8641d984ad4ff"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

TARGETS = [
    ("libgen.rs book page", f"https://libgen.rs/book/index.php?md5={MD5}"),
    ("libgen.st", f"https://libgen.st/book/index.php?md5={MD5}"),
    ("libgen.is", f"https://libgen.is/book/index.php?md5={MD5}"),
    ("libgen.xyz", f"https://libgen.xyz/book/{MD5}"),
    ("annas-archive.se", f"https://annas-archive.se/md5/{MD5}"),
]


def main() -> None:
    with ProxyPool(["oc1.hevangel.com"]) as pool:
        if not pool.urls:
            print("no tunnels")
            return
        port = pool.urls[0].rsplit(":", 1)[1]
        proxies = {"http": f"socks5h://127.0.0.1:{port}", "https": f"socks5h://127.0.0.1:{port}"}
        s = __import__("requests").Session()
        s.headers.update({"User-Agent": UA})
        s.proxies.update(proxies)
        for name, url in TARGETS:
            try:
                r = guarded_get(s, url)
                dl_links = re.findall(r'href="(http[^"]{0,120})"', r.text)
                dl_links = [l for l in dl_links if any(k in l for k in ("main.php", "get.php", "ipfs", "lgd-", "/download/"))][:3]
                print(f"  {name}: {r.status_code} {len(r.text)}B links={dl_links}", flush=True)
            except Exception as e:
                print(f"  {name}: FAILED {type(e).__name__}: {str(e)[:70]}", flush=True)


if __name__ == "__main__":
    main()
