from datetime import date, time

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.platforms.base import Platform, PlatformError
from app.services.posting_service import publish_to_platforms


class FakePlatform(Platform):
    def __init__(self, client, name: str, error: Exception | None = None) -> None:
        super().__init__(client)
        self.name = name
        self.error = error

    async def post(self, message: str) -> str:
        if self.error:
            raise self.error
        return f"https://example.test/{self.name.lower()}"


@pytest.mark.anyio
async def test_validation_requires_exactly_one_valid_url():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/posting", json={"message": "No link"})
    assert response.status_code == 422
    assert "exactly one CTA link" in response.text


@pytest.mark.anyio
async def test_posts_continue_after_one_platform_failure():
    platforms = [
        FakePlatform(None, "First", PlatformError("boom")),
        FakePlatform(None, "Second"),
    ]
    results = await publish_to_platforms("Visit https://example.com", platforms)
    assert [result.status for result in results] == ["failed", "success"]
    assert results[1].posted_url == "https://example.test/second"
    assert results[1].public_access is True
    assert isinstance(results[1].date, date)
    assert isinstance(results[1].time, time)


@pytest.mark.anyio
async def test_endpoint_returns_platform_results(monkeypatch):
    app.state.platforms = [FakePlatform(None, "Test")]
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/posting", json={"message": "Read https://example.com today"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["results"][0]["platform"] == "Test"
