import time
from urllib.parse import quote

import httpx

from app.models.proxy import Proxy


async def execute_http_request(
    url: str,
    proxy: Proxy | None = None,
) -> dict:
    proxy_url = None

    if proxy:
        proxy_url = f"{proxy.protocol}://"

        if proxy.username:
            username = quote(proxy.username, safe="")
            password = quote(proxy.password or "", safe="")
            proxy_url += f"{username}:{password}@"

        proxy_url += f"{proxy.host}:{proxy.port}"

    started_at = time.perf_counter()

    try:
        async with httpx.AsyncClient(
            proxy=proxy_url,
            timeout=30.0,
            follow_redirects=True,
        ) as client:
            response = await client.get(url)

        latency_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        return {
            "success": True,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "final_url": str(response.url),
        }

    except Exception as exc:
        latency_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )

        return {
            "success": False,
            "status_code": None,
            "latency_ms": latency_ms,
            "final_url": None,
            "error": str(exc),
        }