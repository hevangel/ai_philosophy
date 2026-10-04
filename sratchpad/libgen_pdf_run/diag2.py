import time

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.connect("ws://localhost:9222/hkej", timeout=60000)
    ctx = browser.new_context(viewport={"width": 1280, "height": 850})
    page = ctx.new_page()
    try:
        page.goto("https://libgen.li/", wait_until="commit", timeout=90000)
        print("goto ok")
    except Exception as e:
        print("goto fail:", type(e).__name__, str(e)[:120])
    time.sleep(14)
    print("title:", page.title())
    print("url:", page.url)
    print("req count:", page.locator('input[name="req"]').count())
    try:
        page.wait_for_selector('input[name="req"]', timeout=30000)
        print("selector ok")
        box = page.locator('input[name="req"]').first
        box.click(timeout=20000)
        print("click ok")
        box.type("Dark Tower and Philosophy", delay=80)
        box.press("Enter")
        page.wait_for_url("**index.php**", timeout=60000)
        print("search url:", page.url)
        page.wait_for_selector("#tablelibgen tbody tr", timeout=60000)
        rows = page.locator("#tablelibgen tbody tr")
        print("rows:", rows.count())
        for i in range(min(rows.count(), 6)):
            tds = rows.nth(i).locator("td")
            if tds.count() >= 9:
                print("row", i, tds.nth(7).inner_text().strip().lower(), "|", tds.nth(2).inner_text()[:60])
    except Exception as e:
        print("FAIL:", type(e).__name__, str(e)[:200])
    page.screenshot(path="/tmp/libgen/home2.png")
    ctx.close()
    browser.close()
print("diag done")
