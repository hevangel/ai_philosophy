import time

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.connect("ws://localhost:9222/hkej", timeout=60000)
    ctx = browser.new_context(viewport={"width": 1280, "height": 850})
    page = ctx.new_page()
    page.goto("https://libgen.li/index.php?req=Dark+Tower+and+Philosophy", timeout=90000)
    page.wait_for_load_state("domcontentloaded", timeout=90000)
    time.sleep(10)
    print("url:", page.url[:120])
    print("title:", page.title())
    info = page.evaluate("""() => {
        const tables = [...document.querySelectorAll('table')].map(t =>
            'table#' + (t.id || '-') + '.' + (t.className || '-') + ' rows=' + t.querySelectorAll('tr').length);
        const inputs = [...document.querySelectorAll('input')].map(i => i.name).filter(Boolean);
        const forms = [...document.querySelectorAll('form')].map(f => (f.id || '-') + ':' + (f.action || '-'));
        const bodyLen = document.body.innerHTML.length;
        return {tables, inputs, forms, bodyLen};
    }""")
    for k, v in info.items():
        print(k, ":", v)
    page.screenshot(path="/tmp/libgen/results.png", full_page=False)
    ctx.close()
    browser.close()
print("diag done")
