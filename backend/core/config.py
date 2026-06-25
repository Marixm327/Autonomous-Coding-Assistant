from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "AI Software Engineer"
    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"

    # OpenAI
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimensions: int = 1536
    openai_chat_model: str = "gpt-4o"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_key: str | None = None
    qdrant_collection_prefix: str = "aise"

    # PostgreSQL
    postgres_dsn: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aise"

    # GitHub
    github_token: str | None = None

    # Ingestion
    max_file_size_bytes: int = 512_000  # 512 KB
    chunk_max_tokens: int = 512
    chunk_overlap_tokens: int = 64

    # RAG
    retrieval_top_k: int = 20
    rerank_top_k: int = 5
    bm25_weight: float = 0.3
    vector_weight: float = 0.7

    # Agent
    agent_max_iterations: int = 20
    agent_timeout_seconds: int = 300


@lru_cache
def get_settings() -> Settings:
    return Settings()
