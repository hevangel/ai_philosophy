import time

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.connect("ws://localhost:9222/hkej", timeout=60000)
    ctx = browser.new_context(viewport={"width": 1280, "height": 850})
    page = ctx.new_page()
    page.goto("https://libgen.li/edition.php?id=148402452", timeout=90000,
              wait_until="domcontentloaded")
    time.sleep(8)
    info = page.evaluate("""() => {
        const tables = [...document.querySelectorAll('table')].map(t =>
            (t.id || '-') + '.' + (t.className || '-') + ' rows=' + t.querySelectorAll('tr').length);
        const links = [...document.querySelectorAll('a')].
            filter(a => /ads\\.php|get\\.php/.test(a.href)).
            map(a => a.href.slice(0, 90));
        const firstRows = [...document.querySelectorAll('table tbody tr')].slice(0, 12).
            map(r => [...r.querySelectorAll('td')].map(td => (td.textContent || '').trim().slice(0, 25)));
        return {tables, links: links.slice(0, 10), firstRows};
    }""")
    print("tables:", info["tables"])
    print("links:")
    for l in info["links"]:
        print("  ", l)
    for i, r in enumerate(info["firstRows"]):
        print("row", i, r)
    ctx.close()
    browser.close()
