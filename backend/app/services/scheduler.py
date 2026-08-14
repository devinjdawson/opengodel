from datetime import datetime, timedelta
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import async_session_maker
from app.db.models import StockCandle, NewsArticle
from app.services.openbb_service import openbb_service
from app.services.vector_service import vector_service


scheduler = AsyncIOScheduler()


async def get_db_session() -> AsyncSession:
    async with async_session_maker() as session:
        return session


async def sync_daily_market_data() -> None:
    """Sync daily market data for tracked symbols."""
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "META", "NVDA", "TSLA", "JPM", "V", "JNJ"]

    async with async_session_maker() as db:
        for symbol in symbols:
            try:
                end_date = datetime.now().strftime("%Y-%m-%d")
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

                candles = openbb_service.get_historical_prices(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    interval="1d",
                )

                for candle in candles:
                    existing = await db.execute(
                        select(StockCandle).where(
                            StockCandle.symbol == symbol,
                            StockCandle.timestamp == candle.timestamp,
                        )
                    )
                    if not existing.scalar_one_or_none():
                        candle_obj = StockCandle(
                            symbol=symbol,
                            timestamp=candle.timestamp,
                            open=candle.open,
                            high=candle.high,
                            low=candle.low,
                            close=candle.close,
                            volume=candle.volume,
                        )
                        db.add(candle_obj)

                await db.commit()
                print(f"Synced {len(candles)} candles for {symbol}")

            except Exception as e:
                print(f"Error syncing {symbol}: {e}")
                await db.rollback()


async def sync_and_embed_news() -> None:
    """Fetch news and generate embeddings for semantic search."""
    symbols = "AAPL,GOOGL,MSFT,AMZN,META,NVDA,TSLA,JPM,V,JNJ"

    try:
        articles = openbb_service.get_news(symbols=symbols, limit=100)

        if not articles:
            return

        article_dicts = []
        for article in articles:
            if article.symbol:
                article_dicts.append({
                    "id": article.id,
                    "symbol": article.symbol,
                    "title": article.title,
                    "content": article.content,
                    "source": article.source,
                    "url": article.url,
                    "published_at": article.published_at,
                })

        if article_dicts:
            async with async_session_maker() as db:
                await vector_service.store_news_with_embedding(db, article_dicts)
                print(f"Stored and embedded {len(article_dicts)} news articles")

    except Exception as e:
        print(f"Error syncing news: {e}")


async def start_scheduler() -> None:
    """Start the background scheduler with jobs."""
    scheduler.add_job(
        sync_daily_market_data,
        "interval",
        hours=1,
        id="sync_market_data",
        replace_existing=True,
    )
    scheduler.add_job(
        sync_and_embed_news,
        "interval",
        minutes=15,
        id="sync_news",
        replace_existing=True,
    )
    scheduler.start()
    print("Scheduler started with jobs: sync_market_data (1h), sync_news (15m)")


async def shutdown_scheduler() -> None:
    scheduler.shutdown()
    print("Scheduler shut down")