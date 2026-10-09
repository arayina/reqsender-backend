import time
from uuid import UUID

from playwright.async_api import Page

from app.browser.browser_manager import browser_manager
from app.models.proxy import Proxy
from app.schemas.browser import BrowserSettings


async def execute_browser_request(
    url: str,
    target_url_id: UUID,
    proxy: Proxy | None = None,
    settings: BrowserSettings | None = None,
) -> dict:
    settings = settings or BrowserSettings()
    started_at = time.perf_counter()
    page: Page | None = None

    try:
        session = await browser_manager.get_session(
            target_url_id=target_url_id,
            proxy=proxy,
            show_browser=settings.show_browser,
        )
        page = await session.context.new_page()

        if settings.delay_before_navigation_ms > 0:
            await page.wait_for_timeout(settings.delay_before_navigation_ms)

        response = await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=settings.navigation_timeout_ms,
        )

        if settings.wait_after_load_ms > 0:
            await page.wait_for_timeout(settings.wait_after_load_ms)

        if settings.scroll_enabled:
            await page.mouse.wheel(0, settings.scroll_amount)
            if settings.wait_after_scroll_ms > 0:
                await page.wait_for_timeout(settings.wait_after_scroll_ms)

        if settings.delay_after_navigation_ms > 0:
            await page.wait_for_timeout(settings.delay_after_navigation_ms)

        title = await page.title()
        latency_ms = round((time.perf_counter() - started_at) * 1000, 2)

        return {
            "success": True,
            "status_code": response.status if response else None,
            "latency_ms": latency_ms,
            "final_url": page.url,
            "title": title,
            "error": None,
        }
    except Exception as exc:
        latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
        return {
            "success": False,
            "status_code": None,
            "latency_ms": latency_ms,
            "final_url": None,
            "title": None,
            "error": str(exc),
        }
    finally:
        if page is not None:
            try:
                await page.close()
            except Exception:
                pass
