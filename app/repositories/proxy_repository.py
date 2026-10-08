from uuid import UUID

from app.models.proxy import Proxy


class ProxyRepository:
    def __init__(self):
        self._proxies: dict[UUID, Proxy] = {}

    def create(self, proxy: Proxy) -> Proxy:
        self._proxies[proxy.id] = proxy
        return proxy

    def get_all(self) -> list[Proxy]:
        return list(self._proxies.values())

    def get_by_id(self, proxy_id: UUID) -> Proxy | None:
        return self._proxies.get(proxy_id)

    def delete(self, proxy_id: UUID) -> bool:
        if proxy_id not in self._proxies:
            return False

        del self._proxies[proxy_id]
        return True