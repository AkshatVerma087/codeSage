from functools import lru_cache
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.rag.pipeline.pipeline import RAGPipeline
from app.llm.client import LLMClient
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)

router = APIRouter()


@lru_cache(maxsize=1)
def get_pipeline() -> RAGPipeline:
    return RAGPipeline()


@lru_cache(maxsize=1)
def get_llm_client() -> LLMClient:
    return LLMClient()


class AnalyzeRequest(BaseModel):
    """Request to analyze a repository."""
    repoUrl: str
    repoId: str
    jobId: str
    githubToken: Optional[str] = None
    analysisType: Optional[str] = None
    question: Optional[str] = None
    correlationId: Optional[str] = None


class GenerateRequest(BaseModel):
    prompt: str
    systemPrompt: str = ""
    maxNewTokens: int = 256
    temperature: float = 0.2
    backend: Optional[str] = None


class GenerateResponse(BaseModel):
    success: bool
    text: str
    model: str
    backend: str


@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """
    Analyze a repository: clone -> parse -> embed -> index.
    Returns indexing statistics.
    """
    try:
        logger.info(f"Starting analysis", extra={
            "jobId": request.jobId,
            "repoId": request.repoId,
            "correlationId": request.correlationId
        })
        
        stats = get_pipeline().run_indexing(
            repo_url=request.repoUrl,
            job_id=request.jobId,
            repo_id=request.repoId,
            github_token=request.githubToken
        )
        
        return {
            "success": True,
            "stats": stats,
            "message": f"Indexed {stats['chunks_indexed']} chunks"
        }
    
    except ValueError as e:
        logger.error(f"Validation error: {e}", extra={"jobId": request.jobId})
        return {
            "success": False,
            "error": str(e),
            "errorCode": "VALIDATION_ERROR"
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}", extra={"jobId": request.jobId})
        return {
            "success": False,
            "error": str(e),
            "errorCode": "ANALYSIS_ERROR"
        }


@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    try:
        client = get_llm_client()
        backend = request.backend or settings.llm_backend
        text = client.generate(
            prompt=request.prompt,
            system_prompt=request.systemPrompt,
            max_new_tokens=request.maxNewTokens,
            temperature=request.temperature,
            backend=backend,
        )
        return GenerateResponse(
            success=True,
            text=text,
            model=settings.llm_model_path,
            backend=backend,
        )
    except Exception as exc:
        logger.error(f"Generation failed: {exc}")
        raise HTTPException(status_code=500, detail="LLM generation failed")
