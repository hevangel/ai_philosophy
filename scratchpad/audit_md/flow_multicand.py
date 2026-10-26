"""Container-side: search one book on the mirror, open the Editions tab, visit
each edition page, and download up to K epub candidates (skipping any file
within 100 kB of the bad size we already own). Saves to
/tmp/libgen_dl/cand_<num>_<i>.epub and inventory to /tmp/libgen_r/inv_<num>.json.

Runs INSIDE the camoufox container:
  python - <num> <K> <bad_size>
Reads /tmp/libgen_r/books.json (1-book list)."""
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
    num = int(sys.argv[1])
    max_cands = int(sys.argv[2])
    bad_size = int(sys.argv[3])
    book = {b["num"]: b for b in json.loads((DATA / "books.json").read_text(encoding="utf-8"))}[num]
    query = book["title"].replace("&", " and ")
    inventory = {"editions": [], "files": []}

    with sync_playwright() as p:
        browser = p.firefox.connect(WS, timeout=60000)
        ctx = browser.new_context(accept_downloads=True, viewport={"width": 1280, "height": 850})
        page = ctx.new_page()

        page.goto(f"{BASE}/", wait_until="commit", timeout=90000)
        time.sleep(rng.uniform(8, 12))
        box = page.wait_for_selector('input[name="req"]', timeout=90000)
        time.sleep(rng.uniform(1.5, 3.0))
        bb = box.bounding_box()
        if not bb:
            raise RuntimeError("search box has no bbox")
        page.mouse.click(bb["x"] + min(200, bb["width"] / 2), bb["y"] + bb["height"] / 2)
        page.keyboard.type(query, delay=rng.randrange(40, 100))
        time.sleep(rng.uniform(0.5, 1.2))
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
                editions.append({"row": i, "title": title[:90], "href": href})
        ids = list(dict.fromkeys(e["href"] for e in editions))
        log(f"#{num:03d} edition rows: {len(editions)}, unique: {len(ids)}")
        inventory["editions"] = editions

        for eid in ids:
            row = next(e for e in editions if e["href"] == eid)
            if re.search(r"Glimpse|Philosophers Magazine|Choice Reviews", row["title"], re.I):
                continue
            time.sleep(rng.uniform(2.5, 5.0))
            try:
                page.goto(f"{BASE}/{eid}", timeout=90000, wait_until="domcontentloaded")
            except PWTimeout:
                log(f"goto timeout on {eid[-12:]}, skipping")
                continue
            time.sleep(rng.uniform(2.5, 4.5))
            frows = page.locator("table tbody tr")
            for i in range(frows.count()):
                tds = frows.nth(i).locator("td")
                n = tds.count()
                if n < 2:
                    continue
                blob = " | ".join(tds.nth(j).inner_text().strip() for j in range(n))
                if "Size:" not in blob:
                    continue
                m_b = re.search(r"\((\d+)\s*B\)", blob)
                m_e = re.search(r"(?:Ext|Extension)\w*\s*:\s*(epub|pdf|mobi|azw3|djvu|fb2)",
                                blob, re.I)
                ads = page.locator('a[href*="ads.php?md5="]').first
                inventory["files"].append({
                    "edition": eid,
                    "ext": (m_e.group(1).lower() if m_e else "?"),
                    "size_bytes": int(m_b.group(1)) if m_b else 0,
                    "has_ads": bool(ads.count()),
                })
            (DATA / f"inv_{num}.json").write_text(
                json.dumps(inventory, indent=1, ensure_ascii=False), encoding="utf-8")

        epubs = [f for f in inventory["files"] if f["ext"] == "epub" and f["has_ads"]
                 and abs(f["size_bytes"] - bad_size) > 100 * 1024]
        epubs.sort(key=lambda f: -f["size_bytes"])
        log(f"#{num:03d} epub candidates (excl. bad size): {len(epubs)}")

        downloaded = 0
        edition_to_files = {}
        for f in epubs:
            edition_to_files.setdefault(f["edition"], []).append(f)
        for eid, flist in edition_to_files.items():
            if downloaded >= max_cands:
                break
            f0 = flist[0]
            time.sleep(rng.uniform(2.0, 4.0))
            try:
                page.goto(f"{BASE}/{eid}", timeout=90000, wait_until="domcontentloaded")
            except PWTimeout:
                log("goto timeout on picked edition page, continuing anyway")
            time.sleep(rng.uniform(2.5, 4.5))
            mirror = page.locator('a[href*="ads.php?md5="]').first
            if not mirror.count():
                continue
            time.sleep(rng.uniform(1.5, 3.0))
            try:
                mirror.click()
                page.wait_for_load_state("domcontentloaded", timeout=90000)
            except PWTimeout:
                log("ads click timeout, skipping edition")
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
            final = DL / f"cand_{num:03d}_{downloaded}.epub"
            tmp.replace(final)
            log(f"#{num:03d} candidate {downloaded}: {f0['size_bytes']} bytes")
            downloaded += 1
            time.sleep(rng.uniform(20, 40))

        ctx.close()
        browser.close()
    log(f"#{num:03d} done: {downloaded} candidates downloaded")


if __name__ == "__main__":
    try:
        main()
    except PWTimeout as e:
        log(f"timeout: {str(e)[:150]}")
        raise SystemExit(2)
    except Exception as e:
        log(f"error: {type(e).__name__}: {str(e)[:200]}")
        raise SystemExit(1)
