"""Polite VPN-rotation download loop for libgen.li.

Cycle: rotate the vpn-rotate gluetun container to the next VPN Unlimited
server IP -> verify egress -> run one batch attempt through its HTTP proxy.
  - probe run (--max-books 1 --abort-on-retry): if the key-mint gate is still
    closed, the run aborts at the first throttle signature (3 requests spent).
  - if the probe downloads a book, the gate is open: run drains up to 5 books
    per IP at 45-90 s spacing, then rotates regardless.
  - when closed: sleep 20-35 min, rotate to the next IP.

One IP therefore sees at most ~3 requests per many-hours cycle. Stops after
--max-hours (default 12) or when the queue is empty.
"""
import argparse
import json
import random
import subprocess
import time
from pathlib import Path

import requests

HERE = Path(__file__).parent
SERVERS = Path(r"A:\docker_volume\vpn_unlimited\gluetun\servers\vpn unlimited.json")
PROXY = "http://127.0.0.1:8890"
PY = r"B:\ai_agents\.venv\Scripts\python.exe"
LOG = HERE / "vpn_loop_log.txt"

rng = random.SystemRandom()


def log(msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def ip_pool() -> list[dict]:
    d = json.loads(SERVERS.read_text(encoding="utf-8"))
    out = []
    for s in d["servers"]:
        if s.get("udp") and s["ips"]:
            out.append({"country": s["country"], "hostname": s["hostname"], "ips": s["ips"]})
    return out


def run_quiet(cmd: list[str], timeout: int = 300) -> int:
    try:
        return subprocess.run(cmd, timeout=timeout,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              shell=False).returncode
    except subprocess.TimeoutExpired:
        return -1


def rotate(idx: int, pool: list[dict]) -> tuple[str, str] | None:
    host = pool[idx % len(pool)]
    ip = host["ips"][(idx // len(pool)) % len(host["ips"])]
    if run_quiet([PY, str(HERE / "set_vpn_remote.py"), ip, "1194"]) != 0:
        log(f"set_vpn_remote failed for {ip}")
        return None
    run_quiet(["docker", "restart", "vpn-rotate"], timeout=120)
    # wait for the tunnel: egress via proxy must equal the chosen IP
    deadline = time.time() + 120
    while time.time() < deadline:
        try:
            r = requests.get("https://api.ipify.org", proxies={"http": PROXY, "https": PROXY},
                             timeout=15)
            if r.text.strip() == ip:
                log(f"tunnel up via {host['country']} {host['hostname']} ({ip})")
                return ip, host["country"]
        except requests.RequestException:
            pass
        time.sleep(6)
    log(f"tunnel FAILED for {ip}, rotating on")
    return None


def queue_empty() -> bool:
    """Pending = bibliography books neither done/no_result (state) nor copied locally."""
    books = json.loads((HERE / "books.json").read_text(encoding="utf-8"))
    state = json.loads((HERE / "batch_state.json").read_text(encoding="utf-8")) \
        if (HERE / "batch_state.json").exists() else {}
    report = json.loads((HERE / "match_report.json").read_text(encoding="utf-8")) \
        if (HERE / "match_report.json").exists() else []
    done = {int(k) for k, v in state.items() if v.get("status") in ("done", "no_result")}
    copied = {r["num"] for r in report if r.get("status") == "copied"}
    pending = [b for b in books if b["num"] not in done and b["num"] not in copied]
    log(f"pending books: {len(pending)}")
    return len(pending) == 0


def attempt(max_books: int) -> str:
    """Run one batch attempt; return 'open' | 'closed' | 'empty'."""
    p = subprocess.run(
        [PY, str(HERE / "batch_download.py"), "--proxy", PROXY,
         "--max-books", str(max_books), "--abort-on-retry",
         "--min-gap", "45", "--max-gap", "90"],
        capture_output=True, text=True, timeout=7200, cwd=str(HERE), shell=False)
    out = p.stdout + p.stderr
    if "OK ->" in out:
        return "open"
    if "nothing to do" in out:
        return "empty"
    return "closed"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-hours", type=float, default=12.0)
    args = ap.parse_args()

    pool = ip_pool()
    log(f"=== vpn rotation loop start: {len(pool)} hosts, max {args.max_hours} h ===")
    start = time.time()
    idx = rng.randrange(len(pool))

    while (time.time() - start) < args.max_hours * 3600:
        if queue_empty():
            log("queue empty, done")
            break
        got = None
        for _ in range(3):  # try up to 3 hosts to get a live tunnel
            idx = (idx + 1) % (len(pool) * 3)
            got = rotate(idx, pool)
            if got:
                break
            time.sleep(rng.uniform(30, 60))
        if not got:
            log("no live tunnel in 3 tries; sleeping 10 min")
            time.sleep(600)
            continue
        ip, country = got

        time.sleep(rng.uniform(60, 120))  # settle before first libgen touch
        probe = attempt(1)
        if probe == "open":
            log(f"gate OPEN from {ip} ({country}); draining")
            while True:
                res = attempt(5)
                log(f"drain run: {res}")
                if res != "open":
                    break
                time.sleep(rng.uniform(60, 120))
            log("drain finished; rotating")
            continue
        if probe == "empty":
            log("queue empty, done")
            break
        wait = rng.uniform(1200, 2100)
        log(f"gate closed from {ip} ({country}); sleeping {wait / 60:.0f} min")
        time.sleep(wait)

    log("=== vpn rotation loop end ===")


if __name__ == "__main__":
    main()
