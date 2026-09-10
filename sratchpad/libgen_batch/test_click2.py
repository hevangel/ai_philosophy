"""Click-download test with proper UA override."""
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(r"B:\ai_philosophy\sratchpad\libgen_batch\test")
MD5 = "8d23f0442eaa96b5d7e8641d984ad4ff"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(accept_downloads=True, user_agent=UA)
        page = ctx.new_page()

        saved: list[str] = []
        responses: list[str] = []

        def on_download(dl) -> None:
            path = OUT / "seinfeld_click2.epub"
            dl.save_as(str(path))
            saved.append(str(path))

        def on_response(resp) -> None:
            if "get.php" in resp.url:
                responses.append(f"{resp.status} {resp.url[:80]}")

        page.on("download", on_download)
        page.on("response", on_response)

        page.goto(f"https://libgen.li/ads.php?md5={MD5}", wait_until="commit", timeout=60000)
        page.wait_for_timeout(8000)
        link = page.locator('a[href*="get.php"]').first
        print("href:", link.get_attribute("href"))
        link.click(no_wait_after=True)
        for _ in range(45):
            if saved:
                break
            page.wait_for_timeout(2000)
        print("get.php responses:", responses)
        if saved:
            print("SAVED", saved[0], Path(saved[0]).stat().st_size, "bytes")
        else:
            print("no download; final url:", page.url[:100])
        b.close()


if __name__ == "__main__":
    main()
