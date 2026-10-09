from uuid import UUID

from sqlalchemy import func, select, Integer
from sqlalchemy.orm import Session

from app.models.execution import Execution


class ExecutionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        target_url_id: UUID | None,
        proxy_id: UUID | None,
        execution_mode: str,
        success: bool,
        status_code: int | None,
        latency_ms: float,
        final_url: str | None,
        error: str | None,
    ) -> Execution:
        execution = Execution(
            target_url_id=target_url_id,
            proxy_id=proxy_id,
            execution_mode=execution_mode,
            success=success,
            status_code=status_code,
            latency_ms=latency_ms,
            final_url=final_url,
            error=error,
        )

        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)

        return execution

    def get_url_summary(
        self,
        target_url_id: UUID,
    ) -> dict:
        total = self.db.scalar(
            select(func.count(Execution.id)).where(
                Execution.target_url_id == target_url_id
            )
        ) or 0

        success = self.db.scalar(
            select(func.count(Execution.id)).where(
                Execution.target_url_id == target_url_id,
                Execution.success.is_(True),
            )
        ) or 0

        failed = total - success

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": round(
                (success / total) * 100,
                2,
            ) if total else 0,
        }

    def get_proxy_summary(
        self,
        target_url_id: UUID,
    ) -> list[dict]:
        rows = self.db.execute(
            select(
                Execution.proxy_id,
                Execution.execution_mode,
                func.count(Execution.id),
                func.sum(
                    func.cast(
                        Execution.success,
                        Integer,
                    )
                ),
            )
            .where(
                Execution.target_url_id == target_url_id
            )
            .group_by(
                Execution.proxy_id,
                Execution.execution_mode,
            )
            .order_by(
                func.count(Execution.id).desc()
            )
        ).all()

        result = []

        for proxy_id, mode, total, success in rows:
            success = success or 0

            result.append(
                {
                    "proxy_id": (
                        str(proxy_id)
                        if proxy_id
                        else None
                    ),
                    "execution_mode": mode,
                    "total": total,
                    "success": success,
                    "failed": total - success,
                }
            )

        return result

    def get_recent(
        self,
        target_url_id: UUID,
        limit: int = 100,
    ) -> list[Execution]:
        return list(
            self.db.scalars(
                select(Execution)
                .where(
                    Execution.target_url_id == target_url_id
                )
                .order_by(
                    Execution.created_at.desc()
                )
                .limit(limit)
            )
        )