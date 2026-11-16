from datetime import datetime, timezone

from .base import Platform, PlatformError


class BlueskyPlatform(Platform):
    name = "Bluesky"

    def __init__(self, client, handle: str | None, app_password: str | None, pds_url: str) -> None:
        super().__init__(client)
        self.handle = handle
        self.app_password = app_password
        self.pds_url = pds_url.rstrip("/")

    async def post(self, message: str) -> str:
        if not self.handle or not self.app_password:
            raise PlatformError("Bluesky credentials are not configured")
        session_response = await self.client.post(
            f"{self.pds_url}/xrpc/com.atproto.server.createSession",
            json={"identifier": self.handle, "password": self.app_password},
        )
        if session_response.is_error:
            raise PlatformError(f"Bluesky authentication returned HTTP {session_response.status_code}")
        session = session_response.json()
        did, token = session.get("did"), session.get("accessJwt")
        if not did or not token:
            raise PlatformError("Bluesky authentication response was incomplete")
        record = {
            "$type": "app.bsky.feed.post",
            "text": message,
            "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        response = await self.client.post(
            f"{self.pds_url}/xrpc/com.atproto.repo.createRecord",
            headers={"Authorization": f"Bearer {token}"},
            json={"repo": did, "collection": "app.bsky.feed.post", "record": record},
        )
        if response.is_error:
            raise PlatformError(f"Bluesky API returned HTTP {response.status_code}")
        uri = response.json().get("uri")
        if not uri:
            raise PlatformError("Bluesky API response did not include a post URI")
        return f"https://bsky.app/profile/{self.handle}/post/{uri.rsplit('/', 1)[-1]}"
