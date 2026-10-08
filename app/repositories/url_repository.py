from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.url import TargetUrl


class TargetUrlRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, target_url: TargetUrl) -> TargetUrl:
        self.db.add(target_url)
        self.db.commit()
        self.db.refresh(target_url)
        return target_url

    def get_all(self) -> list[TargetUrl]:
        statement = select(TargetUrl)
        return list(self.db.scalars(statement).all())

    def get_by_id(self, url_id: UUID) -> TargetUrl | None:
        return self.db.get(TargetUrl, url_id)

    def update(
        self,
        url_id: UUID,
        data: dict,
    ) -> TargetUrl | None:
        target_url = self.db.get(TargetUrl, url_id)

        if target_url is None:
            return None

        for field, value in data.items():
            setattr(target_url, field, value)

        self.db.commit()
        self.db.refresh(target_url)

        return target_url

    def delete(self, url_id: UUID) -> bool:
        target_url = self.db.get(TargetUrl, url_id)

        if target_url is None:
            return False

        self.db.delete(target_url)
        self.db.commit()

        return True