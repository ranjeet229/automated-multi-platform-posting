from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    request_timeout_seconds: float = 15.0
    enabled_platforms: str = "mastodon,bluesky,reddit,telegram,discord"

    mastodon_base_url: str | None = None
    mastodon_access_token: str | None = None

    bluesky_handle: str | None = None
    bluesky_app_password: str | None = None
    bluesky_pds_url: str = "https://bsky.social"

    reddit_client_id: str | None = None
    reddit_client_secret: str | None = None
    reddit_username: str | None = None
    reddit_password: str | None = None
    reddit_subreddit: str | None = None

    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None

    discord_webhook_url: str | None = None

    def platform_names(self) -> list[str]:
        return [name.strip().lower() for name in self.enabled_platforms.split(",") if name.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
