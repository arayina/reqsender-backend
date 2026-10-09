from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.url_proxy_repository import UrlProxyRepository
from app.repositories.url_repository import TargetUrlRepository
from app.repositories.url_settings_repository import TargetUrlSettingsRepository
from app.schemas.url_settings import TargetUrlSettingsResponse, TargetUrlSettingsUpdate
from app.services.url_settings_service import TargetUrlSettingsService


router = APIRouter(
    prefix="/urls",
    tags=["URL Settings"],
)


def get_service(db: Session = Depends(get_db)) -> TargetUrlSettingsService:
    return TargetUrlSettingsService(
        settings_repository=TargetUrlSettingsRepository(db),
        proxy_repository=UrlProxyRepository(db),
    )


def ensure_url_exists(db: Session, url_id: UUID) -> None:
    if TargetUrlRepository(db).get_by_id(url_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found",
        )


@router.get(
    "/settings",
    response_model=list[TargetUrlSettingsResponse],
)
def get_all_url_settings(
    service: TargetUrlSettingsService = Depends(get_service),
    db: Session = Depends(get_db),
):
    urls = TargetUrlRepository(db).get_all()
    return service.get_all([item.id for item in urls])


@router.get(
    "/{url_id}/settings",
    response_model=TargetUrlSettingsResponse,
)
def get_url_settings(
    url_id: UUID,
    service: TargetUrlSettingsService = Depends(get_service),
    db: Session = Depends(get_db),
):
    ensure_url_exists(db, url_id)
    return service.get(url_id)


@router.put(
    "/{url_id}/settings",
    response_model=TargetUrlSettingsResponse,
)
def update_url_settings(
    url_id: UUID,
    data: TargetUrlSettingsUpdate,
    service: TargetUrlSettingsService = Depends(get_service),
    db: Session = Depends(get_db),
):
    ensure_url_exists(db, url_id)
    return service.update(url_id, data)
