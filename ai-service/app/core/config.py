from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    service_name: str = Field("codesage-ai-service", alias="SERVICE_NAME")
    environment: str = Field("development", alias="ENVIRONMENT")

    secret_key: str = Field(..., alias="SECRET_KEY")
    api_key_header: str = Field("X-API-Key", alias="API_KEY_HEADER")

    redis_url: str = Field("redis://localhost:6379/0", alias="REDIS_URL")
    redis_key_prefix: str = Field("codesage", alias="REDIS_KEY_PREFIX")
    redis_cache_ttl_seconds: int = Field(300, alias="REDIS_CACHE_TTL_SECONDS")
    rate_limit_requests: int = Field(60, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window_seconds: int = Field(60, alias="RATE_LIMIT_WINDOW_SECONDS")
    repo_lock_ttl_seconds: int = Field(1800, alias="REPO_LOCK_TTL_SECONDS")
    job_ttl_seconds: int = Field(86400, alias="JOB_TTL_SECONDS")

    qdrant_url: str = Field("http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: str = Field("", alias="QDRANT_API_KEY")
    qdrant_collection_prefix: str = Field("codesage", alias="QDRANT_COLLECTION_PREFIX")
    vector_db_backend: str = Field("qdrant", alias="VECTOR_DB_BACKEND")

    embedding_model: str = Field("BAAI/bge-base-en-v1.5", alias="EMBEDDING_MODEL")
    embedding_device: str = Field("cpu", alias="EMBEDDING_DEVICE")
    embedding_batch_size: int = Field(32, alias="EMBEDDING_BATCH_SIZE")

    llm_model_path: str = Field(
        "./models/mistral-7b-instruct-v0.3.Q4_K_M.gguf",
        alias="LLM_MODEL_PATH",
    )
    llm_backend: str = Field("local", alias="LLM_BACKEND")
    llm_n_ctx: int = Field(4096, alias="LLM_N_CTX")
    llm_n_gpu_layers: int = Field(0, alias="LLM_N_GPU_LAYERS")
    llm_n_threads: int = Field(8, alias="LLM_N_THREADS")
    llm_n_batch: int = Field(512, alias="LLM_N_BATCH")
    llm_temperature: float = Field(0.1, alias="LLM_TEMPERATURE")
    llm_top_p: float = Field(0.9, alias="LLM_TOP_P")
    llm_repeat_penalty: float = Field(1.1, alias="LLM_REPEAT_PENALTY")
    llm_max_new_tokens: int = Field(512, alias="LLM_MAX_NEW_TOKENS")

    max_repo_size_mb: int = Field(100, alias="MAX_REPO_SIZE_MB")
    clone_timeout_sec: int = Field(120, alias="CLONE_TIMEOUT_SEC")
    allowed_origins: str = Field("http://localhost:3000", alias="ALLOWED_ORIGINS")
    supported_extensions: list[str] = Field(
        default_factory=lambda: [".py", ".js", ".ts", ".go", ".java", ".md"],
        alias="SUPPORTED_EXTENSIONS",
    )

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()