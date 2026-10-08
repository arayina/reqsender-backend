from uuid import UUID

from app.models.proxy import Proxy
from app.repositories.proxy_repository import ProxyRepository
from app.schemas.proxy import ProxyCreate, ProxyUpdate

class ProxyService:
    def __init__(self, repository: ProxyRepository):
        self.repository = repository

    def create_proxy(self, data: ProxyCreate) -> Proxy:
        proxy = Proxy(
            host=data.host,
            port=data.port,
            protocol=data.protocol,
            username=data.username,
            password=data.password,
            enabled=data.enabled,
        )

        return self.repository.create(proxy)

    def get_proxies(self) -> list[Proxy]:
        return self.repository.get_all()

    def get_proxy(self, proxy_id: UUID) -> Proxy | None:
        return self.repository.get_by_id(proxy_id)

    def delete_proxy(self, proxy_id: UUID) -> bool:
        return self.repository.delete(proxy_id)
    
    
    def update_proxy(
        self,
        proxy_id: UUID,
        data: ProxyUpdate,
    ) -> Proxy | None:
        update_data = data.model_dump(exclude_unset=True)

        return self.repository.update(
            proxy_id,
            update_data,
        )