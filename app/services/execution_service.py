import asyncio
import random
import time
from collections.abc import AsyncIterator
from uuid import UUID

from app.executors.browser_executer import execute_browser_request
from app.executors.http_executor import execute_http_request
from app.repositories.execution_repository import ExecutionRepository
from app.repositories.proxy_repository import ProxyRepository
from app.schemas.browser import BrowserSettings


class ExecutionService:
    def __init__(
        self,
        proxy_repository: ProxyRepository,
        execution_repository: ExecutionRepository,
    ):
        self.proxy_repository = proxy_repository
        self.execution_repository = execution_repository

    async def execute_one(
        self,
        url: str,
        proxy_id: UUID | None = None,
        mode: str = "http",
        browser_settings: BrowserSettings | None = None,
    ) -> dict:
        proxy = None

        if proxy_id is not None:
            proxy = self.proxy_repository.get_by_id(proxy_id)

            if proxy is None:
                raise ValueError("Proxy not found")

            if not proxy.enabled:
                raise ValueError("Proxy is disabled")

        actual_mode = mode

        if mode == "random":
            actual_mode = random.choice(
                ["http", "browser"]
            )

        if actual_mode == "http":
            result = await execute_http_request(
                url=url,
                proxy=proxy,
            )

        elif actual_mode == "browser":
            result = await execute_browser_request(
                url=url,
                proxy=proxy,
                settings=browser_settings,
            )

        else:
            raise ValueError(
                f"Unsupported request mode: {mode}"
            )

        result["execution_mode"] = actual_mode

        return result

    def select_proxy_id(
        self,
        proxy_ids: list[UUID],
        strategy: str,
        index: int,
    ) -> UUID | None:
        """
        Select a proxy for a request based on strategy.
        """

        if not proxy_ids:
            return None

        if strategy == "fixed":
            return proxy_ids[0]

        if strategy == "round_robin":
            return proxy_ids[
                (index - 1) % len(proxy_ids)
            ]

        if strategy == "random":
            return random.choice(proxy_ids)

        raise ValueError(
            f"Unsupported proxy strategy: {strategy}"
        )

    async def execute_batch_stream(
        self,
        url: str,
        proxy_ids: list[UUID],
        proxy_strategy: str,
        mode: str,
        count: int,
        concurrency: int,
        browser_settings: BrowserSettings | None = None,
        target_url_id: UUID | None = None,
    ) -> AsyncIterator[dict]:
        semaphore = asyncio.Semaphore(
            concurrency
        )

        started_at = time.perf_counter()

        completed = 0
        success = 0
        failed = 0
        total_latency_ms = 0.0

        tasks: set[asyncio.Task] = set()

        def build_metrics() -> dict:
            elapsed_ms = (
                time.perf_counter()
                - started_at
            ) * 1000

            elapsed_seconds = (
                elapsed_ms / 1000
            )

            average_latency_ms = (
                total_latency_ms / completed
                if completed > 0
                else 0
            )

            requests_per_second = (
                completed / elapsed_seconds
                if elapsed_seconds > 0
                else 0
            )

            success_rate = (
                (success / completed) * 100
                if completed > 0
                else 0
            )

            return {
                "elapsed_ms": round(
                    elapsed_ms,
                    2,
                ),
                "average_latency_ms": round(
                    average_latency_ms,
                    2,
                ),
                "requests_per_second": round(
                    requests_per_second,
                    2,
                ),
                "success_rate": round(
                    success_rate,
                    2,
                ),
            }

        async def execute_one_task(
            index: int,
        ) -> dict:
            nonlocal completed
            nonlocal success
            nonlocal failed
            nonlocal total_latency_ms

            async with semaphore:
                selected_proxy_id = (
                    self.select_proxy_id(
                        proxy_ids=proxy_ids,
                        strategy=proxy_strategy,
                        index=index,
                    )
                )

                try:
                    result = await self.execute_one(
                        url=url,
                        proxy_id=selected_proxy_id,
                        mode=mode,
                        browser_settings=browser_settings,
                    )

                except asyncio.CancelledError:
                    raise

                except Exception as exc:
                    result = {
                        "success": False,
                        "status_code": None,
                        "latency_ms": 0,
                        "final_url": None,
                        "title": None,
                        "error": str(exc),
                        "execution_mode": mode,
                    }
                    

                completed += 1
                
                self.execution_repository.create(
                    target_url_id=target_url_id,
                    proxy_id=selected_proxy_id,
                    execution_mode=result.get(
                        "execution_mode",
                        mode,
                    ),
                    success=result["success"],
                    status_code=result.get("status_code"),
                    latency_ms=result.get("latency_ms", 0) or 0,
                    final_url=result.get("final_url"),
                    error=result.get("error"),
                )

                latency_ms = result.get(
                    "latency_ms",
                    0,
                ) or 0

                total_latency_ms += latency_ms

                if result["success"]:
                    success += 1
                else:
                    failed += 1

                return {
                    "type": "progress",
                    "index": index,
                    "completed": completed,
                    "total": count,
                    "success": success,
                    "failed": failed,
                    "proxy_id": (
                        str(selected_proxy_id)
                        if selected_proxy_id
                        else None
                    ),
                    "result": result,
                    "metrics": build_metrics(),
                }

        try:
            yield {
                "type": "started",
                "total": count,
                "success": 0,
                "failed": 0,
                "completed": 0,
                "metrics": build_metrics(),
            }

            tasks = {
                asyncio.create_task(
                    execute_one_task(index)
                )
                for index in range(
                    1,
                    count + 1,
                )
            }

            pending = tasks.copy()

            while pending:
                done, pending = await asyncio.wait(
                    pending,
                    return_when=asyncio.FIRST_COMPLETED,
                )

                for task in done:
                    yield task.result()

            yield {
                "type": "completed",
                "total": count,
                "success": success,
                "failed": failed,
                "completed": completed,
                "metrics": build_metrics(),
            }

        finally:
            # Cancel remaining tasks if the client
            # disconnects or aborts the SSE stream.
            for task in tasks:
                if not task.done():
                    task.cancel()

            if tasks:
                await asyncio.gather(
                    *tasks,
                    return_exceptions=True,
                )