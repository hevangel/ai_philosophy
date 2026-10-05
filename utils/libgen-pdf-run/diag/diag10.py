import time

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.connect("ws://localhost:9222/hkej", timeout=60000)
    ctx = browser.new_context(viewport={"width": 1280, "height": 850})
    page = ctx.new_page()
    page.goto("https://libgen.li/index.php?req=Seinfeld+and+Philosophy", timeout=90000)
    page.wait_for_load_state("domcontentloaded", timeout=90000)
    time.sleep(8)
    rows = page.locator("#tablelibgen tbody tr")
    print("rows:", rows.count())
    for i in range(min(rows.count(), 5)):
        tds = rows.nth(i).locator("td")
        n = tds.count()
        if n < 9:
            continue
        ext = tds.nth(7).inner_text().strip().lower()
        links = tds.nth(0).locator("a")
        hrefs = [links.nth(j).get_attribute("href") for j in range(links.count())]
        print(f"row {i} ext={ext} td0links={hrefs}")
    ctx.close()
    browser.close()
print("diag done")
