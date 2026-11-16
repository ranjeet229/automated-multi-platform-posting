from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request

from app.config import get_settings
from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import build_platforms, publish_to_platforms


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        app.state.platforms = build_platforms(client, settings)
        yield


app = FastAPI(title="Automated Multi-Platform Posting System", lifespan=lifespan)


@app.post("/posting", response_model=PostingResponse)
async def posting(payload: PostingRequest, request: Request) -> PostingResponse:
    results = await publish_to_platforms(payload.message, request.app.state.platforms)
    return PostingResponse(success=any(result.status == "success" for result in results), results=results)
