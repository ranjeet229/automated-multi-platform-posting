from .base import Platform, PlatformError


class RedditPlatform(Platform):
    name = "Reddit"

    def __init__(self, client, client_id, client_secret, username, password, subreddit) -> None:
        super().__init__(client)
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.subreddit = subreddit

    async def post(self, message: str) -> str:
        values = (self.client_id, self.client_secret, self.username, self.password, self.subreddit)
        if not all(values):
            raise PlatformError("Reddit credentials or subreddit are not configured")
        token_response = await self.client.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=(self.client_id, self.client_secret),
            headers={"User-Agent": "automated-posting-system/1.0"},
            data={"grant_type": "password", "username": self.username, "password": self.password},
        )
        if token_response.is_error:
            raise PlatformError(f"Reddit authentication returned HTTP {token_response.status_code}")
        token = token_response.json().get("access_token")
        if not token:
            raise PlatformError("Reddit authentication response did not include an access token")
        response = await self.client.post(
            "https://oauth.reddit.com/api/submit",
            headers={"Authorization": f"Bearer {token}", "User-Agent": "automated-posting-system/1.0"},
            data={"sr": self.subreddit, "kind": "self", "title": message[:80], "text": message, "resubmit": "true"},
        )
        if response.is_error:
            raise PlatformError(f"Reddit API returned HTTP {response.status_code}")
        url = response.json().get("json", {}).get("data", {}).get("url")
        if not url:
            raise PlatformError("Reddit API response did not include a post URL")
        return url
