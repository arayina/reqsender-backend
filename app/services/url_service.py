from uuid import UUID

from app.models.url import TargetUrl
from app.repositories.url_repository import TargetUrlRepository
from app.schemas.url import TargetUrlCreate, TargetUrlUpdate


class TargetUrlService:
    def __init__(self, repository: TargetUrlRepository):
        self.repository = repository

    def create_url(self, data: TargetUrlCreate) -> TargetUrl:
        target_url = TargetUrl(
            url=data.url,
            name=data.name,
            enabled=data.enabled,
        )

        return self.repository.create(target_url)

    def get_urls(self) -> list[TargetUrl]:
        return self.repository.get_all()

    def get_url(self, url_id: UUID) -> TargetUrl | None:
        return self.repository.get_by_id(url_id)

    def update_url(
        self,
        url_id: UUID,
        data: TargetUrlUpdate,
    ) -> TargetUrl | None:
        update_data = data.model_dump(exclude_unset=True)

        return self.repository.update(
            url_id,
            update_data,
        )

    def delete_url(self, url_id: UUID) -> bool:
        return self.repository.delete(url_id)