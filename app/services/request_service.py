import random
from uuid import UUID

from app.executors.browser_executer import execute_browser_request
from app.executors.http_executor import execute_http_request
from app.repositories.proxy_repository import ProxyRepository


class RequestService:
    def __init__(self, proxy_repository: ProxyRepository):
        self.proxy_repository = proxy_repository

    async def execute(
        self,
        url: str,
        proxy_id: UUID | None = None,
        mode: str = "http",
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
            )

        raise ValueError(f"Unsupported request mode: {mode}")