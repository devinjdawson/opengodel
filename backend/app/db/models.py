import uuid
from datetime import datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel


class StockCandle(SQLModel, table=True):
    __tablename__ = "stock_candles"

    id: Optional[int] = Field(
        default=None,
        sa_type=BigInteger,
        primary_key=True,
    )
    symbol: str = Field(
        sa_type=String(16),
        index=True,
        description="Stock symbol (e.g., AAPL)",
    )
    timestamp: datetime = Field(
        sa_type=DateTime(timezone=True),
        index=True,
        description="Candle timestamp (UTC)",
    )
    open: float = Field(sa_type=Float, description="Open price")
    high: float = Field(sa_type=Float, description="High price")
    low: float = Field(sa_type=Float, description="Low price")
    close: float = Field(sa_type=Float, description="Close price")
    volume: float = Field(sa_type=Float, description="Volume")

    __table_args__ = (
        UniqueConstraint("symbol", "timestamp", name="uq_symbol_timestamp"),
        Index("ix_stock_candles_symbol_timestamp", "symbol", "timestamp"),
    )


class NewsArticle(SQLModel, table=True):
    __tablename__ = "news_articles"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_type=UUID(as_uuid=True),
        primary_key=True,
    )
    symbol: str = Field(
        sa_type=String(16),
        index=True,
        description="Related stock symbol",
    )
    title: str = Field(sa_type=Text, description="Article title")
    content: str = Field(sa_type=Text, description="Article content")
    source: str = Field(sa_type=String(64), description="News source")
    url: str = Field(sa_type=Text, description="Article URL")
    published_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        index=True,
        description="Publication timestamp (UTC)",
    )
    embedding: list[float] = Field(
        sa_type=Vector(1536),
        description="Vector embedding for semantic search",
    )

    __table_args__ = (
        Index(
            "ix_news_articles_embedding_cosine",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        Index("ix_news_articles_symbol_published", "symbol", "published_at"),
    )