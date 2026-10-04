import time

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.connect("ws://localhost:9222/hkej", timeout=60000)
    ctx = browser.new_context(viewport={"width": 1280, "height": 850})
    page = ctx.new_page()
    page.goto("https://libgen.li/index.php?req=Dark+Tower+and+Philosophy", timeout=90000)
    page.wait_for_load_state("domcontentloaded", timeout=90000)
    time.sleep(8)
    # find the Editions tab link
    tabs = page.evaluate("""() => [...document.querySelectorAll('a, button, li')].
        filter(e => /Editions/.test(e.textContent || '') && e.textContent.length < 40).
        map(e => e.tagName + '#' + (e.id || '') + '.' + (e.className || '') + ' :: ' + e.textContent.trim().slice(0, 30))""")
    print("tab candidates:")
    for t in tabs[:8]:
        print("  ", t)
    clicked = False
    for el in page.locator("a, button").all():
        txt = (el.inner_text() or "").strip()
        if txt.startswith("Editions"):
            el.click()
            clicked = True
            break
    print("clicked tab:", clicked)
    time.sleep(6)
    print("url now:", page.url[:130])
    info = page.evaluate("""() => {
        const tables = [...document.querySelectorAll('table')].map(t =>
            'table#' + (t.id || '-') + ' rows=' + t.querySelectorAll('tr').length);
        const links = [...document.querySelectorAll('a')].
            filter(a => /edition\\.php|ads\\.php/.test(a.href)).
            map(a => a.href.slice(0, 80));
        return {tables, links: links.slice(0, 8)};
    }""")
    for k, v in info.items():
        print(k, ":", v)
    rows = page.locator("table tbody tr")
    print("tbody rows:", rows.count())
    for i in range(min(rows.count(), 5)):
        tds = rows.nth(i).locator("td")
        cells = [tds.nth(j).inner_text().strip()[:25] for j in range(min(tds.count(), 10))]
        print("row", i, cells)
    page.screenshot(path="/tmp/libgen/editions.png")
    ctx.close()
    browser.close()
print("diag done")
