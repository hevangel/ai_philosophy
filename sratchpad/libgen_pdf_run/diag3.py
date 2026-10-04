import time

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.firefox.connect("ws://localhost:9222/hkej", timeout=60000)
    ctx = browser.new_context(viewport={"width": 1280, "height": 850})
    page = ctx.new_page()
    page.goto("https://libgen.li/", wait_until="commit", timeout=90000)
    time.sleep(14)
    box = page.locator('input[name="req"]').first
    print("visible:", box.is_visible())
    bb = box.bounding_box()
    print("bbox:", bb)
    if bb:
        x, y = bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2
        top = page.evaluate(
            "([x, y]) => { const el = document.elementFromPoint(x, y);"
            " return el ? el.tagName + ' ' + (el.id || '') + ' ' + (el.className || '') : 'none'; }",
            [x, y])
        print("elementFromPoint:", top)
        hits = page.evaluate(
            "([x, y]) => document.elementsFromPoint(x, y).slice(0, 5)"
            ".map(e => e.tagName + '#' + (e.id || '') + '.' + (e.className || '')).join(' | ')",
            [x, y])
        print("stack:", hits)
    page.screenshot(path="/tmp/libgen/home3.png")
    ctx.close()
    browser.close()
print("diag done")
