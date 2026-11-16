from abc import ABC, abstractmethod

import httpx


class PlatformError(Exception):
    """A user-safe error raised when a platform cannot publish."""


class Platform(ABC):
    name: str

    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client

    @abstractmethod
    async def post(self, message: str) -> str:
        """Publish message and return its public URL."""
