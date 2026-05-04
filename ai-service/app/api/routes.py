import asyncio
from typing import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()

class AnalyzeRequest(BaseModel):
    # Supports both frontend-style payloads and worker payloads.
    repoUrl: str | None = None
    repoId: str | None = None
    analysisType: str | None = None
    jobId: str | None = None
    ownerUserId: str | None = None
    question: str | None = None
    correlationId: str | None = None

async def stream_stub() -> AsyncIterator[bytes]:
    chunks = [
        "analysis started\n",
        "reading repo metadata\n",
        "building context\n",
        "generating answer\n",
        "analysis completed\n"
    ]

    for chunk in chunks:
        await asyncio.sleep(0.05)
        yield chunk.encode('utf-8')


@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    return StreamingResponse(stream_stub(), media_type="text/plain")