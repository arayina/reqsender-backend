from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.url_proxy import TargetUrlProxy


class UrlProxyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_proxy_ids(self, target_url_id: UUID) -> list[UUID]:
        rows = self.db.scalars(
            select(TargetUrlProxy.proxy_id).where(
                TargetUrlProxy.target_url_id == target_url_id
            )
        )
        return list(rows)

    def replace_proxy_ids(
        self,
        target_url_id: UUID,
        proxy_ids: list[UUID],
    ) -> list[UUID]:
        unique_ids = list(dict.fromkeys(proxy_ids))

        self.db.execute(
            delete(TargetUrlProxy).where(
                TargetUrlProxy.target_url_id == target_url_id
            )
        )

        for proxy_id in unique_ids:
            self.db.add(
                TargetUrlProxy(
                    target_url_id=target_url_id,
                    proxy_id=proxy_id,
                )
            )

        self.db.commit()
        return self.get_proxy_ids(target_url_id)
