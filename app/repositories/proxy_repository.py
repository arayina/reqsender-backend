from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.proxy import Proxy


class ProxyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, proxy: Proxy) -> Proxy:
        self.db.add(proxy)
        self.db.commit()
        self.db.refresh(proxy)

        return proxy

    def get_all(self) -> list[Proxy]:
        statement = select(Proxy)

        return list(
            self.db.scalars(statement).all()
        )

    def get_by_id(self, proxy_id: UUID) -> Proxy | None:
        return self.db.get(Proxy, proxy_id)

    def delete(self, proxy_id: UUID) -> bool:
        proxy = self.db.get(Proxy, proxy_id)

        if proxy is None:
            return False

        self.db.delete(proxy)
        self.db.commit()

        return True
    
    def update(self, proxy_id: UUID, data: dict) -> Proxy | None:
        proxy = self.db.get(Proxy, proxy_id)

        if proxy is None:
            return None

        for field, value in data.items():
            setattr(proxy, field, value)

        self.db.commit()
        self.db.refresh(proxy)

        return proxy