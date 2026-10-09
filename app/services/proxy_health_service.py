import time
from urllib.parse import quote

import httpx

from app.models.proxy import Proxy


HEALTH_CHECK_URL = "https://www.google.com/generate_204"


class ProxyHealthService:
    async def check(self, proxy: Proxy) -> dict:
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
                timeout=10.0,
                follow_redirects=True,
            ) as client:
                response = await client.get(HEALTH_CHECK_URL)

            latency_ms = round(
                (time.perf_counter() - started_at) * 1000,
                2,
            )

            return {
                "healthy": response.is_success,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "error": None,
            }

        except Exception as exc:
            latency_ms = round(
                (time.perf_counter() - started_at) * 1000,
                2,
            )

            return {
                "healthy": False,
                "status_code": None,
                "latency_ms": latency_ms,
                "error": str(exc),
            }