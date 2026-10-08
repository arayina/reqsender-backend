from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas.proxy import ProxyCreate, ProxyResponse
from app.services.proxy_service import ProxyService
from app.repositories.proxy_repository import ProxyRepository


router = APIRouter(
    prefix="/proxies",
    tags=["Proxies"],
)


repository = ProxyRepository()
service = ProxyService(repository)


@router.post(
    "",
    response_model=ProxyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_proxy(data: ProxyCreate):
    return service.create_proxy(data)


@router.get(
    "",
    response_model=list[ProxyResponse],
)
def get_proxies():
    return service.get_proxies()


@router.get(
    "/{proxy_id}",
    response_model=ProxyResponse,
)
def get_proxy(proxy_id: UUID):
    proxy = service.get_proxy(proxy_id)

    if proxy is None:
        raise HTTPException(
            status_code=404,
            detail="Proxy not found",
        )

    return proxy


@router.delete(
    "/{proxy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_proxy(proxy_id: UUID):
    deleted = service.delete_proxy(proxy_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Proxy not found",
        )