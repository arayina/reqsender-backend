import asyncio

from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=False,
            proxy={
                "server": "socks5://37.202.244.195:1080",
            },
        )

        page = await browser.new_page()

        try:
            response = await page.goto(
                "https://api.ipify.org",
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            print("STATUS:", response.status if response else None)
            print("URL:", page.url)
            print("BODY:", await page.locator("body").inner_text())

            await page.wait_for_timeout(5000)

        except Exception as exc:
            print("ERROR:", repr(exc))

        finally:
            await browser.close()


asyncio.run(main())