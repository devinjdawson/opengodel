from datetime import datetime, timedelta
from typing import Any, Optional
import asyncio
import functools
import json
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from fastapi_cache.decorator import cache

from app.core.config import settings
from app.core.widget_registry import register_widget, create_base_widget_config

router = APIRouter(prefix="/widgets/market", tags=["market widgets"])


async def _run_obb_sync(func, *args, **kwargs):
    """Run synchronous OpenBB call in thread pool."""
    loop = asyncio.get_event_loop()
    if kwargs:
        return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
    return await loop.run_in_executor(None, func, *args)


SP500_TOP = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "BRK.B", "GOOG", "TSLA", "AVGO",
    "JPM", "V", "LLY", "UNH", "XOM", "MA", "WMT", "PG", "COST", "JNJ",
    "ORCL", "HD", "ABBV", "BAC", "CRM", "NFLX", "CVX", "KO", "PEP", "TMO",
    "CSCO", "MRK", "LIN", "ABT", "ACN", "AMD", "VZ", "MCD", "DIS", "WFC",
]


@router.get("/market-heatmap")
@register_widget(
    create_base_widget_config(
        name="Market Heatmap",
        description="S&P 500 top stocks heatmap by sector and % change",
        category="Market",
        endpoint="market-heatmap",
        widget_type="heatmap",
        grid_w=50,
        grid_h=30,
        params=[
            {
                "paramName": "symbols",
                "value": "default",
                "label": "Symbol List",
                "show": True,
                "type": "text",
                "description": "Comma-separated symbols or 'default' for S&P500 top 40",
                "options": [
                    {"label": "S&P500 Top 40", "value": "default"},
                    {"label": "Mega Cap 10", "value": "mega10"},
                    {"label": "Tech Sector", "value": "tech"},
                ],
            },
            {
                "paramName": "provider",
                "value": "yfinance",
                "label": "Provider",
                "show": True,
                "type": "text",
                "options": [
                    {"label": "YFinance", "value": "yfinance"},
                    {"label": "FMP", "value": "fmp"},
                ],
            },
        ],
    )
)
async def market_heatmap(
    symbols: str = Query("default"),
    provider: str = Query("yfinance"),
) -> Any:
    """Return market heatmap data for Recharts Treemap."""
    try:
        symbol_list = SP500_TOP
        if symbols == "mega10":
            symbol_list = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "BRK.B", "GOOG", "TSLA", "AVGO"]
        elif symbols == "tech":
            symbol_list = ["AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "CRM", "CSCO", "AMD", "ACN", "ADBE", "INTC", "QCOM", "TXN", "MU", "AMAT"]
        elif symbols != "default":
            symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]

        from openbb import obb

        df = await _run_obb_sync(
            obb.equity.profile,
            symbol=",".join(symbol_list),
            provider=provider,
        )
        profile_df = df.to_df()

        prices = await _run_obb_sync(
            obb.equity.price.quote,
            symbol=",".join(symbol_list),
            provider=provider,
        )
        price_df = prices.to_df()

        result = []
        for symbol in symbol_list:
            try:
                profile_row = profile_df[profile_df["symbol"] == symbol] if "symbol" in profile_df.columns else profile_df.iloc[0:0]
                price_row = price_df[price_df["symbol"] == symbol] if "symbol" in price_df.columns else price_df.iloc[0:0]

                if profile_row.empty or price_row.empty:
                    profile_row = profile_df[profile_df.index == 0] if not profile_df.empty else None
                    price_row = price_df[price_df.index == 0] if not price_df.empty else None
                    if profile_row is None or price_row is None:
                        continue

                profile_row = profile_row if not profile_row.empty else profile_df.iloc[[0]]
                price_row = price_row if not price_row.empty else price_df.iloc[[0]]

                prof = profile_row.iloc[0] if not profile_row.empty else None
                sector_val = str(prof.get("sector") or prof.get("industry_category") or "Other") if prof is not None else "Other"
                if sector_val == "nan":
                    sector_val = "Other"
                raw_cap = prof.get("market_cap") or prof.get("marketCap") if prof is not None else None
                mktcap = float(raw_cap) if raw_cap is not None else 10000000000.0

                price_val: float | None = None
                change_pct = 0.0
                if not price_row.empty:
                    row = price_row.iloc[0]
                    price_val = row.get("last_price") or row.get("price") or row.get("lastPrice")
                    if price_val is not None:
                        price_val = round(float(price_val), 2)

                    cp = row.get("changePercent") or row.get("change_percent")
                    if cp is not None:
                        change_pct = float(cp)
                    else:
                        prev_close = row.get("prev_close") or row.get("previousClose") or row.get("previous_close")
                        if price_val and prev_close:
                            prev_close = float(prev_close)
                            if prev_close > 0:
                                change_pct = (price_val - prev_close) / prev_close * 100

                def _safe_int(v) -> int:
                    if v is None:
                        return 0
                    try:
                        import math
                        if math.isnan(float(v)):
                            return 0
                        return int(v)
                    except (TypeError, ValueError):
                        return 0

                volume_val = _safe_int(price_row.iloc[0].get("volume") if not price_row.empty else None)
                if mktcap == 10000000000.0:
                    cap_val = price_row.iloc[0].get("marketCap") if not price_row.empty else None
                    if cap_val is not None:
                        try:
                            mktcap = float(cap_val)
                        except (TypeError, ValueError):
                            pass

                raw_name = prof.get("name", symbol) if prof is not None else symbol
                name_val = str(raw_name) if str(raw_name) != "nan" else symbol

                result.append({
                    "symbol": symbol,
                    "name": name_val,
                    "sector": sector_val,
                    "marketCap": mktcap,
                    "changePercent": round(change_pct, 2),
                    "price": price_val if price_val is not None else 0,
                    "volume": volume_val,
                })
            except Exception as item_err:
                result.append({
                    "symbol": symbol,
                    "name": symbol,
                    "sector": "Other",
                    "marketCap": 100000000,
                    "changePercent": 0.0,
                    "price": 0,
                    "volume": 0,
                    "error": str(item_err),
                })

        return {"data": result, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Heatmap fetch failed: {str(e)}"})
