from pydantic_settings import BaseSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    llm_api_key: str = Field(..., alias="LLM_API_KEY")
    embedding_model: str = Field("sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDING_MODEL")
    chroma_dir: str = Field("./chroma", alias="CHROMA_DIR")
    max_repo_size_mb: int = Field(100, alias="MAX_REPO_SIZE_MB")
    clone_timeout_sec: int = Field(120, alias="CLONE_TIMEOUT_SEC")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


    
@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()