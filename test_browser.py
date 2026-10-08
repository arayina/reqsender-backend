import asyncio

from app.core.database import SessionLocal
from app.repositories.proxy_repository import ProxyRepository
from app.executors.browser_executer import execute_browser_request


async def main():
    db = SessionLocal()

    try:
        repository = ProxyRepository(db)

        proxies = repository.get_all()

        for proxy in proxies:
            print(
                f"{proxy.host}:{proxy.port} "
                f"[{proxy.protocol}]"
            )

        proxy = next(
            (
                proxy
                for proxy in proxies
                if proxy.host == "37.202.244.195"
                and proxy.port == 1080
            ),
            None,
        )

        if proxy is None:
            print("VPS proxy not found.")
            return

        print("\nTesting VPS proxy:")
        print(f"Host: {proxy.host}")
        print(f"Port: {proxy.port}")
        print(f"Protocol: {proxy.protocol}")

        result = await execute_browser_request(
            "https://httpbin.org/ip",
            proxy=proxy,
        )

        print(result)

    finally:
        db.close()


asyncio.run(main())