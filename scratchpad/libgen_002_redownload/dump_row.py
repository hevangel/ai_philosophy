import time

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.connect("ws://localhost:9222/hkej", timeout=60000)
    ctx = browser.new_context(viewport={"width": 1280, "height": 850})
    page = ctx.new_page()
    page.goto("https://libgen.li/index.php?req=The+Simpsons+and+Philosophy&curtab=e",
              timeout=90000)
    page.wait_for_load_state("domcontentloaded", timeout=90000)
    time.sleep(8)
    rows = page.locator("#tablelibgen tbody tr")
    print("rowcount:", rows.count())
    html = rows.nth(1).get_attribute("outerHTML") or rows.nth(1).inner_html()
    print(html[:3500])
    ctx.close()
    browser.close()
