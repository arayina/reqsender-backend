import random
from uuid import UUID
import asyncio
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
    ) -> dict:
        proxy = None

        if proxy_id is not None:
            proxy = self.proxy_repository.get_by_id(proxy_id)

            if proxy is None:
                raise ValueError("Proxy not found")

            if not proxy.enabled:
                raise ValueError("Proxy is disabled")

        if mode == "http":
            return await execute_http_request(
                url=url,
                proxy=proxy,
            )

        if mode == "browser":
            return await execute_browser_request(
                url=url,
                proxy=proxy,
                settings=browser_settings,
            )

        if mode == "random":
            selected_mode = random.choice(["http", "browser"])

            if selected_mode == "http":
                return await execute_http_request(
                    url=url,
                    proxy=proxy,
                )

            return await execute_browser_request(
                url=url,
                proxy=proxy,
                settings=browser_settings,
            )

        raise ValueError(f"Unsupported request mode: {mode}")
    
    async def execute_batch(
        self,
        url: str,
        proxy_id: UUID | None = None,
        mode: str = "http",
        count: int = 1,
        concurrency: int = 1,
    ) -> list[dict]:
        semaphore = asyncio.Semaphore(concurrency)

        async def execute_one() -> dict:
            async with semaphore:
                return await self.execute(
                    url=url,
                    proxy_id=proxy_id,
                    mode=mode,
                    browser_settings=browser_settings,
                )

        tasks = [
            execute_one()
            for _ in range(count)
        ]

        return await asyncio.gather(*tasks)