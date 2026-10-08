from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.proxy_repository import ProxyRepository
from app.schemas.request import RequestCreate, RequestResponse
from app.services.request_service import RequestService


router = APIRouter(
    prefix="/requests",
    tags=["Requests"],
)


def get_request_service(
    db: Session = Depends(get_db),
) -> RequestService:
    proxy_repository = ProxyRepository(db)

    return RequestService(
        proxy_repository=proxy_repository,
    )


@router.post("", response_model=RequestResponse)
async def execute_request(
    data: RequestCreate,
    service: RequestService = Depends(get_request_service),
):
    try:
        return await service.execute(
            url=data.url,
            proxy_id=data.proxy_id,
            mode=data.mode,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )