from .base import Platform, PlatformError


class DiscordPlatform(Platform):
    name = "Discord"

    def __init__(self, client, webhook_url: str | None) -> None:
        super().__init__(client)
        self.webhook_url = webhook_url

    async def post(self, message: str) -> str:
        if not self.webhook_url:
            raise PlatformError("Discord webhook URL is not configured")
        response = await self.client.post(f"{self.webhook_url}?wait=true", json={"content": message})
        if response.is_error:
            raise PlatformError(f"Discord API returned HTTP {response.status_code}")
        data = response.json()
        channel_id, message_id = data.get("channel_id"), data.get("id")
        if not channel_id or not message_id:
            raise PlatformError("Discord API response did not include a message URL")
        return f"https://discord.com/channels/@me/{channel_id}/{message_id}"
