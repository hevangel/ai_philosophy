import time

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.connect("ws://localhost:9222/hkej", timeout=60000)
    ctx = browser.new_context(viewport={"width": 1280, "height": 850})
    page = ctx.new_page()
    page.goto("https://libgen.li/edition.php?id=2345695", timeout=90000)
    page.wait_for_load_state("domcontentloaded", timeout=90000)
    time.sleep(8)
    links = page.evaluate("""() => [...document.querySelectorAll('a')].
        filter(a => /ads\\.php|get\\.php/.test(a.href)).
        map(a => a.href.slice(0, 100) + ' :: ' + (a.textContent || '').trim().slice(0, 40))""")
    for l in links[:15]:
        print(l)
    rows = page.locator("table tbody tr")
    print("tbody rows:", rows.count())
    for i in range(min(rows.count(), 10)):
        tds = rows.nth(i).locator("td")
        cells = [tds.nth(j).inner_text().strip()[:30] for j in range(min(tds.count(), 10))]
        if any(c for c in cells):
            print("row", i, cells)
    page.screenshot(path="/tmp/libgen/edition.png", full_page=False)
    ctx.close()
    browser.close()
print("diag done")
