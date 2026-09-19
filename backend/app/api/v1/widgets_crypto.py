from typing import Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.core.widget_registry import register_widget, create_base_widget_config, WidgetResponse
from app.services import coingecko_service
from app.services.cache_service import ProviderBlocked

router = APIRouter(prefix="/widgets/crypto", tags=["crypto widgets"])

VS_CURRENCY_OPTIONS = [
    {"label": "USD", "value": "usd"},
    {"label": "EUR", "value": "eur"},
    {"label": "GBP", "value": "gbp"},
    {"label": "JPY", "value": "jpy"},
    {"label": "BTC", "value": "btc"},
    {"label": "ETH", "value": "eth"},
]

COIN_OPTIONS = [
    {"label": "Bitcoin", "value": "bitcoin"},
    {"label": "Ethereum", "value": "ethereum"},
    {"label": "BNB", "value": "binancecoin"},
    {"label": "Solana", "value": "solana"},
    {"label": "XRP", "value": "ripple"},
    {"label": "Dogecoin", "value": "dogecoin"},
    {"label": "Cardano", "value": "cardano"},
    {"label": "Avalanche", "value": "avalanche-2"},
    {"label": "Polkadot", "value": "polkadot"},
    {"label": "Chainlink", "value": "chainlink"},
]

CHART_DAYS_OPTIONS = [
    {"label": "24h", "value": "1"},
    {"label": "7d", "value": "7"},
    {"label": "30d", "value": "30"},
    {"label": "90d", "value": "90"},
    {"label": "180d", "value": "180"},
    {"label": "1y", "value": "365"},
    {"label": "Max", "value": "max"},
]


def _blocked_response(e: ProviderBlocked) -> JSONResponse:
    return JSONResponse(status_code=503, content={"error": str(e)})


@router.get("/crypto-markets")
@register_widget(
    create_base_widget_config(
        name="Crypto Markets",
        description="Top cryptocurrencies by market cap with price, 24h change, volume (CoinGecko)",
        category="Crypto",
        endpoint="crypto-markets",
        widget_type="table",
        grid_w=50,
        grid_h=20,
        source="CoinGecko",
        params=[
            {
                "paramName": "per_page",
                "value": 50,
                "label": "Coins",
                "show": True,
                "type": "number",
                "description": "Number of coins to return (1-250)",
            },
            {
                "paramName": "order",
                "value": "market_cap_desc",
                "label": "Sort",
                "show": True,
                "type": "text",
                "options": [
                    {"label": "Market Cap ↓", "value": "market_cap_desc"},
                    {"label": "Market Cap ↑", "value": "market_cap_asc"},
                    {"label": "Volume ↓", "value": "volume_desc"},
                    {"label": "24h Change ↓", "value": "price_change_percentage_24h_desc"},
                ],
            },
            {
                "paramName": "vs_currency",
                "value": "usd",
                "label": "Currency",
                "show": True,
                "type": "text",
                "options": VS_CURRENCY_OPTIONS,
            },
        ],
    )
)
async def crypto_markets(
    per_page: int = Query(50, ge=1, le=250),
    order: str = Query("market_cap_desc"),
    vs_currency: str = Query("usd"),
) -> Any:
    try:
        coins = await coingecko_service.get_markets(
            vs_currency=vs_currency, per_page=per_page, order=order
        )
        rows = [
            {
                "rank": c.get("market_cap_rank"),
                "symbol": (c.get("symbol") or "").upper(),
                "name": c.get("name"),
                "price": c.get("current_price"),
                "change_pct_24h": round(c.get("price_change_percentage_24h") or 0, 2),
                "market_cap": c.get("market_cap"),
                "volume_24h": c.get("total_volume"),
                "high_24h": c.get("high_24h"),
                "low_24h": c.get("low_24h"),
            }
            for c in coins
        ]
        columns = [
            {"field": "rank", "headerName": "#"},
            {"field": "symbol", "headerName": "Symbol"},
            {"field": "name", "headerName": "Name"},
            {"field": "price", "headerName": "Price"},
            {"field": "change_pct_24h", "headerName": "24h %"},
            {"field": "market_cap", "headerName": "Market Cap"},
            {"field": "volume_24h", "headerName": "Volume 24h"},
            {"field": "high_24h", "headerName": "24h High"},
            {"field": "low_24h", "headerName": "24h Low"},
        ]
        return WidgetResponse.table(rows, columns_defs=columns)
    except ProviderBlocked as e:
        return _blocked_response(e)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Crypto markets fetch failed: {str(e)}"})


