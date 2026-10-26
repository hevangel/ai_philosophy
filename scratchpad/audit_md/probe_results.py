import time

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.connect("ws://localhost:9222/hkej", timeout=60000)
    ctx = browser.new_context(viewport={"width": 1280, "height": 850})
    page = ctx.new_page()
    page.goto("https://libgen.li/index.php?req=The+Beatles+and+Philosophy",
              timeout=90000, wait_until="domcontentloaded")
    time.sleep(8)
    for tab_text, curtab in (("Files", "f"), ("Editions", "e"), ("Works", "w")):
        rows = page.locator("#tablelibgen tbody tr")
        n = rows.count()
        print(f"== {tab_text} tab ({curtab}): {n} rows")
        for i in range(min(n, 12)):
            tds = rows.nth(i).locator("td")
            cnt = tds.count()
            if cnt < 2:
                continue
            title = tds.nth(1).inner_text().strip().splitlines()[0][:60] if cnt > 1 else ""
            ext = tds.nth(7).inner_text().strip() if cnt > 7 else ""
            size = tds.nth(8).inner_text().strip() if cnt > 8 else ""
            link = tds.nth(1).locator('a[href*="edition.php?id="]').first
            href = link.get_attribute("href") if link.count() else ""
            print(f"   {ext:6} {size:10} {title}  [{href[-14:]}]")
        nxt = page.locator(f'a.nav-link[href*="curtab={curtab}"]').first
        if nxt.count():
            nxt.click()
            page.wait_for_load_state("domcontentloaded", timeout=90000)
            time.sleep(5)
    ctx.close()
    browser.close()
