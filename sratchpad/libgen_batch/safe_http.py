"""SSRF-hardened HTTP helper: https only, strict host allowlist, resolved-IP
checks against private/loopback/link-local/reserved ranges, no auto redirects."""
import ipaddress
import socket
from urllib.parse import urlsplit

import requests

ALLOWED_HOSTS = {
    "libgen.li",
    "libgen.rs",
    "libgen.st",
    "libgen.is",
    "libgen.xyz",
    "annas-archive.se",
    "annas-archive.org",
    "api.ipify.org",
}

_BLOCKED_NETS = [
    ipaddress.ip_network(n)
    for n in (
        "0.0.0.0/8", "10.0.0.0/8", "100.64.0.0/10", "127.0.0.0/8",
        "169.254.0.0/16", "172.16.0.0/12", "192.0.0.0/24", "192.0.2.0/24",
        "192.168.0.0/16", "198.18.0.0/15", "198.51.100.0/24", "203.0.113.0/24",
        "224.0.0.0/4", "240.0.0.0/4", "255.255.255.255/32", "::1/128",
        "::/128", "fc00::/7", "fe80::/10", "ff00::/8",
    )
]


def validate_url(url: str) -> None:
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise ValueError(f"only https allowed, got: {parts.scheme}")
    host = parts.hostname
    if not host or host not in ALLOWED_HOSTS:
        raise ValueError(f"host not in allowlist: {host}")
    try:
        infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
    except OSError as e:
        raise ValueError(f"DNS resolution failed for {host}: {e}")
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        for net in _BLOCKED_NETS:
            if ip in net:
                raise ValueError(f"{host} resolves to blocked address: {ip}")


def guarded_get(session: requests.Session, url: str, **kw) -> requests.Response:
    validate_url(url)
    kw.setdefault("allow_redirects", False)
    kw.setdefault("timeout", 30)
    return session.get(url, **kw)
