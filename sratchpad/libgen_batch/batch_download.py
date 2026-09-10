"""Rate-limited batch downloader for the philosophy/pop-culture bibliography.

Downloads via libgen.li using Playwright browser sessions. In --proxied mode,
one SSH SOCKS5 tunnel per egress host is opened (proxy_pool.py) and each
worker thread gets its own chromium pinned to one tunnel, so the local
residential IP sends libgen zero requests and the per-IP footprint is spread
across the pool. Pacing per worker: 12-20 s between books, 8-15 s between a
search and its download, exponential per-worker cooldown on throttle
signatures. State is checkpointed after every book (resumable).

Usage:
  uv run python batch_download.py --proxied            # main run (SSH pool)
  uv run python batch_download.py --direct             # single local browser
  uv run python batch_download.py --proxied --only 1,2
  uv run python batch_download.py --proxied --retry-failed
"""
import argparse
import json
import queue
import random
import re
import threading
import time
import unicodedata
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

from proxy_pool import ProxyPool

BATCH = Path(r"B:\ai_philosophy\sratchpad\libgen_batch")
DEST = Path(r"B:\ai_philosophy\philosophy_pop_culture")
STATE_FILE = BATCH / "batch_state.json"
LOG_FILE = BATCH / "batch_log.txt"
BOOKS = json.loads((BATCH / "books.json").read_text(encoding="utf-8"))

BASE_URL = "https://libgen.li"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
PROXY_HOSTS = ["oc1.hevangel.com", "oc2.hevangel.com", "oc3.hevangel.com",
               "oc4.hevangel.com", "horace.org"]

_log_lock = threading.Lock()


