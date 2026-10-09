import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.proxy_repository import ProxyRepository
from app.schemas.request import (
    BatchRequestCreate,
    BatchRequestResponse,
    RequestCreate,
    RequestResponse,
)
from app.services.execution_service import ExecutionService
from app.services.request_service import RequestService


router = APIRouter(
    prefix="/requests",
    tags=["Requests"],
)


def get_request_service(
    db: Session = Depends(get_db),
) -> RequestService:
    return RequestService(
        proxy_repository=ProxyRepository(db),
    )


def get_execution_service(
    db: Session = Depends(get_db),
) -> ExecutionService:
    return ExecutionService(
        proxy_repository=ProxyRepository(db),
    )


@router.post(
    "",
    response_model=RequestResponse,
)
async def execute_request(
    data: RequestCreate,
    service: RequestService = Depends(
        get_request_service
    ),
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
    service: ExecutionService = Depends(
        get_execution_service
    ),
):
    try:
        events = []

        async for event in service.execute_batch_stream(
            url=data.url,
            proxy_ids=data.proxy_ids,
            proxy_strategy=data.proxy_strategy,
            mode=data.mode,
            count=data.count,
            concurrency=data.concurrency,
        ):
            if event["type"] == "progress":
                events.append(event)

        results = [
            event["result"]
            for event in events
        ]

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


@router.post(
    "/batch/stream"
)
async def execute_batch_stream(
    data: BatchRequestCreate,
    service: ExecutionService = Depends(
        get_execution_service
    ),
):
    async def event_generator():
        try:
            async for event in service.execute_batch_stream(
                url=data.url,
                proxy_ids=data.proxy_ids,
                proxy_strategy=data.proxy_strategy,
                mode=data.mode,
                count=data.count,
                concurrency=data.concurrency,
            ):
                yield (
                    f"data: "
                    f"{json.dumps(event)}"
                    f"\n\n"
                )

        except Exception as exc:
            error_event = {
                "type": "error",
                "error": str(exc),
            }

            yield (
                f"data: "
                f"{json.dumps(error_event)}"
                f"\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )