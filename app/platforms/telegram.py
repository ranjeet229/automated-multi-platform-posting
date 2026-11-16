from .base import Platform, PlatformError


class TelegramPlatform(Platform):
    name = "Telegram"

    def __init__(self, client, bot_token: str | None, chat_id: str | None) -> None:
        super().__init__(client)
        self.bot_token = bot_token
        self.chat_id = chat_id

    async def post(self, message: str) -> str:
        if not self.bot_token or not self.chat_id:
            raise PlatformError("Telegram credentials are not configured")
        response = await self.client.post(
            f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
            json={"chat_id": self.chat_id, "text": message},
        )
        if response.is_error:
            raise PlatformError(f"Telegram API returned HTTP {response.status_code}")
        data = response.json().get("result", {})
        message_id = data.get("message_id")
        if not message_id:
            raise PlatformError("Telegram API response did not include a message ID")
        channel_id = str(self.chat_id)
        if channel_id.startswith("-100"):
            channel_id = channel_id[4:]
        return f"https://t.me/c/{channel_id}/{message_id}"
