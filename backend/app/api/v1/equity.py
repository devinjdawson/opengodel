from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi_cache.decorator import cache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.db.models import StockCandle
from app.services.openbb_service import openbb_service

router = APIRouter(prefix="/equity", tags=["equity"])


@router.get("/search")
async def search_equity(
    query: str = Query(..., min_length=1, description="Search query for equity"),
    provider: str = Query("yfinance", description="Data provider"),
) -> list[dict]:
    return await openbb_service.search_equity(query=query, provider=provider)


@router.get("/quote/{symbol}")
async def get_quote(
    symbol: str,
    provider: str = Query("yfinance", description="Data provider"),
) -> dict | None:
    return await openbb_service.get_equity_quote(symbol=symbol, provider=provider)


@router.get("/profile/{symbol}")
async def get_profile(
    symbol: str,
    provider: str = Query("yfinance", description="Data provider"),
) -> dict | None:
    return await openbb_service.get_company_profile(symbol=symbol, provider=provider)


@router.get("/historical/{symbol}")
@cache(expire=3600)
async def get_historical(
    symbol: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    interval: str = Query("1d", description="Interval (1d, 1h, 5m, etc.)"),
    provider: str = Query("yfinance", description="Data provider"),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    if not start_date:
        start_date = (datetime.now().replace(day=1) - timedelta(days=365)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    stmt = (
        select(StockCandle)
        .where(
            StockCandle.symbol == symbol.upper(),
            StockCandle.timestamp >= start_date,
            StockCandle.timestamp <= end_date,
        )
        .order_by(StockCandle.timestamp)
    )
    result = await db.execute(stmt)
    candles = result.scalars().all()

    if candles:
        return [
            {
                "timestamp": c.timestamp.isoformat(),
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume,
            }
            for c in candles
        ]

    obb_candles = await openbb_service.get_historical_prices(
        symbol=symbol.upper(),
        start_date=start_date,
        end_date=end_date,
        interval=interval,
        provider=provider,
    )
    return [
        {
            "timestamp": c.timestamp.isoformat(),
            "open": c.open,
            "high": c.high,
            "low": c.low,
            "close": c.close,
            "volume": c.volume,
        }
        for c in obb_candles
    ]


