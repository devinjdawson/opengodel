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

SP500_FULL = SP500_TOP + [
    "AMGN", "ADBE", "INTC", "QCOM", "TXN", "MU", "AMAT", "ADI", "INTU", "PYPL",
    "ISRG", "BKNG", "MDLZ", "GILD", "REGN", "VRTX", "ASML", "LRCX", "KLAC", "SNPS",
    "CDNS", "MCHP", "NXPI", "ON", "FTNT", "PANW", "CRWD", "ZS", "OKTA", "DDOG",
    "SNOW", "PLTR", "MDB", "NET", "ESTC", "TWLO", "DOCU", "ZM", "SHOP", "SQ",
    "ROKU", "PINS", "SNAP", "UBER", "LYFT", "ABNB", "DASH", "COIN", "HOOD", "SOFI",
    "UPST", "AFRM", "NU", "MELI", "SEA", "BABA", "JD", "PDD", "TME", "BILI",
    "NIO", "XPEV", "LI", "RIVN", "LCID", "F", "GM", "TSLA", "NVDA", "AMD",
]

MOST_ACTIVE = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "NFLX", "AMD", "INTC",
    "PLTR", "SOFI", "NIO", "RIVN", "LCID", "MULN", "BBBY", "GME", "AMC", "SPY",
    "QQQ", "IWM", "DIA", "VTI", "VOO", "IVV", "SPLG", "SCHB", "ITOT", "SCHX",
]

INDICES = [
    "SPY", "QQQ", "DIA", "IWM", "VTI", "VOO", "IVV", "SPLG", "SCHB", "ITOT",
    "XLF", "XLK", "XLE", "XLV", "XLI", "XLP", "XLY", "XLU", "XLB", "XLRE",
    "XLRE", "XLC", "SMH", "SOXX", "ARKK", "ARKQ", "ARKW", "ARKG", "ARKF",
]

SECTORS = [
    "Technology", "Financial Services", "Healthcare", "Consumer Cyclical",
    "Communication Services", "Consumer Defensive", "Energy", "Industrials",
    "Basic Materials", "Real Estate", "Utilities", "Other"
]


@router.get("/market-heatmap")
@register_widget(
    create_base_widget_config(
        name="Market Heatmap",
        description="Market heatmap by sector with configurable symbol lists, sorting, and filtering",
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
                "description": "Symbol list preset or comma-separated symbols",
                "options": [
                    {"label": "S&P500 Top 40", "value": "default"},
                    {"label": "S&P500 Full", "value": "sp500"},
                    {"label": "Mega Cap 10", "value": "mega10"},
                    {"label": "Tech Sector", "value": "tech"},
                    {"label": "Most Active", "value": "active"},
                    {"label": "Indices/ETFs", "value": "indices"},
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
            {
                "paramName": "sortBy",
                "value": "pctChange",
                "label": "Sort By",
                "show": True,
                "type": "text",
                "options": [
                    {"label": "% Change", "value": "pctChange"},
                    {"label": "Absolute Change ($)", "value": "absChange"},
                    {"label": "Market Cap", "value": "marketCap"},
                    {"label": "Volume", "value": "volume"},
                    {"label": "Symbol", "value": "symbol"},
                ],
            },
            {
                "paramName": "sortOrder",
                "value": "desc",
                "label": "Sort Order",
                "show": True,
                "type": "text",
                "options": [
                    {"label": "Descending", "value": "desc"},
                    {"label": "Ascending", "value": "asc"},
                ],
            },
            {
                "paramName": "sectors",
                "value": "",
                "label": "Sectors (comma-separated, empty=all)",
                "show": True,
                "type": "text",
                "description": "Filter sectors: Technology,Financial Services,Healthcare,etc.",
            },
        ],
    )
)
async def market_heatmap(
    symbols: str = Query("default"),
    provider: str = Query("yfinance"),
    sortBy: str = Query("pctChange"),
    sortOrder: str = Query("desc"),
    sectors: str = Query(""),
) -> Any:
    """Return market heatmap data for Recharts Treemap."""
    print(f"=== market_heatmap called with symbols={symbols}, provider={provider}, sortBy={sortBy} ===")
    try:
        # Determine symbol list
        symbol_list = SP500_TOP
        if symbols == "mega10":
            symbol_list = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "BRK.B", "GOOG", "TSLA", "AVGO"]
        elif symbols == "tech":
            symbol_list = ["AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "CRM", "CSCO", "AMD", "ACN", "ADBE", "INTC", "QCOM", "TXN", "MU", "AMAT"]
        elif symbols == "sp500":
            symbol_list = SP500_FULL
        elif symbols == "active":
            symbol_list = MOST_ACTIVE
        elif symbols == "indices":
            symbol_list = INDICES
        elif symbols != "default":
            symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]

        # Parse sector filter
        sector_filter = set()
        if sectors:
            sector_filter = set(s.strip() for s in sectors.split(",") if s.strip())

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

                # Apply sector filter
                if sector_filter and sector_val not in sector_filter:
                    continue

                raw_cap = prof.get("market_cap") or prof.get("marketCap") if prof is not None else None
                mktcap = float(raw_cap) if raw_cap is not None else 10000000000.0

                price_val: float | None = None
                change_pct = 0.0
                change_abs = 0.0
                prev_close_val: float | None = None
                if not price_row.empty:
                    row = price_row.iloc[0]
                    price_val = row.get("last_price") or row.get("price") or row.get("lastPrice")
                    if price_val is not None:
                        price_val = round(float(price_val), 2)

                    # Get prev_close for absolute change calculation
                    prev_close = row.get("prev_close") or row.get("previousClose") or row.get("previous_close")
                    if prev_close is not None:
                        prev_close_val = float(prev_close)

                    cp = row.get("changePercent") or row.get("change_percent")
                    if cp is not None:
                        change_pct = float(cp)
                    elif price_val and prev_close_val:
                        if prev_close_val > 0:
                            change_pct = (price_val - prev_close_val) / prev_close_val * 100

                    # Calculate absolute change if we have both price and prev_close
                    if price_val is not None and prev_close_val is not None and prev_close_val > 0:
                        change_abs = price_val - prev_close_val
                    else:
                        # Fallback: try to get direct change field
                        ca = row.get("change") or row.get("change_abs")
                        if ca is not None:
                            change_abs = float(ca)

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
                    "changeAbsolute": round(change_abs, 2),
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
                    "changeAbsolute": 0.0,
                    "price": 0,
                    "volume": 0,
                    "error": str(item_err),
                })

        # Sort results
        reverse = sortOrder == "desc"
        if sortBy == "pctChange":
            result.sort(key=lambda x: x.get("changePercent", 0), reverse=reverse)
        elif sortBy == "absChange":
            result.sort(key=lambda x: x.get("changeAbsolute", 0), reverse=reverse)
        elif sortBy == "marketCap":
            result.sort(key=lambda x: x.get("marketCap", 0), reverse=reverse)
        elif sortBy == "volume":
            result.sort(key=lambda x: x.get("volume", 0), reverse=reverse)
        elif sortBy == "symbol":
            result.sort(key=lambda x: x.get("symbol", ""), reverse=reverse)

        return {"data": result, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Heatmap fetch failed: {str(e)}"})
