"""One-off libgen flow: enumerate ALL editions of one book on the mirror's
Editions tab, visit each edition page, read its file table (ext + size), then
download the best epub that differs from the bad calibre conversion we already
own (374 kB).

Runs INSIDE the camoufox container (piped via `docker exec -i ... python -`).
Reads /tmp/libgen/books.json (1-book list), writes /tmp/libgen/editions_002.json
(the full edition inventory) and /tmp/libgen_dl/book_0002.epub.
"""
import json
import re
import secrets
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

WS = "ws://localhost:9222/hkej"
BASE = "https://libgen.li"
DL = Path("/tmp/libgen_dl")
DATA = Path("/tmp/libgen")
BAD_SIZE = 374217
NUM = 2

rng = secrets.SystemRandom()


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def size_to_bytes(text):
    m = re.search(r"([\d.]+)\s*(kb|mb)", text.strip().lower())
    if not m:
        return 0
    val = float(m.group(1))
    return int(val * 1024 * (1024 if m.group(2) == "mb" else 1))


def looks_valid(path):
    try:
        return path.read_bytes()[:2] == b"PK"
    except OSError:
        return False


def main():
    books = {b["num"]: b for b in json.loads((DATA / "books.json").read_text(encoding="utf-8"))}
    book = books[NUM]
    query = book["title"].replace("&", " and ")
    inventory = []

    with sync_playwright() as p:
        browser = p.firefox.connect(WS, timeout=60000)
        ctx = browser.new_context(accept_downloads=True, viewport={"width": 1280, "height": 850})
        page = ctx.new_page()

        page.goto(f"{BASE}/", wait_until="commit", timeout=90000)
        time.sleep(rng.uniform(10, 14))
        box = page.wait_for_selector('input[name="req"]', timeout=90000)
        time.sleep(rng.uniform(1.5, 3.5))
        bb = box.bounding_box()
        if not bb:
            raise RuntimeError("search box has no bbox")
        page.mouse.click(bb["x"] + min(200, bb["width"] / 2), bb["y"] + bb["height"] / 2)
        page.keyboard.type(query, delay=rng.randrange(40, 110))
        time.sleep(rng.uniform(0.5, 1.3))
        page.keyboard.press("Enter")
        page.wait_for_url("**index.php**", timeout=90000)
        time.sleep(rng.uniform(2.0, 4.0))

        tab = page.locator("a.nav-link", has_text="Editions").first
        if not tab.count():
            raise RuntimeError("no Editions tab on results page")
        time.sleep(rng.uniform(1.5, 3.0))
        tab.click()
        page.wait_for_load_state("domcontentloaded", timeout=90000)
        time.sleep(rng.uniform(3.0, 5.0))

        rows = page.locator("#tablelibgen tbody tr")
        editions = []
        for i in range(rows.count()):
            tds = rows.nth(i).locator("td")
            link = tds.nth(1).locator('a[href*="edition.php?id="]').first
            href = link.get_attribute("href") if link.count() else ""
            title = tds.nth(1).inner_text().strip().splitlines()[0] if tds.count() > 1 else ""
            if href:
                editions.append({"row": i, "title": title[:80], "href": href})
        ids = list(dict.fromkeys(e["href"] for e in editions))
        log(f"edition rows: {len(editions)}, unique ids: {len(ids)}")
        for e in editions:
            log(f"  {e['href'][-12:]} {e['title']}")

        files = []
        for eid in ids:
            row = next(e for e in editions if e["href"] == eid)
            if re.search(r"Glimpse|Philosophers Magazine|Choice Reviews", row["title"], re.I):
                log(f"skip journal article: {row['title'][:50]}")
                continue
            time.sleep(rng.uniform(3.0, 6.0))
            try:
                page.goto(f"{BASE}/{eid}", timeout=90000, wait_until="domcontentloaded")
            except PWTimeout:
                log(f"goto timeout on {eid[-12:]}, skipping")
                continue
            time.sleep(rng.uniform(3.0, 5.0))
            frows = page.locator("table tbody tr")
            for i in range(frows.count()):
                tds = frows.nth(i).locator("td")
                n = tds.count()
                if n < 2:
                    continue
                cells = [tds.nth(j).inner_text().strip() for j in range(n)]
                blob = " | ".join(cells)
                if "Size:" not in blob:
                    continue
                m_b = re.search(r"\((\d+)\s*B\)", blob)
                m_e = re.search(r"(?:Ext|Extension)\w*\s*:\s*(epub|pdf|mobi|azw3|djvu|fb2)",
                                blob, re.I)
                ads = page.locator('a[href*="ads.php?md5="]').first
                files.append({
                    "edition": eid,
                    "ext": (m_e.group(1).lower() if m_e else "?"),
                    "size_bytes": int(m_b.group(1)) if m_b else 0,
                    "row_text": blob[:200],
                    "has_ads": bool(ads.count()),
                    "ads_href": ads.get_attribute("href") if ads.count() else "",
                })
            log(f"scanned {eid[-12:]}: {sum(1 for f in files if f['edition'] == eid)} file rows")

        (DATA / "editions_002.json").write_text(
            json.dumps({"editions": editions, "files": files}, indent=1, ensure_ascii=False),
            encoding="utf-8")
        epubs = [f for f in files if f["ext"] == "epub" and f["has_ads"]]
        log(f"epub files with mirror links: {len(epubs)}")
        for f in epubs:
            log(f"  size={f['size_bytes']} md5={f['ads_href'][-40:]} :: {f['row_text'][:80]}")

        candidates = [f for f in epubs if abs(f["size_bytes"] - BAD_SIZE) > 100 * 1024]
        if not candidates:
            raise RuntimeError(f"no alternative epub edition besides the {BAD_SIZE}B one")
        pick = max(candidates, key=lambda f: f["size_bytes"])
        log(f"picked epub size={pick['size_bytes']} md5={pick['ads_href'][-40:]}")

        time.sleep(rng.uniform(2.0, 4.0))
        try:
            page.goto(f"{BASE}/{pick['edition']}", timeout=90000, wait_until="domcontentloaded")
        except PWTimeout:
            log("goto timeout on picked edition page, continuing anyway")
        time.sleep(rng.uniform(3.0, 5.0))
        mirror = page.locator('a[href*="ads.php?md5="]').first
        if not mirror.count():
            raise RuntimeError("no mirror link on edition page")
        time.sleep(rng.uniform(1.5, 3.5))
        mirror.click()
        page.wait_for_load_state("domcontentloaded", timeout=90000)
        time.sleep(rng.uniform(2.0, 4.0))

        get_link = page.locator('a[href*="get.php"]').first
        if not get_link.count():
            raise RuntimeError("ads page has no GET link")
        time.sleep(rng.uniform(2.5, 5.0))
        tmp = DL / f"flow_{NUM:04d}.epub"
        with page.expect_download(timeout=240000) as dl_info:
            get_link.click()
        dl_info.value.save_as(str(tmp))
        if not looks_valid(tmp):
            raise RuntimeError(f"download invalid: {tmp.read_bytes()[:8]!r}")
        final = DL / f"book_{NUM:04d}.epub"
        tmp.replace(final)
        log(f"OK -> {final} ({final.stat().st_size} bytes)")

        ctx.close()
        browser.close()


if __name__ == "__main__":
    try:
        main()
    except PWTimeout as e:
        log(f"timeout: {str(e)[:150]}")
        raise SystemExit(2)
    except Exception as e:
        log(f"error: {type(e).__name__}: {str(e)[:200]}")
        raise SystemExit(1)
