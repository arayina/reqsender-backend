from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.url_settings import TargetUrlSettings


class TargetUrlSettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_url_id(self, target_url_id: UUID) -> TargetUrlSettings | None:
        return self.db.scalar(
            select(TargetUrlSettings).where(
                TargetUrlSettings.target_url_id == target_url_id
            )
        )

    def get_all(self) -> list[TargetUrlSettings]:
        return list(self.db.scalars(select(TargetUrlSettings)).all())

    def create(self, settings: TargetUrlSettings) -> TargetUrlSettings:
        self.db.add(settings)
        self.db.commit()
        self.db.refresh(settings)
        return settings

    def update(self, settings: TargetUrlSettings, data: dict) -> TargetUrlSettings:
        for field, value in data.items():
            setattr(settings, field, value)
        self.db.commit()
        self.db.refresh(settings)
        return settings
