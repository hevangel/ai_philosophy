"""Rate-limited batch downloader for the philosophy/pop-culture bibliography.

Pipeline (pure requests, no browser): libgen.li search -> pick best record ->
ads.php keyed link -> get.php download, all through SSH SOCKS5 tunnels
(proxy_pool.py). One worker thread per tunnel; the local residential IP sends
libgen zero requests. Politeness: 12-20 s between books per worker, 8-15 s
between a search and its download, 3 download attempts with key re-minting,
per-worker cooldown on throttle signatures. State checkpointed after every
book (resumable).

Usage:
  uv run python batch_download.py --proxied            # main run (SSH pool)
  uv run python batch_download.py --direct             # local IP, no tunnels
  uv run python batch_download.py --proxied --only 1,2
  uv run python batch_download.py --proxied --retry-failed
"""
import argparse
import contextlib
import json
import queue
import re
import secrets
import threading
import time
import unicodedata
from pathlib import Path

import requests

from proxy_pool import ProxyPool

BATCH = Path(r"B:\ai_philosophy\sratchpad\libgen_batch").resolve()
DEST = Path(r"B:\ai_philosophy\philosophy_pop_culture").resolve()
STATE_FILE = BATCH / "batch_state.json"
LOG_FILE = BATCH / "batch_log.txt"
BOOKS = json.loads((BATCH / "books.json").read_text(encoding="utf-8"))

BASE = "https://libgen.li"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
PROXY_HOSTS = ["oc1.hevangel.com", "oc2.hevangel.com", "oc3.hevangel.com",
               "oc4.hevangel.com", "horace.org"]
ALLOWED_HOST = "libgen.li"

STOPWORDS = {"the", "a", "an", "and", "of", "in", "to", "for", "is", "it"}

# server-minted key pieces, matched individually with strict whitelists
MD5_RE = re.compile(r"^[0-9a-f]{32}$")
KEY_RE = re.compile(r"^[A-Z0-9]{6,20}$")
# filename characters we allow (everything else becomes '_')
NAME_OK = re.compile(r"[^A-Za-z0-9 ()&',!.\-]")

rng = secrets.SystemRandom()

_log_lock = threading.Lock()
_state_lock = threading.Lock()


