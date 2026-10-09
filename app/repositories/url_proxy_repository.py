from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.url_proxy import TargetUrlProxy


class UrlProxyRepository:
    def __init__(self, db: Session):
        self.db = db

    def assign(
        self,
        target_url_id: UUID,
        proxy_id: UUID,
    ) -> TargetUrlProxy:
        existing = self.db.scalar(
            select(TargetUrlProxy).where(
                TargetUrlProxy.target_url_id == target_url_id,
                TargetUrlProxy.proxy_id == proxy_id,
            )
        )

        if existing:
            return existing

        assignment = TargetUrlProxy(
            target_url_id=target_url_id,
            proxy_id=proxy_id,
        )

        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)

        return assignment

    def remove(
        self,
        target_url_id: UUID,
        proxy_id: UUID,
    ) -> bool:
        assignment = self.db.scalar(
            select(TargetUrlProxy).where(
                TargetUrlProxy.target_url_id == target_url_id,
                TargetUrlProxy.proxy_id == proxy_id,
            )
        )

        if assignment is None:
            return False

        self.db.delete(assignment)
        self.db.commit()

        return True
    
    
    def get_proxy_ids(
        self,
        target_url_id: UUID,
    ) -> list[UUID]:
        rows = self.db.scalars(
            select(TargetUrlProxy.proxy_id).where(
                TargetUrlProxy.target_url_id == target_url_id
            )
        )

        return list(rows)