import time

from playwright.async_api import (
    ProxySettings,
    async_playwright,
)

from app.models.proxy import Proxy


CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


async def execute_browser_request(
    url: str,
    proxy: Proxy | None = None,
) -> dict:
    proxy_config: ProxySettings | None = None

    if proxy:
        proxy_config = {
            "server": f"{proxy.protocol}://{proxy.host}:{proxy.port}",
            "username": proxy.username,
            "password": proxy.password,
        }

    started_at = time.perf_counter()

    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                executable_path=CHROME_PATH,
                headless=False,
                proxy=proxy_config,
            )

            page = await browser.new_page()

            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30_000,
            )

            title = await page.title()

            latency_ms = round(
                (time.perf_counter() - started_at) * 1000,
                2,
            )

            result = {
                "success": True,
                "status_code": response.status if response else None,
                "latency_ms": latency_ms,
                "final_url": page.url,
                "title": title,
                "error": None,
            }

            await browser.close()

            return result

    except Exception as exc:
        latency_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        return {
            "success": False,
            "status_code": None,
            "latency_ms": latency_ms,
            "final_url": None,
            "title": None,
            "error": str(exc),
        }