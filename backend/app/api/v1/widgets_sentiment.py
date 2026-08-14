"""Market sentiment widgets built on Marketaux news data."""

import asyncio
import functools
import json
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import plotly.graph_objects as go

from app.core.config import settings
from app.core.widget_registry import (
    register_widget,
    create_base_widget_config,
    WidgetResponse,
)

router = APIRouter(prefix="/widgets/sentiment", tags=["sentiment widgets"])

from openbb import obb


async def _run_obb_sync(func, *args, **kwargs):
    """Run synchronous OpenBB SDK call in thread pool."""
    loop = asyncio.get_event_loop()
    if kwargs:
        return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
    return await loop.run_in_executor(None, func, *args)


def _normalize_symbols(symbols: str) -> list[str]:
    """Normalize and deduplicate symbols."""
    if not symbols:
        return []
    return sorted(set(s.strip().upper() for s in symbols.split(",") if s.strip()))


def _published_after(days: int) -> str:
    """Return ISO date string for `days` days ago."""
    return (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")


@router.get("/summary")
@register_widget(
    create_base_widget_config(
        name="Sentiment Summary (Marketaux)",
        description="Per-symbol news sentiment from Marketaux articles (requires Marketaux API key)",
        category="Sentiment",
        endpoint="sentiment-summary",
        widget_type="table",
        grid_w=50,
        grid_h=20,
        params=[
            {
                "paramName": "symbols",
                "value": "AAPL,MSFT,AMZN,GOOGL,TSLA,NVDA,META",
                "label": "Symbols",
                "show": True,
                "type": "text",
                "description": "Comma separated list of symbols",
            },
            {
                "paramName": "days",
                "value": 7,
                "label": "Lookback (days)",
                "show": True,
                "type": "number",
                "description": "Number of days to look back",
            },
        ],
    )
)
async def sentiment_summary(
    symbols: str = Query("AAPL,MSFT,AMZN,GOOGL,TSLA,NVDA,META"),
    days: int = Query(7),
) -> Any:
    """Sentiment summary for multiple symbols. Costs 1 Marketaux request per symbol."""
    try:
        symbol_list = _normalize_symbols(symbols)
        if not symbol_list:
            return JSONResponse(
                content={"error": "At least one symbol is required"},
                status_code=400,
            )

        all_rows = []
        for symbol in symbol_list:
            try:
                result = await _run_obb_sync(
                    obb.marketaux.sentiment,
                    provider="marketaux",
                    symbol=symbol,
                    start_date=_published_after(days),
                )
                df = result.to_df()
                if not df.empty:
                    for _, row in df.iterrows():
                        all_rows.append(row.to_dict())
            except Exception as e:
                if "endpoint_access_restricted" in str(e).lower() or "402" in str(e):
                    return JSONResponse(
                        content={"error": "This endpoint requires a Marketaux Standard plan or above. Please upgrade your plan."},
                        status_code=403,
                    )

        if not all_rows:
            return JSONResponse(
                content={"error": "No sentiment data found"},
                status_code=404,
            )

        return WidgetResponse.table(
            all_rows,
            columns_defs=[
                {"field": "symbol", "headerName": "Symbol", "cellDataType": "text"},
                {"field": "sentiment", "headerName": "Sentiment", "cellDataType": "number", "renderFn": "greenRed"},
                {"field": "articles", "headerName": "Articles", "cellDataType": "number"},
                {"field": "positive", "headerName": "Positive", "cellDataType": "number"},
                {"field": "negative", "headerName": "Negative", "cellDataType": "number"},
                {"field": "neutral", "headerName": "Neutral", "cellDataType": "number"},
                {"field": "top_headline", "headerName": "Top Headline", "cellDataType": "text", "flex": 2},
                {"field": "top_headline_date", "headerName": "Date", "cellDataType": "text"},
            ],
        )
    except Exception as e:
        error_msg = str(e)
        if "endpoint_access_restricted" in error_msg.lower() or "402" in error_msg:
            return JSONResponse(
                content={"error": "This endpoint requires a Marketaux Standard plan or above. Please upgrade your plan."},
                status_code=403,
            )
        return JSONResponse(content={"error": error_msg}, status_code=500)


@router.get("/breakdown")
@register_widget(
    create_base_widget_config(
        name="Sentiment Breakdown (Marketaux)",
        description="Article counts per sentiment bucket with Bayesian adjusted score",
        category="Sentiment",
        endpoint="sentiment-breakdown",
        widget_type="chart",
        chart_type="bar",
        grid_w=40,
        grid_h=20,
        params=[
            {
                "paramName": "symbols",
                "value": "AAPL,MSFT,AMZN",
                "label": "Symbols",
                "show": True,
                "type": "text",
                "description": "Comma separated list of symbols (empty = market-wide)",
            },
            {
                "paramName": "days",
                "value": 7,
                "label": "Lookback (days)",
                "show": True,
                "type": "number",
                "description": "Number of days to look back",
            },
        ],
    )
)
async def sentiment_breakdown(
    symbols: str = Query("AAPL,MSFT,AMZN"),
    days: int = Query(7),
) -> Any:
    """Sentiment breakdown chart. Costs 6 Marketaux requests per call."""
    try:
        symbol_list = _normalize_symbols(symbols)

        all_rows = []
        if symbol_list:
            for symbol in symbol_list:
                try:
                    result = await _run_obb_sync(
                        obb.marketaux.sentiment_breakdown,
                        provider="marketaux",
                        symbol=symbol,
                        start_date=_published_after(days),
                    )
                    df = result.to_df()
                    if not df.empty:
                        for _, row in df.iterrows():
                            all_rows.append(row.to_dict())
                except Exception as e:
                    if "endpoint_access_restricted" in str(e).lower() or "402" in str(e):
                        return JSONResponse(
                            content={"error": "This endpoint requires a Marketaux Standard plan or above."},
                            status_code=403,
                        )
        else:
            result = await _run_obb_sync(
                obb.marketaux.sentiment_breakdown,
                provider="marketaux",
                symbol="",
                start_date=_published_after(days),
            )
            df = result.to_df()
            if not df.empty:
                for _, row in df.iterrows():
                    all_rows.append(row.to_dict())

        if not all_rows:
            return JSONResponse(
                content={"error": "No sentiment breakdown data found"},
                status_code=404,
            )

        # Aggregate across all symbol calls
        aggregated = {
            "weak_positive": 0, "moderate_positive": 0, "strong_positive": 0,
            "weak_negative": 0, "moderate_negative": 0, "strong_negative": 0,
        }
        for row in all_rows:
            for k in aggregated:
                aggregated[k] += row.get(k, 0) or 0

        buckets = [
            "strong_positive", "moderate_positive", "weak_positive",
            "weak_negative", "moderate_negative", "strong_negative",
        ]
        colors = ["#059669", "#34d399", "#6ee7b7", "#fca5a5", "#f87171", "#dc2626"]
        values = [aggregated.get(b, 0) for b in buckets]
        total = sum(values)
        pos = sum(values[:3])
        neg = sum(values[3:])
        score = (pos - neg) / max(total, 1)

        label = "Bullish" if score > 0.15 else "Bearish" if score < -0.15 else "Neutral"

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=[b.replace("_", " ").title() for b in buckets],
                y=values,
                marker_color=colors,
                text=values,
                textposition="outside",
                hovertemplate="%{x}: %{y} articles<extra></extra>",
            )
        )

        fig.update_layout(
            title=f"Adjusted Sentiment Score: {score:+.3f} ({label})",
            xaxis_title="Sentiment",
            yaxis_title="Articles",
            showlegend=False,
        )

        return WidgetResponse.chart(chart_type="bar", data=json.loads(fig.to_json()))
    except Exception as e:
        error_msg = str(e)
        if "endpoint_access_restricted" in error_msg.lower() or "402" in error_msg:
            return JSONResponse(
                content={"error": "This endpoint requires a Marketaux Standard plan or above. Please upgrade your plan."},
                status_code=403,
            )
        return JSONResponse(content={"error": error_msg}, status_code=500)


