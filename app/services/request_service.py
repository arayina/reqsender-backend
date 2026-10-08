from uuid import UUID

from app.executors.http_executor import execute_http_request
from app.repositories.proxy_repository import ProxyRepository


class RequestService:
    def __init__(self, proxy_repository: ProxyRepository):
        self.proxy_repository = proxy_repository

    async def execute(
        self,
        url: str,
        proxy_id: UUID | None = None,
    ) -> dict:

        proxy = None

        if proxy_id is not None:
            proxy = self.proxy_repository.get_by_id(proxy_id)

            if proxy is None:
                raise ValueError("Proxy not found")

        return await execute_http_request(
            url=url,
            proxy=proxy,
        )