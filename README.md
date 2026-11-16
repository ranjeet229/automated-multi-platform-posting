# Automated Multi-Platform Posting System

FastAPI service that publishes one validated message to Mastodon, Bluesky, Reddit, Telegram, and Discord. Each platform is attempted independently, so one API failure does not stop the remaining attempts.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Fill in credentials in .env for the platforms you want to enable.
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

Open `http://localhost:4000/docs` for Swagger UI.

## Request

```bash
curl -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Check out our latest platform https://example.com\"}"
```

Messages are limited to 200 characters and must contain exactly one valid HTTP(S) URL. Platform selection is configured by `ENABLED_PLATFORMS`; credentials remain in environment variables.

## Response

Each result contains the platform, success/failure status, public post URL when available, UTC posting date/time, and a safe error message when posting fails. `success` is true when at least one platform succeeds.

## API references

- [Mastodon REST API](https://docs.joinmastodon.org/methods/statuses/)
- [Bluesky API](https://docs.bsky.app/docs/api/com-atproto-repo-create-record)
- [Reddit API](https://www.reddit.com/dev/api/)
- [Telegram Bot API](https://core.telegram.org/bots/api#sendmessage)
- [Discord Webhooks](https://discord.com/developers/docs/resources/webhook)