@router.get("/history")
@register_widget(
    create_base_widget_config(
        name="Sentiment History (Marketaux)",
        description="Time series of average entity sentiment (requires Standard plan+)",
        category="Sentiment",
        endpoint="sentiment-history",
        widget_type="chart",
        chart_type="line",
        grid_w=50,
        grid_h=25,
        params=[
            {
                "paramName": "symbols",
                "value": "AAPL,MSFT,AMZN",
                "label": "Symbols",
                "show": True,
                "type": "text",
                "description": "Comma separated list of symbols",
            },
            {
                "paramName": "interval",
                "value": "day",
                "label": "Interval",
                "show": True,
                "type": "text",
                "description": "Time series interval",
            },
            {
                "paramName": "days",
                "value": 30,
                "label": "Lookback (days)",
                "show": True,
                "type": "number",
                "description": "Number of days to look back",
            },
        ],
    )
)
async def sentiment_history(
    symbols: str = Query("AAPL,MSFT,AMZN"),
    interval: str = Query("day"),
    days: int = Query(30),
) -> Any:
    """Sentiment time series chart. Requires Marketaux Standard plan or above."""
    try:
        symbol_list = _normalize_symbols(symbols)
        if not symbol_list:
            return JSONResponse(
                content={"error": "At least one symbol is required"},
                status_code=400,
            )

        all_rows = []
        for symbol in symbol_list:
            try:
                result = await _run_obb_sync(
                    obb.marketaux.sentiment_history,
                    provider="marketaux",
                    symbol=symbol,
                    interval=interval,
                    start_date=_published_after(days),
                )
                df = result.to_df()
                if not df.empty:
                    if "symbol" not in df.columns:
                        df["symbol"] = symbol
                    for _, row in df.iterrows():
                        all_rows.append(row.to_dict())
            except Exception as e:
                if "endpoint_access_restricted" in str(e).lower() or "402" in str(e):
                    return JSONResponse(
                        content={"error": "This endpoint requires a Marketaux Standard plan or above."},
                        status_code=403,
                    )

        if not all_rows:
            return JSONResponse(
                content={"error": "No sentiment history data found"},
                status_code=404,
            )

        import pandas as pd
        df = pd.DataFrame(all_rows)

        fig = go.Figure()

        grouped = df.groupby("symbol") if "symbol" in df.columns else [(symbols, df)]
        for symbol, group in grouped:
            fig.add_trace(
                go.Scatter(
                    x=group["date"] if "date" in group.columns else group.index,
                    y=group["sentiment"] if "sentiment" in group.columns else group.iloc[:, 0],
                    mode="lines+markers",
                    name=symbol,
                    hovertemplate=f"{symbol}<br>%{{x}}<br>Sentiment: %{{y:.3f}}<extra></extra>",
                )
            )

        fig.update_layout(
            title="Sentiment Over Time",
            xaxis_title="Date",
            yaxis_title="Sentiment",
            yaxis=dict(range=[-1, 1]),
            showlegend=True,
        )

        return WidgetResponse.chart(chart_type="line", data=json.loads(fig.to_json()))
    except Exception as e:
        error_msg = str(e)
        if "endpoint_access_restricted" in error_msg.lower() or "402" in error_msg:
            return JSONResponse(
                content={"error": "This endpoint requires a Marketaux Standard plan or above. Please upgrade your plan."},
                status_code=403,
            )
        return JSONResponse(content={"error": error_msg}, status_code=500)


