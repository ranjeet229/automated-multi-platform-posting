from urllib.parse import urljoin

from .base import Platform, PlatformError


class MastodonPlatform(Platform):
    name = "Mastodon"

    def __init__(self, client, base_url: str | None, access_token: str | None) -> None:
        super().__init__(client)
        self.base_url = base_url.rstrip("/") + "/" if base_url else None
        self.access_token = access_token

    async def post(self, message: str) -> str:
        if not self.base_url or not self.access_token:
            raise PlatformError("Mastodon credentials are not configured")
        response = await self.client.post(
            urljoin(self.base_url, "api/v1/statuses"),
            headers={"Authorization": f"Bearer {self.access_token}"},
            data={"status": message},
        )
        if response.is_error:
            raise PlatformError(f"Mastodon API returned HTTP {response.status_code}")
        data = response.json()
        url = data.get("url")
        if not url:
            raise PlatformError("Mastodon API response did not include a post URL")
        return url
