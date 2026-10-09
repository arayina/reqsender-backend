from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.execution_repository import ExecutionRepository


router = APIRouter(
    prefix="/executions",
    tags=["Executions"],
)


def get_repository(
    db: Session = Depends(get_db),
) -> ExecutionRepository:
    return ExecutionRepository(db)


@router.get("/urls/{target_url_id}/summary")
def get_url_summary(
    target_url_id: UUID,
    repository: ExecutionRepository = Depends(
        get_repository
    ),
):
    return repository.get_url_summary(
        target_url_id
    )


@router.get("/urls/{target_url_id}/proxies")
def get_url_proxy_summary(
    target_url_id: UUID,
    repository: ExecutionRepository = Depends(
        get_repository
    ),
):
    return repository.get_proxy_summary(
        target_url_id
    )


@router.get("/urls/{target_url_id}/recent")
def get_recent_executions(
    target_url_id: UUID,
    limit: int = 100,
    repository: ExecutionRepository = Depends(
        get_repository
    ),
):
    executions = repository.get_recent(
        target_url_id=target_url_id,
        limit=min(limit, 500),
    )

    return [
        {
            "id": str(execution.id),
            "proxy_id": (
                str(execution.proxy_id)
                if execution.proxy_id
                else None
            ),
            "execution_mode": execution.execution_mode,
            "success": execution.success,
            "status_code": execution.status_code,
            "latency_ms": execution.latency_ms,
            "final_url": execution.final_url,
            "error": execution.error,
            "created_at": execution.created_at,
        }
        for execution in executions
    ]