import time

from playwright.async_api import ProxySettings, async_playwright

from app.models.proxy import Proxy
from app.schemas.browser import BrowserSettings


CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


async def execute_browser_request(
    url: str,
    proxy: Proxy | None = None,
    settings: BrowserSettings | None = None,
) -> dict:
    settings = settings or BrowserSettings()

    proxy_config: ProxySettings | None = None

    if proxy:
        proxy_config = {
            "server": f"{proxy.protocol}://{proxy.host}:{proxy.port}",
            "username": proxy.username,
            "password": proxy.password,
        }

    started_at = time.perf_counter()
    browser = None

    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                executable_path=CHROME_PATH,
                headless=not settings.show_browser,
                proxy=proxy_config,
            )

            page = await browser.new_page()

            if settings.delay_before_navigation_ms > 0:
                await page.wait_for_timeout(
                    settings.delay_before_navigation_ms
                )

            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=settings.navigation_timeout_ms,
            )

            if settings.wait_after_load_ms > 0:
                await page.wait_for_timeout(
                    settings.wait_after_load_ms
                )

            if settings.scroll_enabled:
                await page.evaluate(
                    "(amount) => window.scrollBy(0, amount)",
                    settings.scroll_amount,
                )

                if settings.wait_after_scroll_ms > 0:
                    await page.wait_for_timeout(
                        settings.wait_after_scroll_ms
                    )

            if settings.delay_after_navigation_ms > 0:
                await page.wait_for_timeout(
                    settings.delay_after_navigation_ms
                )

            title = await page.title()

            latency_ms = round(
                (time.perf_counter() - started_at) * 1000,
                2,
            )

            return {
                "success": True,
                "status_code": response.status if response else None,
                "latency_ms": latency_ms,
                "final_url": page.url,
                "title": title,
                "error": None,
            }

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

    finally:
        if browser is not None:
            try:
                await browser.close()
            except Exception:
                pass
