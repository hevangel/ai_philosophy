"""Rewrite rotate.ovpn's remote line to the given VPN Unlimited server IP.

Usage: python set_vpn_remote.py <ip> [port]
Validates the IP against the bundled VPN Unlimited server list before writing.
"""
import json
import re
import sys
from pathlib import Path

CONFIG = Path(r"B:\ai_philosophy\sratchpad\libgen_batch\gluetun_configs\rotate.ovpn")
SERVERS = Path(r"A:\docker_volume\vpn_unlimited\gluetun\servers\vpn unlimited.json")


def main() -> None:
    ip = sys.argv[1]
    port = sys.argv[2] if len(sys.argv) > 2 else "1194"
    data = json.loads(SERVERS.read_text(encoding="utf-8"))
    known = {ip2 for s in data["servers"] for ip2 in s["ips"]}
    if ip not in known:
        raise SystemExit(f"IP {ip} is not in the VPN Unlimited server list")
    text = CONFIG.read_text(encoding="utf-8")
    new_text, n = re.subn(r"(?m)^remote\s+\S+(\s+\S+)?$", f"remote {ip} {port}", text)
    if n != 1:
        raise SystemExit(f"expected exactly one remote line, found {n}")
    CONFIG.write_text(new_text, encoding="utf-8")
    print(f"remote set to {ip} {port}")


if __name__ == "__main__":
    main()
