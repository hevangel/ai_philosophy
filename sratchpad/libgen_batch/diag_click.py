"""Diagnose what happens after clicking the GET link."""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(r"B:\ai_philosophy\sratchpad\libgen_batch\test")
MD5 = "8d23f0442eaa96b5d7e8641d984ad4ff"


def main() -> None:
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(accept_downloads=True)
        page = ctx.new_page()
        page.goto(f"https://libgen.li/ads.php?md5={MD5}", wait_until="commit", timeout=60000)
        page.wait_for_timeout(8000)
        link = page.locator('a[href*="get.php"]').first
        link.click(no_wait_after=True)
        page.wait_for_timeout(10000)
        print("pages:", len(ctx.pages))
        for pg in ctx.pages:
            print("  url:", pg.url[:120])
        try:
            html = page.content()
            print("page len:", len(html))
            import re
            t = re.search(r"<title>([^<]*)</title>", html)
            print("title:", t.group(1) if t else None)
            print("body snippet:", re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))[:300])
        except Exception as e:
            print("content failed:", e)
        b.close()


if __name__ == "__main__":
    main()
