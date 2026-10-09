from uuid import UUID

from app.models.url_settings import TargetUrlSettings
from app.repositories.url_proxy_repository import UrlProxyRepository
from app.repositories.url_settings_repository import TargetUrlSettingsRepository
from app.schemas.url_settings import TargetUrlSettingsUpdate


class TargetUrlSettingsService:
    def __init__(
        self,
        settings_repository: TargetUrlSettingsRepository,
        proxy_repository: UrlProxyRepository,
    ):
        self.settings_repository = settings_repository
        self.proxy_repository = proxy_repository

    def _defaults(self, target_url_id: UUID) -> TargetUrlSettings:
        return TargetUrlSettings(target_url_id=target_url_id)

    def get(self, target_url_id: UUID) -> dict:
        settings = self.settings_repository.get_by_url_id(target_url_id)
        if settings is None:
            settings = self.settings_repository.create(
                self._defaults(target_url_id)
            )

        return self._to_dict(settings, self.proxy_repository.get_proxy_ids(target_url_id))

    def get_all(self, target_url_ids: list[UUID]) -> list[dict]:
        existing = {
            item.target_url_id: item
            for item in self.settings_repository.get_all()
        }
        result = []

        for target_url_id in target_url_ids:
            settings = existing.get(target_url_id)
            if settings is None:
                settings = self.settings_repository.create(
                    self._defaults(target_url_id)
                )

            result.append(
                self._to_dict(
                    settings,
                    self.proxy_repository.get_proxy_ids(target_url_id),
                )
            )

        return result

    def update(
        self,
        target_url_id: UUID,
        data: TargetUrlSettingsUpdate,
    ) -> dict:
        settings = self.settings_repository.get_by_url_id(target_url_id)
        if settings is None:
            settings = self.settings_repository.create(
                self._defaults(target_url_id)
            )

        payload = data.model_dump(exclude={"proxy_ids"})
        settings = self.settings_repository.update(settings, payload)
        proxy_ids = self.proxy_repository.replace_proxy_ids(
            target_url_id,
            data.proxy_ids,
        )

        return self._to_dict(settings, proxy_ids)

    @staticmethod
    def _to_dict(settings: TargetUrlSettings, proxy_ids: list[UUID]) -> dict:
        return {
            "target_url_id": settings.target_url_id,
            "mode": settings.mode,
            "connection": settings.connection,
            "proxy_strategy": settings.proxy_strategy,
            "proxy_ids": proxy_ids,
            "count": settings.count,
            "concurrency": settings.concurrency,
            "show_browser": settings.show_browser,
            "delay_before_navigation_ms": settings.delay_before_navigation_ms,
            "wait_after_load_ms": settings.wait_after_load_ms,
            "scroll_enabled": settings.scroll_enabled,
            "scroll_amount": settings.scroll_amount,
            "wait_after_scroll_ms": settings.wait_after_scroll_ms,
            "delay_after_navigation_ms": settings.delay_after_navigation_ms,
            "navigation_timeout_ms": settings.navigation_timeout_ms,
        }
