import time

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.connect("ws://localhost:9222/hkej", timeout=60000)
    ctx = browser.new_context(viewport={"width": 1280, "height": 850})
    page = ctx.new_page()
    page.goto("https://libgen.li/", wait_until="domcontentloaded", timeout=90000)
    time.sleep(12)
    print("title:", page.title())
    print("url:", page.url)
    n = page.locator('input[name="req"]').count()
    print("input[req] count:", n)
    if n:
        el = page.locator('input[name="req"]').first
        print("visible:", el.is_visible(), "enabled:", el.is_enabled())
    for sel in ["iframe", "#cookie", ".modal", "[class*=consent]", "[id*=cf]", "[class*=challenge]"]:
        print(sel, page.locator(sel).count())
    page.screenshot(path="/tmp/libgen/home.png", full_page=False)
    ctx.close()
    browser.close()
print("diag done")
