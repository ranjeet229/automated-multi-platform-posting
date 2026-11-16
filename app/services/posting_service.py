from datetime import datetime, timezone

import httpx

from app.config import Settings
from app.platforms.base import Platform, PlatformError
from app.platforms.bluesky import BlueskyPlatform
from app.platforms.discord import DiscordPlatform
from app.platforms.mastodon import MastodonPlatform
from app.platforms.reddit import RedditPlatform
from app.platforms.telegram import TelegramPlatform
from app.schemas import PostingResult


def build_platforms(client: httpx.AsyncClient, settings: Settings) -> list[Platform]:
    available: dict[str, Platform] = {
        "mastodon": MastodonPlatform(client, settings.mastodon_base_url, settings.mastodon_access_token),
        "bluesky": BlueskyPlatform(client, settings.bluesky_handle, settings.bluesky_app_password, settings.bluesky_pds_url),
        "reddit": RedditPlatform(
            client,
            settings.reddit_client_id,
            settings.reddit_client_secret,
            settings.reddit_username,
            settings.reddit_password,
            settings.reddit_subreddit,
        ),
        "telegram": TelegramPlatform(client, settings.telegram_bot_token, settings.telegram_chat_id),
        "discord": DiscordPlatform(client, settings.discord_webhook_url),
    }
    return [available[name] for name in settings.platform_names() if name in available]


async def publish_to_platforms(message: str, platforms: list[Platform]) -> list[PostingResult]:
    results: list[PostingResult] = []
    for platform in platforms:
        posted_at = datetime.now(timezone.utc)
        try:
            url = await platform.post(message)
            results.append(
                PostingResult(
                    platform=platform.name,
                    status="success",
                    posted_url=url,
                    public_access=True,
                    date=posted_at.date(),
                    time=posted_at.time().replace(microsecond=0),
                )
            )
        except (PlatformError, httpx.HTTPError) as exc:
            results.append(PostingResult(platform=platform.name, status="failed", error=str(exc)))
    return results
