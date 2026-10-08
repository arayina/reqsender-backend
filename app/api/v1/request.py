from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.proxy_repository import ProxyRepository
from app.schemas.request import (
    BatchRequestCreate,
    BatchRequestResponse,
    RequestCreate,
    RequestResponse,
)
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
        
@router.post(
    "/batch",
    response_model=BatchRequestResponse,
)
async def execute_batch_request(
    data: BatchRequestCreate,
    service: RequestService = Depends(get_request_service),
):
    try:
        results = await service.execute_batch(
            url=data.url,
            proxy_id=data.proxy_id,
            mode=data.mode,
            count=data.count,
            concurrency=data.concurrency,
        )

        success_count = sum(
            1
            for result in results
            if result["success"]
        )

        return {
            "total": len(results),
            "success": success_count,
            "failed": len(results) - success_count,
            "results": results,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )