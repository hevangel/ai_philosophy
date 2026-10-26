"""Container-side: search one book on the mirror's Files tab, visit each epub
row's edition page, and download up to K candidates whose page text matches
the book's match tokens and whose md5 is not excluded.

Runs INSIDE the camoufox container:  python - <num> <K>
Reads /tmp/libgen_r/books.json (1-book list with "match" tokens and
"exclude_md5" list). Downloads to /tmp/libgen_dl/cand_<num>_<i>.epub,
inventory to /tmp/libgen_r/inv_<num>.json."""
import json
import re
import secrets
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

WS = "ws://localhost:9222/hkej"
BASE = "https://libgen.li"
DL = Path("/tmp/libgen_dl")
DATA = Path("/tmp/libgen_r")

rng = secrets.SystemRandom()


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def looks_valid(path):
    try:
        return path.read_bytes()[:2] == b"PK"
    except OSError:
        return False


def main():
    num = int(sys.argv[1])
    max_cands = int(sys.argv[2])
    book = {b["num"]: b for b in json.loads((DATA / "books.json").read_text(encoding="utf-8"))}[num]
    query = book["title"].replace("&", " and ")
    tokens = [t.lower() for t in book.get("match", [])]
    exclude_sizes = set(book.get("exclude_size", []))
    inventory = []

    with sync_playwright() as p:
        browser = p.firefox.connect(WS, timeout=60000)
        ctx = browser.new_context(accept_downloads=True, viewport={"width": 1280, "height": 850})
        page = ctx.new_page()

        page.goto(f"{BASE}/index.php?req={query.replace(' ', '+')}",
                  timeout=90000, wait_until="domcontentloaded")
        time.sleep(rng.uniform(7, 10))
        try:
            page.wait_for_selector("#tablelibgen tbody tr", timeout=45000)
        except PWTimeout:
            log(f"#{num:03d} no results table")
            (DATA / f"inv_{num}.json").write_text("[]", encoding="utf-8")
            return
        time.sleep(rng.uniform(2.0, 3.5))

        rows = page.locator("#tablelibgen tbody tr")
        hrefs = []
        for i in range(rows.count()):
            tds = rows.nth(i).locator("td")
            if tds.count() < 9:
                continue
            if tds.nth(7).inner_text().strip().lower() != "epub":
                continue
            link = tds.nth(0).locator('a[href*="edition.php?id="]').first
            href = link.get_attribute("href") if link.count() else ""
            if href:
                hrefs.append(href)
        hrefs = list(dict.fromkeys(hrefs))
        log(f"#{num:03d} epub file rows: {len(hrefs)}")

        got = 0
        for href in hrefs:
            if got >= max_cands:
                break
            time.sleep(rng.uniform(2.5, 5.0))
            try:
                page.goto(f"{BASE}/{href}", timeout=90000, wait_until="domcontentloaded")
            except PWTimeout:
                log("edition goto timeout, skipping")
                continue
            time.sleep(rng.uniform(2.5, 4.0))
            text = page.evaluate("() => document.body.innerText.toLowerCase()")[:20000]
            if tokens and not any(t in text for t in tokens):
                log(f"  no token match on {href[-12:]}, skipping")
                continue
            ads = page.locator('a[href*="ads.php?md5="]').first
            if not ads.count():
                continue
            md5 = ""
            m = re.search(r"md5=([0-9a-f]{32})", ads.get_attribute("href") or "")
            if m:
                md5 = m.group(1)
            m_b = re.search(r"\((\d+)\s*B\)", text)
            size = int(m_b.group(1)) if m_b else 0
            if any(abs(size - s) <= 1024 for s in exclude_sizes):
                log(f"  {href[-12:]} size {size} matches the file we own, skipping")
                continue
            title = page.title()[:80]
            mirror = page.locator('a[href*="ads.php?md5="]').first
            time.sleep(rng.uniform(1.5, 3.0))
            try:
                mirror.click()
                page.wait_for_load_state("domcontentloaded", timeout=90000)
            except PWTimeout:
                log("ads click timeout, skipping")
                continue
            time.sleep(rng.uniform(2.0, 3.5))
            get_link = page.locator('a[href*="get.php"]').first
            if not get_link.count():
                log("no GET link on ads page")
                continue
            time.sleep(rng.uniform(2.0, 4.0))
            tmp = DL / f"flow_{num:04d}.epub"
            try:
                with page.expect_download(timeout=240000) as dl_info:
                    get_link.click()
                dl_info.value.save_as(str(tmp))
            except PWTimeout:
                log("download timeout, skipping candidate")
                continue
            if not looks_valid(tmp):
                log(f"invalid download: {tmp.read_bytes()[:8]!r}")
                tmp.unlink(missing_ok=True)
                continue
            final = DL / f"cand_{num:03d}_{got}.epub"
            tmp.replace(final)
            inventory.append({"href": href, "page_title": title, "size": size,
                              "md5": md5, "cand": got})
            log(f"#{num:03d} candidate {got}: {size} B  md5={md5[:8]}  {title[:50]}")
            got += 1
            time.sleep(rng.uniform(20, 40))

        (DATA / f"inv_{num}.json").write_text(
            json.dumps(inventory, indent=1, ensure_ascii=False), encoding="utf-8")
        ctx.close()
        browser.close()
    log(f"#{num:03d} done: {got} candidates")


if __name__ == "__main__":
    try:
        main()
    except PWTimeout as e:
        log(f"timeout: {str(e)[:150]}")
        raise SystemExit(2)
    except Exception as e:
        log(f"error: {type(e).__name__}: {str(e)[:200]}")
        raise SystemExit(1)
