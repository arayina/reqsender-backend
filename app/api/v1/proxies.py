from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.proxy_repository import ProxyRepository
from app.schemas.proxy import ProxyCreate, ProxyResponse
from app.services.proxy_service import ProxyService


router = APIRouter(
    prefix="/proxies",
    tags=["Proxies"],
)


def get_proxy_service(
    db: Session = Depends(get_db),
) -> ProxyService:
    repository = ProxyRepository(db)

    return ProxyService(repository)


@router.post(
    "",
    response_model=ProxyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_proxy(
    data: ProxyCreate,
    service: ProxyService = Depends(get_proxy_service),
):
    return service.create_proxy(data)


@router.get(
    "",
    response_model=list[ProxyResponse],
)
def get_proxies(
    service: ProxyService = Depends(get_proxy_service),
):
    return service.get_proxies()


@router.get(
    "/{proxy_id}",
    response_model=ProxyResponse,
)
def get_proxy(
    proxy_id: UUID,
    service: ProxyService = Depends(get_proxy_service),
):
    proxy = service.get_proxy(proxy_id)

    if proxy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proxy not found",
        )

    return proxy


@router.delete(
    "/{proxy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_proxy(
    proxy_id: UUID,
    service: ProxyService = Depends(get_proxy_service),
):
    deleted = service.delete_proxy(proxy_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proxy not found",
        )