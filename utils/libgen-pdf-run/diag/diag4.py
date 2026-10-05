import time

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.connect("ws://localhost:9222/hkej", timeout=60000)
    ctx = browser.new_context(viewport={"width": 1280, "height": 850})
    page = ctx.new_page()
    page.goto("https://libgen.li/", wait_until="commit", timeout=90000)
    time.sleep(14)
    box = page.locator('input[name="req"]').first
    b1 = box.bounding_box()
    time.sleep(1.0)
    b2 = box.bounding_box()
    print("stable bbox:", b1 == b2, b1, b2)

    # bypass actionability: coordinate click + keyboard typing
    page.mouse.click(b2["x"] + 200, b2["y"] + b2["height"] / 2)
    time.sleep(1.0)
    print("focused:", page.evaluate(
        "document.activeElement ? document.activeElement.name || document.activeElement.tagName : 'none'"))
    page.keyboard.type("Dark Tower and Philosophy", delay=70)
    time.sleep(0.8)
    page.keyboard.press("Enter")
    try:
        page.wait_for_url("**index.php**", timeout=60000)
        print("search url:", page.url[:100])
        page.wait_for_selector("#tablelibgen tbody tr", timeout=60000)
        rows = page.locator("#tablelibgen tbody tr")
        print("rows:", rows.count())
        for i in range(min(rows.count(), 8)):
            tds = rows.nth(i).locator("td")
            if tds.count() >= 9:
                print("row", i, repr(tds.nth(7).inner_text().strip().lower()),
                      "|", tds.nth(2).inner_text()[:70])
    except Exception as e:
        print("FAIL:", type(e).__name__, str(e)[:200])
    ctx.close()
    browser.close()
print("diag done")