@router.get("/trending")
@register_widget(
    create_base_widget_config(
        name="Trending Entities (Marketaux)",
        description="Entities trending in the news right now (requires Standard plan+)",
        category="Sentiment",
        endpoint="sentiment-trending",
        widget_type="table",
        grid_w=40,
        grid_h=25,
        params=[
            {
                "paramName": "countries",
                "value": "us",
                "label": "Countries",
                "show": True,
                "type": "text",
                "description": "Comma separated exchange countries (e.g., us,ca)",
            },
            {
                "paramName": "days",
                "value": 1,
                "label": "Lookback (days)",
                "show": True,
                "type": "number",
                "description": "Number of days to look back",
            },
            {
                "paramName": "limit",
                "value": 20,
                "label": "Limit",
                "show": True,
                "type": "number",
                "description": "Number of trending entities to return",
            },
        ],
    )
)
async def trending_entities(
    countries: str = Query("us"),
    days: int = Query(1),
    limit: int = Query(20),
) -> Any:
    """Trending entities from Marketaux. Requires Marketaux Standard plan or above."""
    try:
        result = await _run_obb_sync(obb.marketaux.trending, provider="marketaux", countries=countries, limit=limit, start_date=_published_after(days))
        df = result.to_df()

        if df.empty:
            return JSONResponse(
                content={"error": "No trending entities found"},
                status_code=404,
            )

        rows = df.to_dict("records")
        return WidgetResponse.table(
            rows,
            columns_defs=[
                {"field": "symbol", "headerName": "Symbol", "cellDataType": "text"},
                {"field": "name", "headerName": "Name", "cellDataType": "text", "flex": 2},
                {"field": "articles", "headerName": "Articles", "cellDataType": "number"},
                {"field": "sentiment", "headerName": "Sentiment", "cellDataType": "number", "renderFn": "greenRed"},
                {"field": "score", "headerName": "Trend Score", "cellDataType": "number"},
            ],
        )
    except Exception as e:
        error_msg = str(e)
        if "endpoint_access_restricted" in error_msg.lower() or "402" in error_msg:
            return JSONResponse(
                content={"error": "This endpoint requires a Marketaux Standard plan or above. Please upgrade your plan."},
                status_code=403,
            )
        return JSONResponse(content={"error": error_msg}, status_code=500)


