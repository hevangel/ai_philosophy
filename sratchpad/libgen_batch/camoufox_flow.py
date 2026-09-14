"""Human-mimicking libgen.li flow, running INSIDE the camoufox container.

Connects to the container's own camoufox Playwright server (ws://localhost:9222/hkej),
walks the organic path: homepage search box -> results -> epub result ->
edition page -> libgen mirror -> ads.php GET button. Saves to /tmp/libgen_dl/.

Usage: python /tmp/libgen/flow.py <comma-separated book numbers>
Reads /tmp/libgen/books.json, writes /tmp/libgen/flow_state.json.
"""
import json
import random
import re
import secrets
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

WS = "ws://localhost:9222/hkej"
BASE = "https://libgen.li"
DL = Path("/tmp/libgen_dl")
DATA = Path("/tmp/libgen")

NAME_OK = re.compile(r"[^A-Za-z0-9 ()&',!.\-]")
rng = secrets.SystemRandom()


def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)


def safe_filename(book, ext):
    main = NAME_OK.sub("_", book["title"]).strip(" ._")
    sub = NAME_OK.sub("_", book["subtitle"]).strip(" ._")
    stem = f"{int(book['num']):03d} - {main}" + (f" - {sub}" if sub else "")
    return stem[:180] + f".{ext}"


def looks_valid(path, ext):
    try:
        data = path.read_bytes()
    except OSError:
        return False
    if ext == "epub":
        return data[:2] == b"PK"
    return len(data) > 15000


def main():
    nums = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else []
    books = {b["num"]: b for b in json.loads((DATA / "books.json").read_text(encoding="utf-8"))}
    state_path = DATA / "flow_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}

    with sync_playwright() as p:
        browser = p.firefox.connect(WS, timeout=60000)
        ctx = browser.new_context(accept_downloads=True, viewport={"width": 1280, "height": 850})
        page = ctx.new_page()
        downloaded = []

        def on_dl(dl):
            downloaded.append(dl)

        page.on("download", on_dl)

        for num in nums:
            book = books[num]
            query = book["title"].replace("&", " and ")
            status = "failed"
            try:
                page.goto(f"{BASE}/", wait_until="commit", timeout=90000)
                time.sleep(rng.uniform(10, 14))
                page.wait_for_selector('input[name="req"]', timeout=90000)
                time.sleep(rng.uniform(1.5, 3.5))
                box = page.locator('input[name="req"]').first
                box.click(timeout=20000)
                box.type(query, delay=rng.randrange(40, 110))
                time.sleep(rng.uniform(0.5, 1.3))
                box.press("Enter")
                page.wait_for_url("**index.php**", timeout=90000)
                page.wait_for_selector("#tablelibgen tbody tr", timeout=90000)
                time.sleep(rng.uniform(2.0, 4.0))

                clicked = False
                rows = page.locator("#tablelibgen tbody tr")
                for i in range(rows.count()):
                    tds = rows.nth(i).locator("td")
                    if tds.count() < 9:
                        continue
                    if tds.nth(7).inner_text().strip().lower() != "epub":
                        continue
                    link = tds.nth(0).locator('a[href*="edition.php"]').first
                    if link.count():
                        time.sleep(rng.uniform(1.5, 3.5))
                        link.click()
                        page.wait_for_load_state("domcontentloaded", timeout=90000)
                        time.sleep(rng.uniform(2.0, 4.0))
                        clicked = True
                        break
                if not clicked:
                    log(f"#{num:03d} no epub result row")
                    state[str(num)] = {"status": "no_result"}
                    state_path.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
                    continue

                mirror = page.locator('a[href*="ads.php?md5="]').first
                if not mirror.count():
                    log(f"#{num:03d} no mirror link on edition page")
                    state[str(num)] = {"status": "failed"}
                    state_path.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
                    continue
                time.sleep(rng.uniform(1.5, 3.5))
                mirror.click()
                page.wait_for_load_state("domcontentloaded", timeout=90000)
                time.sleep(rng.uniform(2.0, 4.0))

                get_link = page.locator('a[href*="get.php"]').first
                if not get_link.count():
                    log(f"#{num:03d} ads page has no GET link")
                    state[str(num)] = {"status": "pending_retry"}
                    state_path.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
                    continue

                time.sleep(rng.uniform(2.5, 5.0))
                downloaded.clear()
                tmp = DL / ("flow_%04d.part" % num)
                with page.expect_download(timeout=240000) as dl_info:
                    get_link.click()
                dl_info.value.save_as(str(tmp))

                if looks_valid(tmp, "epub"):
                    final = DL / ("book_%04d.epub" % num)
                    tmp.replace(final)
                    log(f"#{num:03d} OK -> {final.name} ({final.stat().st_size // 1024} kB)")
                    state[str(num)] = {"status": "done", "file": safe_filename(book, "epub")}
                    status = "done"
                else:
                    log(f"#{num:03d} download invalid: {tmp.read_bytes()[:8]!r}")
                    tmp.unlink(missing_ok=True)
                    state[str(num)] = {"status": "pending_retry"}
                    status = "retry"
            except PWTimeout as e:
                log(f"#{num:03d} timeout: {str(e)[:100]}")
                state[str(num)] = {"status": "pending_retry"}
                status = "retry"
            except Exception as e:
                log(f"#{num:03d} error: {type(e).__name__}: {str(e)[:120]}")
                state[str(num)] = {"status": "pending_retry"}
                status = "retry"
            state_path.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
            if num != nums[-1]:
                time.sleep(rng.uniform(45, 90))
        ctx.close()
        browser.close()
    log(f"flow end: {sum(1 for v in state.values() if isinstance(v, dict) and v.get('status') == 'done')} done total in flow state")


if __name__ == "__main__":
    main()
