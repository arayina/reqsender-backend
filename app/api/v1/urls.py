from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.url_repository import TargetUrlRepository
from app.schemas.url import (
    TargetUrlCreate,
    TargetUrlResponse,
    TargetUrlUpdate,
)
from app.services.url_service import TargetUrlService


router = APIRouter(
    prefix="/urls",
    tags=["URLs"],
)


def get_url_service(
    db: Session = Depends(get_db),
) -> TargetUrlService:
    repository = TargetUrlRepository(db)
    return TargetUrlService(repository)


@router.post(
    "",
    response_model=TargetUrlResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_url(
    data: TargetUrlCreate,
    service: TargetUrlService = Depends(get_url_service),
):
    return service.create_url(data)


@router.get(
    "",
    response_model=list[TargetUrlResponse],
)
def get_urls(
    service: TargetUrlService = Depends(get_url_service),
):
    return service.get_urls()


@router.get(
    "/{url_id}",
    response_model=TargetUrlResponse,
)
def get_url(
    url_id: UUID,
    service: TargetUrlService = Depends(get_url_service),
):
    target_url = service.get_url(url_id)

    if target_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found",
        )

    return target_url


@router.patch(
    "/{url_id}",
    response_model=TargetUrlResponse,
)
def update_url(
    url_id: UUID,
    data: TargetUrlUpdate,
    service: TargetUrlService = Depends(get_url_service),
):
    target_url = service.update_url(url_id, data)

    if target_url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found",
        )

    return target_url


@router.delete(
    "/{url_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_url(
    url_id: UUID,
    service: TargetUrlService = Depends(get_url_service),
):
    deleted = service.delete_url(url_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found",
        )