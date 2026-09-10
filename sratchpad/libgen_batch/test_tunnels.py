"""Verify SSH tunnels open and each egress IP is distinct."""
import requests
from proxy_pool import ProxyPool

PROXY_HOSTS = ["oc1.hevangel.com", "oc2.hevangel.com", "oc3.hevangel.com",
               "oc4.hevangel.com", "horace.org"]

with ProxyPool(PROXY_HOSTS) as pool:
    print("tunnels:", pool.urls)
    for url in pool.urls:
        try:
            r = requests.get("https://api.ipify.org",
                             proxies={"https": url.replace("socks5://", "socks5h://")},
                             timeout=20)
            print(f"  {url} -> egress IP {r.text}")
        except Exception as e:
            print(f"  {url} -> FAILED {type(e).__name__}: {str(e)[:80]}")
