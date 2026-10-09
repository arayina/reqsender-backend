import asyncio
import random
from uuid import UUID, uuid4

from app.browser.browser_manager import browser_manager
from app.executors.browser_executer import execute_browser_request
from app.executors.http_executor import execute_http_request
from app.repositories.proxy_repository import ProxyRepository
from app.schemas.browser import BrowserSettings


class RequestService:
    def __init__(self, proxy_repository: ProxyRepository):
        self.proxy_repository = proxy_repository

    async def execute(
        self,
        url: str,
        proxy_id: UUID | None = None,
        mode: str = "http",
        browser_settings: BrowserSettings | None = None,
        target_url_id: UUID | None = None,
    ) -> dict:
        proxy = None

        if proxy_id is not None:
            proxy = self.proxy_repository.get_by_id(proxy_id)
            if proxy is None:
                raise ValueError("Proxy not found")
            if not proxy.enabled:
                raise ValueError("Proxy is disabled")

        actual_mode = random.choice(["http", "browser"]) if mode == "random" else mode

        if actual_mode == "http":
            result = await execute_http_request(url=url, proxy=proxy)
            result["execution_mode"] = actual_mode
            return result

        if actual_mode != "browser":
            raise ValueError(f"Unsupported request mode: {mode}")

        temporary_target_id = target_url_id is None
        effective_target_id = target_url_id or uuid4()

        try:
            result = await execute_browser_request(
                url=url,
                target_url_id=effective_target_id,
                proxy=proxy,
                settings=browser_settings,
            )
            result["execution_mode"] = actual_mode
            return result
        finally:
            if temporary_target_id:
                await browser_manager.close_target(effective_target_id)

    async def execute_batch(
        self,
        url: str,
        proxy_id: UUID | None = None,
        mode: str = "http",
        count: int = 1,
        concurrency: int = 1,
        browser_settings: BrowserSettings | None = None,
        target_url_id: UUID | None = None,
    ) -> list[dict]:
        if count < 1:
            raise ValueError("Count must be at least 1")
        if concurrency < 1:
            raise ValueError("Concurrency must be at least 1")

        semaphore = asyncio.Semaphore(concurrency)
        effective_target_id = target_url_id or uuid4()
        await browser_manager.acquire_target(effective_target_id)

        async def execute_one() -> dict:
            async with semaphore:
                return await self.execute(
                    url=url,
                    proxy_id=proxy_id,
                    mode=mode,
                    browser_settings=browser_settings,
                    target_url_id=effective_target_id,
                )

        tasks = [asyncio.create_task(execute_one()) for _ in range(count)]
        try:
            return await asyncio.gather(*tasks)
        finally:
            await browser_manager.release_target(effective_target_id)
