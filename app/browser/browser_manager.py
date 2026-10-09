import asyncio
from pathlib import Path
from uuid import UUID

from playwright.async_api import (
    BrowserContext,
    Playwright,
    ProxySettings,
    async_playwright,
)

from app.models.proxy import Proxy


CHROME_PATH = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe"
)

PROFILE_ROOT = (
    Path(__file__).resolve().parents[2]
    / ".browser_profiles"
)


class BrowserSession:
    def __init__(
        self,
        target_url_id: UUID,
        proxy_id: UUID,
        context: BrowserContext,
        user_data_dir: Path,
        show_browser: bool,
    ):
        self.target_url_id = target_url_id
        self.proxy_id = proxy_id
        self.context = context
        self.user_data_dir = user_data_dir
        self.show_browser = show_browser


class BrowserManager:
    def __init__(self):
        self.playwright: Playwright | None = None

        # One browser session per:
        #
        # (target_url_id, proxy_id)
        #
        # Example:
        #
        # Target A + Proxy 1
        # Target A + Proxy 2
        # Target B + Proxy 1
        # Target B + Proxy 2
        self.sessions: dict[
            tuple[UUID, UUID],
            BrowserSession,
        ] = {}

        self.lock = asyncio.Lock()

    async def start(self) -> Playwright:
        """
        Start Playwright once and return
        a non-optional Playwright instance.
        """

        if self.playwright is None:
            self.playwright = (
                await async_playwright().start()
            )

        return self.playwright

    def _remove_session(
        self,
        target_url_id: UUID,
        proxy_id: UUID,
    ) -> None:
        """
        Remove a session after its BrowserContext
        has been closed manually or unexpectedly.
        """

        self.sessions.pop(
            (
                target_url_id,
                proxy_id,
            ),
            None,
        )

        print(
            "[BrowserManager] "
            f"Removed closed session "
            f"target={target_url_id} "
            f"proxy={proxy_id}"
        )

    async def get_session(
        self,
        target_url_id: UUID,
        proxy: Proxy,
        show_browser: bool,
    ) -> BrowserSession:

        playwright = await self.start()

        key = (
            target_url_id,
            proxy.id,
        )

        async with self.lock:

            # -------------------------------------------------
            # Reuse existing browser
            # -------------------------------------------------

            existing = self.sessions.get(key)

            if existing is not None:

                if not existing.context.is_closed():
                    return existing

                # Existing browser is closed/crashed.
                self.sessions.pop(
                    key,
                    None,
                )

                print(
                    "[BrowserManager] "
                    "Existing browser was closed. "
                    "Creating a new one. "
                    f"target={target_url_id} "
                    f"proxy={proxy.host}:{proxy.port}"
                )

            # -------------------------------------------------
            # Profile directory
            #
            # .browser_profiles/
            #   target_id/
            #     proxy_id/
            # -------------------------------------------------

            user_data_dir = (
                PROFILE_ROOT
                / str(target_url_id)
                / str(proxy.id)
            )

            user_data_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            # -------------------------------------------------
            # Proxy configuration
            # -------------------------------------------------

            proxy_config: ProxySettings = {
                "server": (
                    f"{proxy.protocol}://"
                    f"{proxy.host}:{proxy.port}"
                )
            }

            # Only add credentials when they exist.
            if proxy.username:
                proxy_config["username"] = (
                    proxy.username
                )

            if proxy.password:
                proxy_config["password"] = (
                    proxy.password
                )

            # -------------------------------------------------
            # Launch persistent browser
            # -------------------------------------------------

            context = (
                await playwright.chromium
                .launch_persistent_context(
                    user_data_dir=str(
                        user_data_dir
                    ),
                    executable_path=CHROME_PATH,
                    headless=not show_browser,
                    proxy=proxy_config,
                )
            )

            # -------------------------------------------------
            # Handle browser closing
            # -------------------------------------------------

            def handle_close(_context: BrowserContext) -> None:
                self._remove_session(
                    target_url_id,
                    proxy.id,
                )

            context.on(
                "close",
                handle_close,
            )

            # -------------------------------------------------
            # Store session
            # -------------------------------------------------

            session = BrowserSession(
                target_url_id=target_url_id,
                proxy_id=proxy.id,
                context=context,
                user_data_dir=user_data_dir,
                show_browser=show_browser,
            )

            self.sessions[key] = session

            print(
                "[BrowserManager] "
                f"Started browser "
                f"target={target_url_id} "
                f"proxy={proxy.host}:{proxy.port}"
            )

            return session

    async def close_session(
        self,
        target_url_id: UUID,
        proxy_id: UUID,
    ) -> None:

        key = (
            target_url_id,
            proxy_id,
        )

        async with self.lock:
            session = self.sessions.pop(
                key,
                None,
            )

        if session is None:
            return

        try:
            await session.context.close()
        except Exception:
            pass

        print(
            "[BrowserManager] "
            f"Closed browser "
            f"target={target_url_id} "
            f"proxy={proxy_id}"
        )

    async def close_target(
        self,
        target_url_id: UUID,
    ) -> None:
        """
        Close every browser belonging to
        the specified target.

        Example:

        Target A:
            Proxy 1 -> CLOSE
            Proxy 2 -> CLOSE

        Target B:
            Proxy 1 -> KEEP
            Proxy 2 -> KEEP
        """

        async with self.lock:

            target_sessions = [
                session
                for key, session in self.sessions.items()
                if key[0] == target_url_id
            ]

            for session in target_sessions:

                self.sessions.pop(
                    (
                        target_url_id,
                        session.proxy_id,
                    ),
                    None,
                )

        # Close contexts outside the manager lock.
        for session in target_sessions:

            try:
                await session.context.close()
            except Exception:
                pass

            print(
                "[BrowserManager] "
                f"Closed browser "
                f"target={target_url_id} "
                f"proxy={session.proxy_id}"
            )

    async def shutdown(self) -> None:
        """
        Close every browser when the
        application shuts down.
        """

        async with self.lock:

            sessions = list(
                self.sessions.values()
            )

            self.sessions.clear()

        # Close browsers outside the lock.
        for session in sessions:

            try:
                await session.context.close()
            except Exception:
                pass

        if self.playwright is not None:

            await self.playwright.stop()

            self.playwright = None

        print(
            "[BrowserManager] "
            "Shutdown complete"
        )


browser_manager = BrowserManager()