def log(msg: str) -> None:
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    with _log_lock:
        print(line, flush=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")


_state_lock = threading.Lock()


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


STOPWORDS = {"the", "a", "an", "and", "of", "in", "to", "for", "is", "it"}


def parse_search_html(html: str) -> list[dict]:
    """Parse libgen.li search result table rows into records."""
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
        author = re.sub(r"<[^>]+>", "", tds[1]).strip()
        language = re.sub(r"<[^>]+>", "", tds[4]).strip()
        ext = re.sub(r"<[^>]+>", "", tds[7]).strip().lower()
        size_txt = re.sub(r"<[^>]+>", "", tds[6]).strip()
        results.append({
            "title": title, "author": author, "language": language,
            "ext": ext, "size_txt": size_txt,
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

    def score(r: dict) -> float:
        rt = norm(r["title"])
        s = 0.0
        covered = sum(1 for t in tokens if t in rt)
        s += 10.0 * covered / max(1, len(tokens))
        extra_words = len(set(rt.split()) - set(norm(book["title"]).split()) - set(norm(book["subtitle"]).split()))
        s -= 0.5 * min(extra_words, 8)
        if sub_tokens and all(t in rt for t in sub_tokens):
            s += 3.0
        ext = r["ext"]
        s += {"epub": 6.0, "pdf": 2.5}.get(ext, 0.5)
        if "english" in r["language"].lower():
            s += 2.0
        kb = size_kb(r["size_txt"])
        if kb <= 0:
            s -= 1.0
        elif kb < 20:
            s -= 3.0
        return s

    scored = [(score(r), r) for r in results if r["md5"]]
    if not scored:
        return None
    scored.sort(key=lambda t: -t[0])
    best_s, best_r = scored[0]
    log(f"    picked ({len(scored)} cand, score {best_s:.1f}): "
        f"{best_r['title'][:55]} [{best_r['ext']}, {best_r['size_txt']}]")
    return best_r


def safe_name(book: dict, ext: str) -> str:
    safe_main = re.sub(r'[\\/:*?"<>|]', "", book["title"]).strip()
    safe_sub = re.sub(r'[\\/:*?"<>|]', "", book["subtitle"]).strip()
    name = f"{book['num']:03d} - {safe_main}" + (f" - {safe_sub}" if safe_sub else "")
    return name + f".{ext}"


def valid_file(path: Path, ext: str) -> bool:
    try:
        if path.stat().st_size < 15_000:
            return False
        head = path.read_bytes()[:5]
        if ext == "epub":
            return head[:2] == b"PK"
        if ext == "pdf":
            return head[:5] == b"%PDF-"
        return True
    except OSError:
        return False


class Session:
    """One browser bound to one egress IP (or direct)."""

    def __init__(self, pw, proxy_url: str | None, name: str):
        self.name = name
        args = ["--disable-blink-features=AutomationControlled"]
        kwargs = {"headless": True, "args": args}
        if proxy_url:
            kwargs["proxy"] = {"server": proxy_url}
            # force DNS through the tunnel too, no local resolution leaks
            args.append("--host-resolver-rules=MAP * ~NOTFOUND , EXCLUDE 127.0.0.1")
        self.browser = pw.chromium.launch(**kwargs)
        self.ctx = self.browser.new_context(
            accept_downloads=True,
            user_agent=UA,
            viewport={"width": 1366, "height": 900},
            locale="en-US",
        )
        self.ctx.add_init_script(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined});")
        self.page = self.ctx.new_page()
        self.downloaded: list = []
        self.page.on("download", self._on_dl)
        self.ctx.on("page", lambda pg: pg.on("download", self._on_dl))

    def _on_dl(self, dl):
        try:
            self.downloaded.append(dl)
        except Exception:
            pass

    def close(self):
        try:
            self.browser.close()
        except Exception:
            pass


def session_get_html(sess: Session, url: str, settle_ms: int) -> str:
    try:
        sess.page.goto(url, wait_until="commit", timeout=75000)
        sess.page.wait_for_timeout(settle_ms)
        return sess.page.content()
    except PWTimeout:
        return ""
    except Exception as e:
        log(f"    [{sess.name}] goto error: {type(e).__name__}: {str(e)[:90]}")
        return ""


def process_book(sess: Session, book: dict, state: dict) -> None:
    num = book["num"]
    query = book["title"].replace("&", " and ")
    search_url = (f"{BASE_URL}/index.php?req={query.replace(' ', '+')}&res=25"
                  "&columns[]=t&objects[]=f&objects[]=e&objects[]=s&objects[]=a&objects[]=p&objects[]=w")

    html = session_get_html(sess, search_url, 6000)
    results = parse_search_html(html)
    if not results:
        log(f"#{num:03d} [{sess.name}] no search results ({len(html)}B)")
        state[str(num)] = {"status": "no_result"}
        return
    best = pick_best(results, book)
    if not best:
        log(f"#{num:03d} [{sess.name}] no candidate with md5")
        state[str(num)] = {"status": "no_result"}
        return

    time.sleep(random.uniform(8, 15))

    sess.downloaded.clear()
    html = session_get_html(sess, f"{BASE_URL}/ads.php?md5={best['md5']}", 6000)
    if 'href="get.php' not in html:
        log(f"#{num:03d} [{sess.name}] GET link absent ({len(html)}B) -> throttled")
        state[str(num)] = {"status": "throttled", "md5": best["md5"]}
        return
    try:
        sess.page.locator('a[href*="get.php"]').first.click(no_wait_after=True)
    except Exception as e:
        log(f"#{num:03d} [{sess.name}] click failed: {type(e).__name__}: {str(e)[:90]}")
        state[str(num)] = {"status": "throttled", "md5": best["md5"]}
        return

    dl = None
    for _ in range(90):
        if sess.downloaded:
            dl = sess.downloaded[0]
            break
        time.sleep(2)
    if not dl:
        log(f"#{num:03d} [{sess.name}] download event never fired")
        state[str(num)] = {"status": "throttled", "md5": best["md5"]}
        return

    ext = best["ext"] if best["ext"] in ("epub", "pdf", "mobi", "azw3") else "epub"
    tmp = BATCH / "downloads" / f"dl_{num}"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    try:
        dl.save_as(str(tmp))
    except Exception as e:
        log(f"#{num:03d} [{sess.name}] save failed: {type(e).__name__}: {str(e)[:90]}")
        state[str(num)] = {"status": "failed", "md5": best["md5"]}
        return

    if not valid_file(tmp, ext):
        got = tmp.read_bytes()[:20] if tmp.exists() else b""
        log(f"#{num:03d} [{sess.name}] invalid file head={got[:8]!r}")
        tmp.unlink(missing_ok=True)
        state[str(num)] = {"status": "failed", "md5": best["md5"]}
        return

    dest = DEST / safe_name(book, ext)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp.replace(dest)
    log(f"#{num:03d} [{sess.name}] OK -> {dest.name} ({dest.stat().st_size // 1024} kB)")
    state[str(num)] = {"status": "done", "file": dest.name, "ext": ext, "md5": best["md5"]}


def worker(wid: int, proxy_url: str | None, q: queue.Queue, state: dict) -> None:
    name = f"w{wid}"
    with sync_playwright() as pw:
        sess = Session(pw, proxy_url, name)
        try:
            while True:
                try:
                    book = q.get_nowait()
                except queue.Empty:
                    return
                try:
                    process_book(sess, book, state)
                except Exception as e:
                    log(f"#{book['num']:03d} [{name}] unexpected: {type(e).__name__}: {str(e)[:130]}")
                    state[str(book["num"])] = {"status": "failed"}
                save_state(state)
                st = state.get(str(book["num"]), {}).get("status")
                if st in ("throttled", "failed"):
                    time.sleep(random.uniform(240, 420))
                else:
                    time.sleep(random.uniform(12, 20))
        finally:
            sess.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma separated book numbers")
    ap.add_argument("--retry-failed", action="store_true")
    ap.add_argument("--proxied", action="store_true", help="use SSH SOCKS5 pool, one browser per tunnel")
    ap.add_argument("--direct", action="store_true", help="single browser, local IP")
    args = ap.parse_args()

    state = load_state()
    if args.only:
        wanted = {int(x) for x in args.only.split(",")}
        todo = [b for b in BOOKS if b["num"] in wanted]
    elif args.retry_failed:
        todo = [b for b in BOOKS if state.get(str(b["num"]), {}).get("status") in ("failed", "throttled")]
    else:
        done_nums = {int(k) for k, v in state.items() if v.get("status") == "done"}
        copied = {r["num"] for r in json.loads((BATCH / "match_report.json").read_text(encoding="utf-8"))
                  if r.get("status") == "copied"}
        todo = [b for b in BOOKS if b["num"] not in done_nums and b["num"] not in copied]

    if not todo:
        log("nothing to do")
        return

    q: queue.Queue = queue.Queue()
    for b in todo:
        q.put(b)

    log(f"=== batch start: {len(todo)} books, mode={'proxied' if args.proxied else 'direct'} ===")

    if args.proxied:
        with ProxyPool(PROXY_HOSTS) as pool:
            urls = pool.urls
            if not urls:
                log("no tunnels; aborting (use --direct to force local IP)")
                return
            log(f"workers: {len(urls)} via {urls}")
            threads = []
            for i, url in enumerate(urls):
                t = threading.Thread(target=worker, args=(i + 1, url, q, state), daemon=True)
                t.start()
                threads.append(t)
                time.sleep(2)  # stagger browser launches
            for t in threads:
                t.join()
    else:
        worker(0, None, q, state)

    done = sum(1 for v in state.values() if v.get("status") == "done")
    log(f"=== batch end: {done} total done; remaining: "
        f"{sum(1 for b in BOOKS if state.get(str(b['num']), {}).get('status') != 'done')} pending states ===")


if __name__ == "__main__":
    main()
