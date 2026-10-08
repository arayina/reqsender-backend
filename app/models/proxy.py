from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass
class Proxy:
    id: UUID
    host: str
    port: int
    protocol: str
    username: str | None = None
    password: str | None = None
    enabled: bool = True

    @classmethod
    def create(
        cls,
        host: str,
        port: int,
        protocol: str,
        username: str | None = None,
        password: str | None = None,
        enabled: bool = True,
    ) -> "Proxy":
        return cls(
            id=uuid4(),
            host=host,
            port=port,
            protocol=protocol,
            username=username,
            password=password,
            enabled=enabled,
        )