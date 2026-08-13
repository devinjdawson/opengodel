from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/openbb",
        description="PostgreSQL connection URL with asyncpg driver",
    )

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching",
    )

    # OpenBB
    openbb_api_key: Optional[str] = Field(
        default=None,
        description="OpenBB API key",
    )
    openbb_pat: Optional[str] = Field(
        default=None,
        description="OpenBB Personal Access Token",
    )

    # Embeddings
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for embeddings",
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Embedding model to use",
    )
    embedding_dimensions: int = Field(
        default=1536,
        description="Dimensions of the embedding vector",
    )

    # App
    app_env: str = Field(default="development", description="Application environment")
    log_level: str = Field(default="INFO", description="Logging level")
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")

    # Frontend
    next_public_api_url: str = Field(
        default="http://127.0.0.1:8000",
        description="Frontend API URL",
    )


settings = Settings()