@router.get("/crypto-heatmap")
@register_widget(
    create_base_widget_config(
        name="Crypto Heatmap",
        description="Cryptocurrency market-cap heatmap colored by 24h change (CoinGecko)",
        category="Crypto",
        endpoint="crypto-heatmap",
        widget_type="heatmap",
        grid_w=50,
        grid_h=30,
        source="CoinGecko",
        params=[
            {
                "paramName": "per_page",
                "value": 50,
                "label": "Coins",
                "show": True,
                "type": "number",
                "description": "Number of coins to return (1-250)",
            },
            {
                "paramName": "sortBy",
                "value": "marketCap",
                "label": "Sort By",
                "show": True,
                "type": "text",
                "options": [
                    {"label": "Market Cap", "value": "marketCap"},
                    {"label": "% Change", "value": "pctChange"},
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
                "paramName": "vs_currency",
                "value": "usd",
                "label": "Currency",
                "show": True,
                "type": "text",
                "options": VS_CURRENCY_OPTIONS,
            },
        ],
    )
)
async def crypto_heatmap(
    per_page: int = Query(50, ge=1, le=250),
    sortBy: str = Query("marketCap"),
    sortOrder: str = Query("desc"),
    vs_currency: str = Query("usd"),
) -> Any:
    try:
        coins = await coingecko_service.get_markets(
            vs_currency=vs_currency, per_page=per_page, order="market_cap_desc"
        )
        result = []
        for c in coins:
            symbol = (c.get("symbol") or "?").upper()
            result.append({
                "symbol": symbol,
                "name": c.get("name") or symbol,
                "sector": "Crypto",
                "marketCap": float(c.get("market_cap") or 0) or 1_000_000,
                "changePercent": round(c.get("price_change_percentage_24h") or 0, 2),
                "changeAbsolute": 0,
                "price": c.get("current_price") or 0,
                "volume": int(c.get("total_volume") or 0),
            })

        reverse = sortOrder == "desc"
        sort_keys = {
            "pctChange": "changePercent",
            "marketCap": "marketCap",
            "volume": "volume",
            "symbol": "symbol",
        }
        result.sort(key=lambda x: x.get(sort_keys.get(sortBy, "marketCap"), 0), reverse=reverse)
        return {"data": result}
    except ProviderBlocked as e:
        return _blocked_response(e)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Crypto heatmap fetch failed: {str(e)}"})


@router.get("/crypto-price-chart")
@register_widget(
    create_base_widget_config(
        name="Crypto Price Chart",
        description="Historical price, market cap, and volume chart for a coin (CoinGecko market_chart)",
        category="Crypto",
        endpoint="crypto-price-chart",
        widget_type="chart",
        chart_type="scatter",
        grid_w=50,
        grid_h=20,
        source="CoinGecko",
        params=[
            {
                "paramName": "coin",
                "value": "bitcoin",
                "label": "Coin",
                "show": True,
                "type": "text",
                "options": COIN_OPTIONS,
            },
            {
                "paramName": "days",
                "value": "30",
                "label": "Range",
                "show": True,
                "type": "text",
                "options": CHART_DAYS_OPTIONS,
            },
            {
                "paramName": "vs_currency",
                "value": "usd",
                "label": "Currency",
                "show": True,
                "type": "text",
                "options": VS_CURRENCY_OPTIONS,
            },
        ],
    )
)
async def crypto_price_chart(
    coin: str = Query("bitcoin"),
    days: str = Query("30"),
    vs_currency: str = Query("usd"),
) -> Any:
    from datetime import datetime, timezone

    try:
        chart = await coingecko_service.get_market_chart(
            coin_id=coin, vs_currency=vs_currency, days=int(days) if days != "max" else 36500
        )
        prices = chart.get("prices") or []
        market_caps = chart.get("market_caps") or []
        volumes = chart.get("total_volumes") or []

        def _xy(series: list) -> tuple[list, list]:
            xs = [datetime.fromtimestamp(p[0] / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M") for p in series]
            ys = [p[1] for p in series]
            return xs, ys

        px_x, px_y = _xy(prices)
        mc_x, mc_y = _xy(market_caps) if market_caps else ([], [])
        vo_x, vo_y = _xy(volumes) if volumes else ([], [])

        traces = [
            {"type": "scatter", "mode": "lines", "x": px_x, "y": px_y, "name": f"Price ({vs_currency.upper()})", "line": {"color": "#f7931a", "width": 2}},
        ]
        if vo_x:
            traces.append({
                "type": "bar", "x": vo_x, "y": vo_y, "name": "Volume", "yaxis": "y2",
                "marker": {"color": "rgba(100,149,237,0.35)"},
            })
        if mc_x:
            traces.append({
                "type": "scatter", "mode": "lines", "x": mc_x, "y": mc_y, "name": "Market Cap", "yaxis": "y3",
                "line": {"color": "#2ecc71", "width": 1, "dash": "dot"},
            })

        layout = {
            "template": "plotly_dark",
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"color": "#e5e7eb"},
            "margin": {"l": 60, "r": 60, "t": 30, "b": 40},
            "showlegend": True,
            "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
            "yaxis": {"title": f"Price ({vs_currency.upper()})", "domain": [0, 1]},
            "yaxis2": {"visible": False, "domain": [0, 0.3]},
            "yaxis3": {"visible": False, "overlaying": "y", "side": "right"},
            "xaxis": {"gridcolor": "#1f2937"},
        }
        return {"type": "chart", "data": {"chart": {"type": "scatter", "data": traces, "layout": layout}}}
    except ProviderBlocked as e:
        return _blocked_response(e)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Crypto price chart fetch failed: {str(e)}"})


@router.get("/crypto-trending")
@register_widget(
    create_base_widget_config(
        name="Crypto Trending",
        description="Top trending coins on CoinGecko over the last 24 hours",
        category="Crypto",
        endpoint="crypto-trending",
        widget_type="table",
        grid_w=25,
        grid_h=15,
        source="CoinGecko",
    )
)
async def crypto_trending() -> Any:
    try:
        trending = await coingecko_service.get_trending()
        rows = []
        for item in trending.get("coins") or []:
            c = item.get("item") or {}
            data = c.get("data") or {}
            price_change = (data.get("price_change_percentage_24h") or {}).get("usd")
            rows.append({
                "name": c.get("name"),
                "symbol": c.get("symbol"),
                "market_cap_rank": c.get("market_cap_rank"),
                "price_btc": c.get("price_btc"),
                "change_pct_24h": round(price_change, 2) if price_change is not None else None,
            })
        columns = [
            {"field": "name", "headerName": "Name"},
            {"field": "symbol", "headerName": "Symbol"},
            {"field": "market_cap_rank", "headerName": "Rank"},
            {"field": "change_pct_24h", "headerName": "24h %"},
        ]
        return WidgetResponse.table(rows, columns_defs=columns)
    except ProviderBlocked as e:
        return _blocked_response(e)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Trending fetch failed: {str(e)}"})


@router.get("/crypto-gainers-losers")
@register_widget(
    create_base_widget_config(
        name="Crypto Gainers & Losers",
        description="Top crypto price gainers and losers by market-cap band (CoinGecko)",
        category="Crypto",
        endpoint="crypto-gainers-losers",
        widget_type="table",
        grid_w=50,
        grid_h=20,
        source="CoinGecko",
        params=[
            {
                "paramName": "duration",
                "value": "24h",
                "label": "Duration",
                "show": True,
                "type": "text",
                "options": [
                    {"label": "1h", "value": "1h"},
                    {"label": "24h", "value": "24h"},
                    {"label": "7d", "value": "7d"},
                    {"label": "30d", "value": "30d"},
                ],
            },
            {
                "paramName": "vs_currency",
                "value": "usd",
                "label": "Currency",
                "show": True,
                "type": "text",
                "options": VS_CURRENCY_OPTIONS,
            },
        ],
    )
)
async def crypto_gainers_losers(
    duration: str = Query("24h"),
    vs_currency: str = Query("usd"),
) -> Any:
    try:
        data = await coingecko_service.get_top_gainers_losers(vs_currency=vs_currency, duration=duration)
        rows = []
        for label, coins in (("gainer", data.get("top_gainers") or []), ("loser", data.get("top_losers") or [])):
            for c in coins:
                rows.append({
                    "type": label,
                    "symbol": (c.get("symbol") or "").upper(),
                    "name": c.get("name"),
                    "image": c.get("image"),
                    "usd": c.get("usd"),
                    "change": round(c.get(f"{vs_currency}_24h_change") or 0, 2),
                    "volume": c.get(f"{vs_currency}_volume"),
                    "market_cap": c.get(f"{vs_currency}_market_cap"),
                })
        columns = [
            {"field": "type", "headerName": "Type"},
            {"field": "symbol", "headerName": "Symbol"},
            {"field": "name", "headerName": "Name"},
            {"field": "usd", "headerName": "Price (USD)"},
            {"field": "change", "headerName": "Change %"},
            {"field": "market_cap", "headerName": "Market Cap"},
            {"field": "volume", "headerName": "Volume"},
        ]
        return WidgetResponse.table(rows, columns_defs=columns)
    except ProviderBlocked as e:
        return _blocked_response(e)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Gainers/losers fetch failed: {str(e)}"})
