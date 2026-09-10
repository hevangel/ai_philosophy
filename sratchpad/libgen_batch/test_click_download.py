"""Single clean download test for libgen.li get.php after cooldown."""
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(r"B:\ai_philosophy\sratchpad\libgen_batch\test")
MD5 = "8d23f0442eaa96b5d7e8641d984ad4ff"  # Seinfeld and Philosophy (epub)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(accept_downloads=True)
        page = ctx.new_page()

        saved: list[str] = []

        def on_download(dl) -> None:
            path = OUT / "seinfeld_click.epub"
            dl.save_as(str(path))
            saved.append(str(path))

        page.on("download", on_download)
        page.goto(f"https://libgen.li/ads.php?md5={MD5}", wait_until="commit", timeout=60000)
        page.wait_for_timeout(8000)
        link = page.locator('a[href*="get.php"]').first
        href = link.get_attribute("href")
        print("href:", href)
        link.click(no_wait_after=True)
        # give the download handler time to fire
        for _ in range(60):
            if saved:
                break
            page.wait_for_timeout(2000)
        if saved:
            size = Path(saved[0]).stat().st_size
            print(f"SAVED {saved[0]} {size} bytes")
        else:
            print("no download event fired")
        b.close()


if __name__ == "__main__":
    main()