def log(msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    with _log_lock:
        print(line, flush=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict) -> None:
    with _state_lock:
        STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("&", " and ").replace("'", "").replace("\u2019", "")
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def sig_tokens(s: str) -> set[str]:
    return {t for t in norm(s).split() if len(t) > 2 and t not in STOPWORDS}


def parse_search_html(html: str) -> list[dict]:
    results = []
    m = re.search(r'<table[^>]*id="tablelibgen"[^>]*>(.*?)</table>', html, re.S)
    if not m:
        return results
    body = m.group(1)
    tb = re.search(r"<tbody>(.*)</tbody>", body, re.S)
    rows = re.findall(r"<tr>(.*?)</tr>", tb.group(1), re.S) if tb else re.findall(r"<tr>(.*?)</tr>", body, re.S)
    for row in rows:
        tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        if len(tds) < 9:
            continue
        title_m = re.search(r'href="edition\.php\?id=\d+[^"]*"[^>]*>(.*?)</a>', tds[0], re.S)
        title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip() if title_m else ""
        fileid_m = re.search(r'href="/file\.php\?id=(\d+)"', tds[6])
        md5_m = re.search(r"ads\.php\?md5=([0-9a-f]{32})", tds[8])
        results.append({
            "title": title,
            "author": re.sub(r"<[^>]+>", "", tds[1]).strip(),
            "language": re.sub(r"<[^>]+>", "", tds[4]).strip(),
            "ext": re.sub(r"<[^>]+>", "", tds[7]).strip().lower(),
            "size_txt": re.sub(r"<[^>]+>", "", tds[6]).strip(),
            "file_id": fileid_m.group(1) if fileid_m else None,
            "md5": md5_m.group(1) if md5_m else None,
        })
    return results


def size_kb(size_txt: str) -> float:
    m = re.match(r"([\d.]+)\s*(kB|MB|GB)", size_txt, re.I)
    if not m:
        return 0.0
    val = float(m.group(1))
    unit = m.group(2).lower()
    return val * 1024 * 1024 if unit == "gb" else val * (1 if unit == "kb" else 1024)


def pick_best(results: list[dict], book: dict) -> dict | None:
    tokens = sig_tokens(book["title"])
    sub_tokens = sig_tokens(book["subtitle"]) if book["subtitle"] else set()
    base_words = set(norm(book["title"]).split()) | set(norm(book["subtitle"]).split())

    def score(r: dict) -> float:
        rt = norm(r["title"])
        s = 10.0 * sum(1 for t in tokens if t in rt) / max(1, len(tokens))
        s -= 0.5 * min(len(set(rt.split()) - base_words), 8)
        if sub_tokens and all(t in rt for t in sub_tokens):
            s += 3.0
        s += {"epub": 6.0, "pdf": 2.5}.get(r["ext"], 0.5)
        if "english" in r["language"].lower():
            s += 2.0
        kb = size_kb(r["size_txt"])
        s += -1.0 if kb <= 0 else (3.0 if kb >= 20 else -3.0)
        return s

    scored = sorted(((score(r), r) for r in results if r["md5"]), key=lambda t: -t[0])
    if not scored:
        return None
    best_s, best_r = scored[0]
    log(f"    picked ({len(scored)} cand, {best_s:.1f}): {best_r['title'][:55]} "
        f"[{best_r['ext']}, {best_r['size_txt']}]")
    return best_r


def safe_filename(book: dict, ext: str) -> str:
    main = NAME_OK.sub("_", book["title"]).strip(" ._")
    sub = NAME_OK.sub("_", book["subtitle"]).strip(" ._")
    stem = f"{int(book['num']):03d} - {main}" + (f" - {sub}" if sub else "")
    return stem[:180] + f".{ext}"


def looks_valid(data: bytes, ext: str) -> bool:
    if len(data) < 15_000:
        return False
    if ext == "epub":
        return data[:2] == b"PK"
    if ext == "pdf":
        return data[:5] == b"%PDF-"
    return True


class Worker:
    """One requests session pinned to one tunnel (or direct)."""

    def __init__(self, wid: int, port: int | None, proxy: str | None = None):
        self.wid = wid
        self.name = f"w{wid}"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": UA})
        if proxy:
            self.session.proxies.update({"http": proxy, "https": proxy})
        elif port:
            p = {"http": f"socks5h://127.0.0.1:{port}", "https": f"socks5h://127.0.0.1:{port}"}
            self.session.proxies.update(p)

    def _check(self, url: str) -> None:
        from urllib.parse import urlsplit
        if not url.startswith("https://"):
            raise ValueError("only https")
        if urlsplit(url).hostname != ALLOWED_HOST:
            raise ValueError(f"host not allowed: {url}")

    def get(self, url: str, **kw) -> requests.Response:
        self._check(url)
        kw.setdefault("timeout", (30, 180))
        return self.session.get(url, **kw)

    def fetch_file(self, md5: str, file_id: str | None) -> bytes | None:
        """file.php warmup -> ads.php key -> get.php download, whole file in memory."""
        if file_id and file_id.isdigit():
            try:
                self.get(f"{BASE}/file.php", params={"id": file_id})
            except requests.RequestException:
                pass
            time.sleep(rng.uniform(3, 6))
        r0 = self.get(f"{BASE}/ads.php", params={"md5": md5})
        if r0.status_code != 200:
            log(f"    [{self.name}] ads.php -> {r0.status_code} (no key)")
            return None
        m = re.search(r'href="get\.php\?md5=([0-9a-f]{32})&amp;key=([A-Z0-9]{6,20})"', r0.text)
        if not m:
            log(f"    [{self.name}] ads.php 200 but no keyed link ({len(r0.text)}B)")
            return None
        md5_hex, key = m.group(1), m.group(2)
        if not (MD5_RE.match(md5_hex) and KEY_RE.match(key)):
            log(f"    [{self.name}] minted key failed whitelist")
            return None
        time.sleep(rng.uniform(6, 12))
        r = self.get(f"{BASE}/get.php",
                     params={"md5": md5_hex, "key": key},
                     headers={"Referer": f"{BASE}/ads.php"},
                     stream=True)
        try:
            if r.status_code != 200:
                log(f"    [{self.name}] get.php -> {r.status_code}")
                return None
            cl = r.headers.get("content-length")
            expected = int(cl) if cl and cl.isdigit() else None
            buf = bytearray()
            for chunk in r.iter_content(chunk_size=65536):
                buf.extend(chunk)
                if len(buf) > 60 * 1024 * 1024:  # sanity cap
                    log(f"    [{self.name}] file exceeds 60 MB cap")
                    return None
            if expected and len(buf) != expected:
                log(f"    [{self.name}] size mismatch {len(buf)}/{expected}")
                return None
            return bytes(buf)
        except requests.RequestException as e:
            log(f"    [{self.name}] transfer error: {type(e).__name__}: {str(e)[:80]}")
            return None
        finally:
            r.close()


def process_book(w: Worker, book: dict, state: dict) -> str:
    """Returns the final status for this attempt."""
    num = int(book["num"])
    query = book["title"].replace("&", " and ")
    search_url = (f"{BASE}/index.php?req={requests.utils.quote(query)}&res=25"
                  "&columns[]=t&objects[]=f&objects[]=e&objects[]=s&objects[]=a&objects[]=p&objects[]=w")
    r = w.get(search_url)
    if r.status_code != 200:
        log(f"#{num:03d} [{w.name}] search http {r.status_code}")
        state[str(num)] = {"status": "throttled"}
        return "throttled"
    results = parse_search_html(r.text)
    if not results:
        log(f"#{num:03d} [{w.name}] no search results")
        state[str(num)] = {"status": "no_result"}
        return "no_result"
    best = pick_best(results, book)
    if not best:
        state[str(num)] = {"status": "no_result"}
        return "no_result"

    time.sleep(rng.uniform(8, 15))

    ext = best["ext"] if best["ext"] in ("epub", "pdf", "mobi", "azw3") else "epub"
    data = None
    for _ in range(2):
        data = w.fetch_file(best["md5"], best.get("file_id"))
        if data is not None:
            break
        time.sleep(rng.uniform(20, 40))
    if data is None:
        state[str(num)] = {"status": "pending_retry", "md5": best["md5"]}
        return "retry"
    if not looks_valid(data, ext):
        log(f"#{num:03d} [{w.name}] invalid file head={data[:8]!r}")
        state[str(num)] = {"status": "pending_retry", "md5": best["md5"]}
        return "retry"

    dest = (DEST / safe_filename(book, ext)).resolve()
    if dest.parent != DEST:
        raise ValueError(f"destination escaped target folder: {dest}")
    dest.write_bytes(data)
    log(f"#{num:03d} [{w.name}] OK -> {dest.name} ({len(data) // 1024} kB)")
    state[str(num)] = {"status": "done", "file": dest.name, "ext": ext, "md5": best["md5"]}
    return "done"


def worker(wid: int, port: int | None, q: queue.Queue, state: dict,
           proxy: str | None = None, min_gap: float = 12, max_gap: float = 20,
           abort_on_retry: bool = False) -> None:
    w = Worker(wid, port, proxy)
    attempts: dict[int, int] = {}   # book num -> failed attempts
    backoff = None                  # per-worker cooldown after a failed attempt
    consecutive_errors = 0
    try:
        while True:
            try:
                book = q.get_nowait()
            except queue.Empty:
                return
            num = int(book["num"])
            status = "failed"
            try:
                status = process_book(w, book, state)
                consecutive_errors = 0
            except requests.RequestException as e:
                consecutive_errors += 1
                log(f"#{num:03d} [{w.name}] net error {consecutive_errors}: {type(e).__name__}: {str(e)[:90]}")
                state[str(num)] = {"status": "pending_retry"}
                status = "retry"
                if consecutive_errors >= 5:
                    log(f"[{w.name}] too many consecutive net errors, retiring worker")
                    return
            except Exception as e:
                log(f"#{num:03d} [{w.name}] unexpected: {type(e).__name__}: {str(e)[:130]}")
                state[str(num)] = {"status": "failed"}
                status = "failed"
            save_state(state)

            if status == "retry":
                # give up on this IP for a while; book goes back for another IP to try
                attempts[num] = attempts.get(num, 0) + 1
                if abort_on_retry:
                    log(f"[{w.name}] retry-signature seen, aborting run for IP rotation")
                    return
                if attempts[num] >= 4:
                    state[str(num)] = {"status": "failed"}
                    save_state(state)
                    log(f"#{num:03d} [{w.name}] giving up after {attempts[num]} attempts")
                else:
                    q.put(book)
                backoff = min((backoff or 600) * 2, 3600)
                time.sleep(rng.uniform(backoff * 0.8, backoff * 1.2))
            else:
                backoff = None  # success or definitive no_result resets the IP's cooldown
                time.sleep(rng.uniform(min_gap, max_gap) if status == "done" else rng.uniform(6, 10))
    finally:
        w.session.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma separated book numbers")
    ap.add_argument("--retry-failed", action="store_true")
    ap.add_argument("--proxied", action="store_true", help="SSH SOCKS5 pool, one worker per tunnel")
    ap.add_argument("--direct", action="store_true", help="single worker on local IP")
    ap.add_argument("--proxy", help="single worker through an http proxy URL")
    ap.add_argument("--max-books", type=int, help="stop after this many queue items processed")
    ap.add_argument("--min-gap", type=float, default=12, help="min seconds between books")
    ap.add_argument("--max-gap", type=float, default=20, help="max seconds between books")
    ap.add_argument("--abort-on-retry", action="store_true",
                    help="exit as soon as a throttle signature is seen (for IP-rotation drivers)")
    args = ap.parse_args()
    q_limit = args.max_books

    state = load_state()
    if args.only:
        wanted = {int(x) for x in args.only.split(",")}
        todo = [b for b in BOOKS if b["num"] in wanted]
    elif args.retry_failed:
        todo = [b for b in BOOKS if state.get(str(b["num"]), {}).get("status")
                in ("failed", "throttled", "pending_retry")]
    else:
        done_nums = {int(k) for k, v in state.items()
                     if v.get("status") in ("done", "no_result")}
        copied = {r["num"] for r in json.loads((BATCH / "match_report.json").read_text(encoding="utf-8"))
                  if r.get("status") == "copied"}
        todo = [b for b in BOOKS if b["num"] not in done_nums and b["num"] not in copied]

    if not todo:
        log("nothing to do")
        return

    if q_limit is not None:
        todo = todo[:q_limit]
        if not todo:
            log("nothing to do")
            return

    q: queue.Queue = queue.Queue()
    for b in todo:
        q.put(b)

    mode = "proxied" if args.proxied else ("proxy" if args.proxy else "direct")
    log(f"=== batch start: {len(todo)} books, mode={mode} ===")

    if args.proxied:
        with ProxyPool(PROXY_HOSTS) as pool:
            if not pool.urls:
                log("no tunnels; aborting")
                return
            ports = [int(u.rsplit(":", 1)[1]) for u in pool.urls]
            log(f"workers: {len(ports)} on ports {ports}")
            threads = []
            for i, port in enumerate(ports):
                t = threading.Thread(target=worker, args=(i + 1, port, q, state), daemon=True)
                t.start()
                threads.append(t)
                time.sleep(1.5)
            for t in threads:
                t.join()
    else:
        worker(0, None, q, state, proxy=args.proxy,
               min_gap=args.min_gap, max_gap=args.max_gap,
               abort_on_retry=args.abort_on_retry)

    done = sum(1 for v in state.values() if v.get("status") == "done")
    log(f"=== batch end: {done} total done ===")


if __name__ == "__main__":
    main()
