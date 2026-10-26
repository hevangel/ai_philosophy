import time

from playwright.sync_api import sync_playwright

QUERIES = [
    "Beatles and Philosophy",
    "Beatles Philosophy Nothing You Can Think",
    "Joss Whedon as Philosopher",
    "Facebook and Philosophy What's on Your Mind",
]

with sync_playwright() as p:
    browser = p.firefox.connect("ws://localhost:9222/hkej", timeout=60000)
    ctx = browser.new_context(viewport={"width": 1280, "height": 850})
    page = ctx.new_page()
    for q in QUERIES:
        url = "https://libgen.li/index.php?req=" + q.replace(" ", "+")
        try:
            page.goto(url, timeout=90000, wait_until="domcontentloaded")
        except Exception as e:
            print(q, "goto fail", str(e)[:60])
            continue
        time.sleep(7)
        rows = page.locator("#tablelibgen tbody tr")
        n = rows.count()
        print(f"== {q!r}: {n} file rows")
        for i in range(min(n, 10)):
            tds = rows.nth(i).locator("td")
            cnt = tds.count()
            if cnt < 2:
                continue
            title = tds.nth(1).inner_text().strip().splitlines()[0][:70] if cnt > 1 else ""
            ext = tds.nth(7).inner_text().strip()[:4] if cnt > 7 else ""
            link = tds.nth(1).locator('a[href*="edition.php?id="]').first
            href = link.get_attribute("href") if link.count() else ""
            print(f"   {ext:5} {title}  [{href[-14:]}]")
        time.sleep(4)
    ctx.close()
    browser.close()
