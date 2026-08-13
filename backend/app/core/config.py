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

    # Inference (LLM) - for chat, reasoning, tool calling
    inference_provider: str = Field(
        default="openai",
        description="Inference provider: openai, anthropic, azure, ollama, openrouter, etc.",
    )
    inference_model: str = Field(
        default="gpt-4o-mini",
        description="Inference model to use for chat/completion",
    )
    inference_api_key: Optional[str] = Field(
        default=None,
        description="API key for inference provider",
    )
    inference_base_url: Optional[str] = Field(
        default=None,
        description="Custom base URL for inference API (e.g., for Azure, Ollama, OpenRouter, local proxies)",
    )
    inference_temperature: float = Field(
        default=0.7,
        description="Temperature for inference sampling",
    )
    inference_max_tokens: int = Field(
        default=4096,
        description="Max tokens for inference response",
    )

    # Embeddings - for vector search, RAG
    embedding_provider: str = Field(
        default="openai",
        description="Embedding provider: openai, sentence-transformers, azure, ollama, cohere, voyage, etc.",
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Embedding model to use",
    )
    embedding_dimensions: int = Field(
        default=1536,
        description="Dimensions of the embedding vector",
    )
    embedding_api_key: Optional[str] = Field(
        default=None,
        description="API key for embedding provider (if different from inference)",
    )
    embedding_base_url: Optional[str] = Field(
        default=None,
        description="Custom base URL for embedding API",
    )

    # OpenAI (legacy/compat - maps to inference/embedding if not set)
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key (used as fallback for inference/embedding)",
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

    # OpenBB MCP Server
    openbb_mcp_url: str = Field(
        default="http://127.0.0.1:6901/mcp",
        description="OpenBB MCP server URL",
    )

    # OpenBB Platform API Server
    openbb_api_url: str = Field(
        default="http://127.0.0.1:6900",
        description="OpenBB Platform API server URL",
    )


settings = Settings()