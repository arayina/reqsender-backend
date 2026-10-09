import asyncio
from pathlib import Path
from uuid import UUID

from playwright.async_api import BrowserContext, Playwright, ProxySettings, async_playwright
from app.models.proxy import Proxy

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_ROOT = Path(__file__).resolve().parents[2] / ".browser_profiles"


class BrowserSession:
    def __init__(self, target_url_id: UUID, proxy_id: UUID | None, context: BrowserContext, user_data_dir: Path, show_browser: bool):
        self.target_url_id = target_url_id
        self.proxy_id = proxy_id
        self.context = context
        self.user_data_dir = user_data_dir
        self.show_browser = show_browser


class BrowserManager:
    def __init__(self):
        self.playwright: Playwright | None = None
        self.sessions: dict[tuple[UUID, UUID | None], BrowserSession] = {}
        self.target_leases: dict[UUID, int] = {}
        self.lock = asyncio.Lock()

    async def start(self) -> Playwright:
        async with self.lock:
            if self.playwright is None:
                self.playwright = await async_playwright().start()
            return self.playwright

    async def acquire_target(self, target_url_id: UUID) -> None:
        async with self.lock:
            self.target_leases[target_url_id] = self.target_leases.get(target_url_id, 0) + 1

    async def release_target(self, target_url_id: UUID) -> None:
        async with self.lock:
            current = self.target_leases.get(target_url_id, 0)
            if current <= 1:
                self.target_leases.pop(target_url_id, None)
                should_close = True
            else:
                self.target_leases[target_url_id] = current - 1
                should_close = False

        if should_close:
            await self.close_target(target_url_id)

    def _remove_session(self, target_url_id: UUID, proxy_id: UUID | None) -> None:
        self.sessions.pop((target_url_id, proxy_id), None)
        print(f"[BrowserManager] Removed closed session target={target_url_id} proxy={proxy_id}")

    async def get_session(self, target_url_id: UUID, proxy: Proxy | None, show_browser: bool) -> BrowserSession:
        playwright = await self.start()
        proxy_id = proxy.id if proxy is not None else None
        key = (target_url_id, proxy_id)

        async with self.lock:
            existing = self.sessions.get(key)
            if existing is not None:
                if not existing.context.is_closed():
                    return existing
                self.sessions.pop(key, None)

            user_data_dir = PROFILE_ROOT / str(target_url_id) / (str(proxy_id) if proxy_id is not None else "direct")
            user_data_dir.mkdir(parents=True, exist_ok=True)

            proxy_config: ProxySettings | None = None
            if proxy is not None:
                proxy_config = {"server": f"{proxy.protocol}://{proxy.host}:{proxy.port}"}
                if proxy.username:
                    proxy_config["username"] = proxy.username
                if proxy.password:
                    proxy_config["password"] = proxy.password

            context = await playwright.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                executable_path=CHROME_PATH,
                headless=not show_browser,
                proxy=proxy_config,
            )

            def handle_close(_context: BrowserContext) -> None:
                self._remove_session(target_url_id, proxy_id)

            context.on("close", handle_close)

            session = BrowserSession(target_url_id, proxy_id, context, user_data_dir, show_browser)
            self.sessions[key] = session
            print(f"[BrowserManager] Started browser target={target_url_id} proxy={proxy_id}")
            return session

    async def close_session(self, target_url_id: UUID, proxy_id: UUID | None) -> None:
        async with self.lock:
            session = self.sessions.pop((target_url_id, proxy_id), None)
        if session is None:
            return
        try:
            await session.context.close()
        except Exception:
            pass

    async def close_target(self, target_url_id: UUID) -> None:
        async with self.lock:
            target_sessions = [
                session for key, session in self.sessions.items()
                if key[0] == target_url_id
            ]
            for session in target_sessions:
                self.sessions.pop((target_url_id, session.proxy_id), None)

        for session in target_sessions:
            try:
                await session.context.close()
            except Exception:
                pass
            print(f"[BrowserManager] Closed browser target={target_url_id} proxy={session.proxy_id}")

    async def shutdown(self) -> None:
        async with self.lock:
            sessions = list(self.sessions.values())
            self.sessions.clear()
            self.target_leases.clear()

        for session in sessions:
            try:
                await session.context.close()
            except Exception:
                pass

        if self.playwright is not None:
            await self.playwright.stop()
            self.playwright = None

        print("[BrowserManager] Shutdown complete")


browser_manager = BrowserManager()
