from datetime import date as Date, time as Time
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PostingRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(..., min_length=1, max_length=200)

    @field_validator("message")
    @classmethod
    def validate_single_cta_link(cls, value: str) -> str:
        links = [word.rstrip(".,!?;:)") for word in value.split() if word.lower().startswith(("http://", "https://"))]
        if len(links) != 1:
            raise ValueError("message must contain exactly one CTA link")
        parsed = urlparse(links[0])
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("CTA link must be a valid HTTP or HTTPS URL")
        return value


class PostingResult(BaseModel):
    platform: str
    status: Literal["success", "failed"]
    posted_url: str | None = None
    public_access: bool = False
    date: Date | None = None
    time: Time | None = None
    error: str | None = None


class PostingResponse(BaseModel):
    success: bool
    results: list[PostingResult]
