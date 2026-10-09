import time
from uuid import UUID

from playwright.async_api import Page

from app.browser.browser_manager import browser_manager
from app.models.proxy import Proxy
from app.schemas.browser import BrowserSettings


CHROME_PATH = (
    r"C:\Program Files\Google"
    r"\Chrome\Application\chrome.exe"
)


async def execute_browser_request(
    url: str,
    target_url_id: UUID,
    proxy: Proxy | None = None,
    settings: BrowserSettings | None = None,
) -> dict:

    settings = settings or BrowserSettings()

    started_at = time.perf_counter()

    page: Page | None = None

    # Direct browser uses its own context.
    direct_playwright = None
    direct_context = None

    try:
        # =====================================================
        # DIRECT BROWSER
        # =====================================================

        if proxy is None:

            from playwright.async_api import async_playwright

            direct_playwright = (
                await async_playwright().start()
            )

            direct_context = (
                await direct_playwright
                .chromium
                .launch_persistent_context(
                    user_data_dir=(
                        ".browser_profiles"
                        "/direct"
                    ),
                    executable_path=CHROME_PATH,
                    headless=not settings.show_browser,
                )
            )

            context = direct_context

        # =====================================================
        # PROXY BROWSER
        # =====================================================

        else:

            session = (
                await browser_manager.get_session(
                    target_url_id=target_url_id,
                    proxy=proxy,
                    show_browser=settings.show_browser,
                )
            )

            context = session.context

        # =====================================================
        # CREATE PAGE
        # =====================================================

        page = await context.new_page()

        # -----------------------------------------------------
        # Delay before navigation
        # -----------------------------------------------------

        if settings.delay_before_navigation_ms > 0:
            await page.wait_for_timeout(
                settings.delay_before_navigation_ms
            )

        # -----------------------------------------------------
        # Navigation
        # -----------------------------------------------------

        response = await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=settings.navigation_timeout_ms,
        )

        # -----------------------------------------------------
        # Wait after load
        # -----------------------------------------------------

        if settings.wait_after_load_ms > 0:
            await page.wait_for_timeout(
                settings.wait_after_load_ms
            )

        # -----------------------------------------------------
        # Scroll
        # -----------------------------------------------------

        if settings.scroll_enabled:
            await page.mouse.wheel(
                0,
                settings.scroll_amount,
            )

            if settings.wait_after_scroll_ms > 0:
                await page.wait_for_timeout(
                    settings.wait_after_scroll_ms
                )

        # -----------------------------------------------------
        # Additional delay
        # -----------------------------------------------------

        if settings.delay_after_navigation_ms > 0:
            await page.wait_for_timeout(
                settings.delay_after_navigation_ms
            )

        # -----------------------------------------------------
        # Title
        # -----------------------------------------------------

        title = await page.title()

        # -----------------------------------------------------
        # Metrics
        # -----------------------------------------------------

        latency_ms = round(
            (
                time.perf_counter()
                - started_at
            )
            * 1000,
            2,
        )

        return {
            "success": True,
            "status_code": (
                response.status
                if response
                else None
            ),
            "latency_ms": latency_ms,
            "final_url": page.url,
            "title": title,
            "error": None,
        }

    except Exception as exc:

        latency_ms = round(
            (
                time.perf_counter()
                - started_at
            )
            * 1000,
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

        # =====================================================
        # PAGE LIFECYCLE
        #
        # Every request gets a new Page.
        # Page is always closed after the request.
        # =====================================================

        if page is not None:
            try:
                await page.close()
            except Exception:
                pass

        # =====================================================
        # DIRECT BROWSER LIFECYCLE
        #
        # Direct browsers are not managed by BrowserManager,
        # so close their context after the request.
        #
        # Proxy browsers stay alive until close_target().
        # =====================================================

        if direct_context is not None:
            try:
                await direct_context.close()
            except Exception:
                pass

        if direct_playwright is not None:
            try:
                await direct_playwright.stop()
            except Exception:
                pass