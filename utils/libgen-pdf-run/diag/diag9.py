import time

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.connect("ws://localhost:9222/hkej", timeout=60000)
    ctx = browser.new_context(viewport={"width": 1280, "height": 850})
    page = ctx.new_page()
    page.goto("https://libgen.li/index.php?req=Seinfeld+and+Philosophy", timeout=90000)
    page.wait_for_load_state("domcontentloaded", timeout=90000)
    time.sleep(8)
    print("url:", page.url[:110])
    tabs = page.evaluate("""() => [...document.querySelectorAll('a.nav-link')].
        map(a => (a.textContent || '').trim().slice(0, 20) + ' -> ' + (a.getAttribute('href') || ''))""")
    for t in tabs[:10]:
        print("  tab:", t)
    info = page.evaluate("""() => {
        const t = document.querySelector('#tablelibgen');
        if (!t) return {table: false};
        const rows = [...t.querySelectorAll('tbody tr')];
        const first = rows.slice(0, 3).map(r =>
            [...r.querySelectorAll('td')].map(td => (td.textContent || '').trim().slice(0, 22)));
        return {table: true, nrows: rows.length, first};
    }""")
    print(info)
    page.screenshot(path="/tmp/libgen/files.png")
    ctx.close()
    browser.close()
print("diag done")
