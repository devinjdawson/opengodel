from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi_cache.decorator import cache
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.db.models import NewsArticle
from app.services.openbb_service import openbb_service
from app.services.vector_service import vector_service

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/latest")
@cache(expire=900)
async def get_latest_news(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    limit: int = Query(50, le=100, description="Number of articles to return"),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    stmt = select(NewsArticle).order_by(desc(NewsArticle.published_at)).limit(limit)
    if symbol:
        stmt = stmt.where(NewsArticle.symbol == symbol.upper())

    result = await db.execute(stmt)
    articles = result.scalars().all()

    return [
        {
            "id": str(a.id),
            "symbol": a.symbol,
            "title": a.title,
            "content": a.content,
            "source": a.source,
            "url": a.url,
            "published_at": a.published_at.isoformat(),
        }
        for a in articles
    ]


@router.get("/search")
async def search_news(
    query: str = Query(..., min_length=1, description="Search query for semantic search"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    limit: int = Query(10, le=50, description="Number of results"),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    articles = await vector_service.search_similar_news(
        db=db,
        query=query,
        limit=limit,
        symbol=symbol.upper() if symbol else None,
    )

    return [
        {
            "id": str(a.id),
            "symbol": a.symbol,
            "title": a.title,
            "content": a.content,
            "source": a.source,
            "url": a.url,
            "published_at": a.published_at.isoformat(),
        }
        for a in articles
    ]


@router.get("/symbols")
@cache(expire=3600)
async def get_news_symbols(
    db: AsyncSession = Depends(get_db),
) -> list[str]:
    result = await db.execute(
        select(NewsArticle.symbol).distinct().where(NewsArticle.symbol != "")
    )
    return sorted([r for r in result.scalars().all() if r])


@router.post("/sync")
async def sync_news() -> dict:
    from app.services.scheduler import sync_and_embed_news
    await sync_and_embed_news()
    return {"status": "success", "message": "News sync triggered"}