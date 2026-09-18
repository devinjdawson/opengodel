from datetime import datetime, timedelta
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from openbb import obb

from app.core.config import settings
from app.core.database import async_session_maker
from app.core.market_hours import is_market_open
from app.db.models import StockCandle, NewsArticle
from app.services.cache_service import run_obb
from app.services.openbb_service import openbb_service
from app.services.vector_service import vector_service


scheduler = AsyncIOScheduler()

# Hot symbols whose data we keep warm in cache during market hours so that
# interactive widget loads (heatmap, quotes) read from cache instead of
# hammering rate-limited providers on every user action.
HOT_SYMBOLS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "BRK.B", "GOOG", "TSLA", "AVGO",
    "JPM", "V", "LLY", "UNH", "XOM", "MA", "WMT", "PG", "COST", "JNJ",
    "ORCL", "HD", "ABBV", "BAC", "CRM", "NFLX", "CVX", "KO", "PEP", "TMO",
    "CSCO", "MRK", "LIN", "ABT", "ACN", "AMD", "VZ", "MCD", "DIS", "WFC",
    "AMGN", "ADBE", "INTC", "QCOM", "TXN", "MU", "AMAT", "ADI", "INTU", "PYPL",
    "ISRG", "BKNG", "MDLZ", "GILD", "REGN", "VRTX", "ASML", "LRCX", "KLAC", "SNPS",
    "CDNS", "MCHP", "NXPI", "ON", "FTNT", "PANW", "CRWD", "ZS", "OKTA", "DDOG",
    "SNOW", "PLTR", "MDB", "NET", "ESTC", "TWLO", "DOCU", "ZM", "SHOP", "SQ",
    "ROKU", "PINS", "SNAP", "UBER", "LYFT", "ABNB", "DASH", "COIN", "HOOD", "SOFI",
    "UPST", "AFRM", "NU", "MELI", "SEA", "BABA", "JD", "PDD", "TME", "BILI",
    "NIO", "XPEV", "LI", "RIVN", "LCID", "F", "GM",
]


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


async def prefetch_hot_data() -> None:
    """Warm the cache for hot symbols during market hours.

    Runs the expensive bulk provider calls (S&P 500 quotes/profiles) on a fixed
    cadence so interactive widget loads read from cache instead of each user
    action independently hitting rate-limited providers.
    """
    if not is_market_open():
        return

    symbols = ",".join(HOT_SYMBOLS)
    for provider in ["yfinance"]:
        try:
            await run_obb(
                obb.equity.price.quote,
                name="equity.price.quote",
                category="quote",
                provider=provider,
                force=True,
                symbol=symbols,
            )
            print(f"[prefetch] warmed quotes for {len(HOT_SYMBOLS)} symbols via {provider}")
        except Exception as e:
            print(f"[prefetch] quote prefetch failed ({provider}): {e}")

        try:
            await run_obb(
                obb.equity.profile,
                name="equity.profile",
                category="fundamentals",
                provider=provider,
                force=True,
                symbol=symbols,
            )
            print(f"[prefetch] warmed profiles for {len(HOT_SYMBOLS)} symbols via {provider}")
        except Exception as e:
            print(f"[prefetch] profile prefetch failed ({provider}): {e}")


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
    scheduler.add_job(
        prefetch_hot_data,
        "interval",
        minutes=2,
        id="prefetch_hot_data",
        replace_existing=True,
        next_run_time=datetime.now(),
    )
    scheduler.start()
    print("Scheduler started with jobs: sync_market_data (1h), sync_news (15m), prefetch_hot_data (2m, market hours)")


async def shutdown_scheduler() -> None:
    scheduler.shutdown()
    print("Scheduler shut down")