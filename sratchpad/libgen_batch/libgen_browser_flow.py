"""Human-mimicking browser download flow for libgen.li.

Replicates the manual path that is known to work: homepage search box ->
search results -> click the epub result -> edition page -> mirror link ->
ads.php GET button -> capture download. Real headed browser (full JS,
cookies, navigation history). Human-paced.

Usage:
  uv run python libgen_browser_flow.py --max-books 1     # test
  uv run python libgen_browser_flow.py --max-books 20 --min-gap 60 --max-gap 150
"""
import argparse
import json
import queue
import random
import re
import secrets
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

BATCH = Path(r"B:\ai_philosophy\sratchpad\libgen_batch").resolve()
DEST = Path(r"B:\ai_philosophy\philosophy_pop_culture").resolve()
STATE_FILE = BATCH / "batch_state.json"
LOG_FILE = BATCH / "browser_flow_log.txt"
BOOKS = json.loads((BATCH / "books.json").read_text(encoding="utf-8"))

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


def safe_filename(book: dict, ext: str) -> str:
    main = NAME_OK.sub("_", book["title"]).strip(" ._")
    sub = NAME_OK.sub("_", book["subtitle"]).strip(" ._")
    stem = f"{int(book['num']):03d} - {main}" + (f" - {sub}" if sub else "")
    return stem[:180] + f".{ext}"


class HumanBrowser:
    """One headed browser doing the organic search->download walk."""

    def __init__(self, pw):
        launch_kwargs = {"headless": False}
        try:  # prefer the real installed Chrome over bundled chromium
            import shutil
            if shutil.which("chrome") or Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe").exists():
                launch_kwargs["channel"] = "chrome"
        except Exception:
            pass
        self.browser = pw.chromium.launch(**launch_kwargs)
        self.ctx = self.browser.new_context(accept_downloads=True, viewport={"width": 1280, "height": 850})
        self.page = self.ctx.new_page()
        self.download: list = []
        self.page.on("download", self._on_dl)
        self.ctx.on("page", lambda pg: pg.on("download", self._on_dl))

    def _on_dl(self, dl):
        self.download.append(dl)

    def close(self):
        try:
            self.browser.close()
        except Exception:
            pass

    def human_pause(self, lo: float = 2.5, hi: float = 6.0) -> None:
        time.sleep(rng.uniform(lo, hi))

    def search(self, query: str) -> None:
        p = self.page
        p.goto("https://libgen.li/", wait_until="commit", timeout=90000)
        p.wait_for_selector('input[name="req"]', timeout=90000)
        self.human_pause()
        box = p.locator('input[name="req"]').first
        box.click()
        box.type(query, delay=rng.randrange(40, 120))  # human typing speed
        self.human_pause(0.6, 1.4)
        box.press("Enter")
        try:
            p.wait_for_selector("#tablelibgen", timeout=90000)
        except PWTimeout:
            log(f"    results table never appeared; url now: {p.url[:90]}")
        self.human_pause(2.0, 4.0)

    def pick_result(self) -> bool:
        """On the results page, click the first epub result's title link."""
        p = self.page
        rows = p.locator('#tablelibgen tbody tr')
        n = rows.count()
        for i in range(n):
            row = rows.nth(i)
            tds = row.locator("td")
            if tds.count() < 9:
                continue
            ext = tds.nth(7).inner_text().strip().lower()
            if ext != "epub":
                continue
            link = tds.nth(0).locator('a[href*="edition.php"]').first
            if link.count():
                self.human_pause(1.5, 4.0)
                link.click()
                p.wait_for_load_state("domcontentloaded", timeout=90000)
                self.human_pause()
                return True
        return False

    def open_mirror(self) -> bool:
        """On the edition page, click the libgen mirror -> ads.php page."""
        p = self.page
        # edition page lists download mirrors; the first one is libgen ads.php
        link = p.locator('a[href*="ads.php?md5="]').first
        if not link.count():
            return False
        self.human_pause(1.5, 4.0)
        link.click()
        p.wait_for_load_state("domcontentloaded", timeout=90000)
        self.human_pause()
        return True

    def click_get(self, tmp_path: Path) -> bool:
        p = self.page
        get = p.locator('a[href*="get.php"]').first
        if not get.count():
            return False
        self.human_pause(2.0, 5.0)
        try:
            with p.expect_download(timeout=180000) as dl_info:
                get.click()
            dl = dl_info.value
            tmp_path.parent.mkdir(parents=True, exist_ok=True)
            dl.save_as(str(tmp_path))
            return tmp_path.exists() and tmp_path.stat().st_size > 15000
        except PWTimeout:
            return False
        except Exception as e:
            log(f"    click/get error: {type(e).__name__}: {str(e)[:90]}")
            return False


