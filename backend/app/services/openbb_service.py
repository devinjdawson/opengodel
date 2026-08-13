from datetime import datetime
from typing import Any

from openbb import obb
from pydantic import BaseModel


class CandleData(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class NewsData(BaseModel):
    id: str
    symbol: str
    title: str
    content: str
    source: str
    url: str
    published_at: datetime


class OpenBBService:
    def __init__(self):
        self._initialized = False

    def initialize(self, api_key: str | None = None, pat: str | None = None) -> None:
        if self._initialized:
            return

        if pat:
            obb.account.login(pat=pat)
        elif api_key:
            obb.account.login(api_key=api_key)

        self._initialized = True

    async def get_historical_prices(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
        interval: str = "1d",
        provider: str = "yfinance",
    ) -> list[CandleData]:
        params = {
            "symbol": symbol,
            "interval": interval,
            "provider": provider,
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        result = await obb.equity.price.historical(**params)
        data = result.to_df()

        candles = []
        for _, row in data.iterrows():
            candles.append(
                CandleData(
                    timestamp=row["date"],
                    open=row["open"],
                    high=row["high"],
                    low=row["low"],
                    close=row["close"],
                    volume=row["volume"],
                )
            )
        return candles

    async def get_news(
        self,
        symbols: str | None = None,
        limit: int = 50,
        provider: str = "benzinga",
    ) -> list[NewsData]:
        params = {
            "limit": limit,
            "provider": provider,
        }
        if symbols:
            params["symbols"] = symbols

        result = await obb.news.world(**params)
        data = result.to_df()

        articles = []
        for _, row in data.iterrows():
            articles.append(
                NewsData(
                    id=str(row.get("id", "")),
                    symbol=row.get("symbols", [""])[0] if row.get("symbols") else "",
                    title=row.get("title", ""),
                    content=row.get("content", row.get("summary", "")),
                    source=row.get("source", ""),
                    url=row.get("url", ""),
                    published_at=row.get("date", datetime.now()),
                )
            )
        return articles

    async def search_equity(
        self,
        query: str,
        provider: str = "yfinance",
    ) -> list[dict[str, Any]]:
        result = await obb.equity.search(query=query, provider=provider)
        return result.to_df().to_dict("records")

    async def get_equity_quote(
        self,
        symbol: str,
        provider: str = "yfinance",
    ) -> dict[str, Any] | None:
        result = await obb.equity.price.quote(symbol=symbol, provider=provider)
        data = result.to_df()
        if data.empty:
            return None
        return data.iloc[0].to_dict()

    async def get_company_profile(
        self,
        symbol: str,
        provider: str = "yfinance",
    ) -> dict[str, Any] | None:
        result = await obb.equity.profile(symbol=symbol, provider=provider)
        data = result.to_df()
        if data.empty:
            return None
        return data.iloc[0].to_dict()


openbb_service = OpenBBService()