@router.get("/news-market")
@register_widget(
    create_base_widget_config(
        name="Market News (Marketaux)",
        description="Latest market news with sentiment from Marketaux",
        category="News",
        endpoint="marketaux-news-market",
        widget_type="table",
        grid_w=60,
        grid_h=25,
        params=[
            {
                "paramName": "search",
                "value": "",
                "label": "Search",
                "show": True,
                "type": "text",
                "description": "Optional search term",
            },
            {
                "paramName": "sentiment",
                "value": "",
                "label": "Sentiment",
                "show": True,
                "type": "text",
                "description": "Filter by sentiment (positive/negative/neutral)",
            },
            {
                "paramName": "limit",
                "value": 20,
                "label": "Limit",
                "show": True,
                "type": "number",
                "description": "Number of articles to return",
            },
        ],
    )
)
async def marketaux_news_market(
    search: str = Query(""),
    sentiment: str = Query(""),
    limit: int = Query(20),
) -> Any:
    """Market-wide news from Marketaux."""
    try:
        kwargs = {"provider": "marketaux", "limit": limit}
        if search:
            kwargs["search"] = search
        if sentiment:
            kwargs["sentiment"] = sentiment

        result = await _run_obb_sync(obb.news.world, **kwargs)
        df = result.to_df()

        if df.empty:
            return JSONResponse(
                content={"error": "No news articles found"},
                status_code=404,
            )

        rows = df.to_dict("records")
        return WidgetResponse.table(
            rows,
            columns_defs=[
                {"field": "title", "headerName": "Title", "cellDataType": "text", "flex": 3},
                {"field": "source", "headerName": "Source", "cellDataType": "text"},
                {"field": "sentiment", "headerName": "Sentiment", "cellDataType": "number", "renderFn": "greenRed"},
                {"field": "date", "headerName": "Date", "cellDataType": "text"},
            ],
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/news-company")
@register_widget(
    create_base_widget_config(
        name="Company News (Marketaux)",
        description="Company-specific news with sentiment from Marketaux",
        category="News",
        endpoint="marketaux-news-company",
        widget_type="table",
        grid_w=60,
        grid_h=25,
        params=[
            {
                "paramName": "symbol",
                "value": "AAPL",
                "label": "Symbol",
                "show": True,
                "type": "text",
                "description": "Company ticker symbol",
            },
            {
                "paramName": "days",
                "value": 7,
                "label": "Lookback (days)",
                "show": True,
                "type": "number",
                "description": "Number of days to look back",
            },
            {
                "paramName": "limit",
                "value": 20,
                "label": "Limit",
                "show": True,
                "type": "number",
                "description": "Number of articles to return",
            },
        ],
    )
)
async def marketaux_news_company(
    symbol: str = Query("AAPL"),
    days: int = Query(7),
    limit: int = Query(20),
) -> Any:
    """Company-specific news from Marketaux."""
    try:
        result = await _run_obb_sync(obb.news.company, provider="marketaux", symbol=symbol.upper(), limit=limit, start_date=_published_after(days))
        df = result.to_df()

        if df.empty:
            return JSONResponse(
                content={"error": f"No news articles found for {symbol}"},
                status_code=404,
            )

        rows = df.to_dict("records")
        return WidgetResponse.table(
            rows,
            columns_defs=[
                {"field": "title", "headerName": "Title", "cellDataType": "text", "flex": 3},
                {"field": "source", "headerName": "Source", "cellDataType": "text"},
                {"field": "sentiment", "headerName": "Sentiment", "cellDataType": "number", "renderFn": "greenRed"},
                {"field": "date", "headerName": "Date", "cellDataType": "text"},
            ],
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