def looks_valid(path: Path, ext: str) -> bool:
    try:
        data = path.read_bytes()
    except OSError:
        return False
    if ext == "epub":
        return data[:2] == b"PK"
    if ext == "pdf":
        return data[:5] == b"%PDF-"
    return len(data) > 15000


def process_book(hb: HumanBrowser, book: dict, state: dict) -> str:
    num = int(book["num"])
    query = book["title"].replace("&", " and ")
    hb.search(query)
    if "tablelibgen" not in hb.page.content():
        log(f"#{num:03d} no results page for: {query[:60]}")
        state[str(num)] = {"status": "no_result"}
        return "no_result"
    if not hb.pick_result():
        log(f"#{num:03d} no epub result row")
        state[str(num)] = {"status": "no_result"}
        return "no_result"
    if not hb.open_mirror():
        log(f"#{num:03d} no mirror link on edition page")
        state[str(num)] = {"status": "failed"}
        return "failed"

    ext = "epub"
    tmp = BATCH / "downloads" / ("flow_%04d.part" % num)
    tmp.unlink(missing_ok=True)
    if not hb.click_get(tmp):
        log(f"#{num:03d} GET click produced no download (gate or empty)")
        tmp.unlink(missing_ok=True)
        state[str(num)] = {"status": "pending_retry"}
        return "retry"

    if not looks_valid(tmp, ext):
        log(f"#{num:03d} downloaded file invalid")
        tmp.unlink(missing_ok=True)
        state[str(num)] = {"status": "failed"}
        return "failed"

    dest = (DEST / safe_filename(book, ext)).resolve()
    if dest.parent != DEST:
        raise ValueError("destination escaped target folder")
    tmp.replace(dest)
    log(f"#{num:03d} OK -> {dest.name} ({dest.stat().st_size // 1024} kB)")
    state[str(num)] = {"status": "done", "file": dest.name, "ext": ext}
    return "done"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-books", type=int, default=1)
    ap.add_argument("--min-gap", type=float, default=60)
    ap.add_argument("--max-gap", type=float, default=150)
    ap.add_argument("--only", help="comma separated book numbers")
    args = ap.parse_args()

    state = load_state()
    done = {int(k) for k, v in state.items() if v.get("status") in ("done", "no_result")}
    report = json.loads((BATCH / "match_report.json").read_text(encoding="utf-8")) \
        if (BATCH / "match_report.json").exists() else []
    copied = {r["num"] for r in report if r.get("status") == "copied"}
    todo = [b for b in BOOKS if b["num"] not in done and b["num"] not in copied]
    if args.only:
        wanted = {int(x) for x in args.only.split(",")}
        todo = [b for b in BOOKS if b["num"] in wanted]
    todo = todo[: args.max_books]
    if not todo:
        log("nothing to do")
        return

    log(f"=== browser flow start: {len(todo)} books ===")
    ok = 0
    with sync_playwright() as p:
        hb = HumanBrowser(p)
        try:
            for i, book in enumerate(todo):
                num = int(book["num"])
                status = "failed"
                try:
                    status = process_book(hb, book, state)
                except Exception as e:
                    log(f"#{num:03d} unexpected: {type(e).__name__}: {str(e)[:130]}")
                save_state(state)
                if status == "done":
                    ok += 1
                if i < len(todo) - 1:
                    time.sleep(rng.uniform(args.min_gap, args.max_gap))
        finally:
            hb.close()
    log(f"=== browser flow end: {ok}/{len(todo)} downloaded ===")


if __name__ == "__main__":
    main()
