from datetime import datetime, timedelta
from typing import Any, Optional
from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.config import settings
from app.core.database import get_db
from app.core.widget_registry import register_widget, create_base_widget_config, WidgetResponse
from app.db.models import NewsArticle
from app.services.vector_service import vector_service

router = APIRouter(prefix="/widgets/news", tags=["news widgets"])


@router.get("/latest-articles")
@register_widget(
    create_base_widget_config(
        name="Latest News",
        description="Latest financial news articles",
        category="News",
        endpoint="latest-articles",
        widget_type="table",
        grid_w=40,
        grid_h=20,
        params=[
            {
                "paramName": "symbol",
                "value": "",
                "label": "Symbol Filter",
                "show": True,
                "description": "Filter by stock symbol (empty for all)",
                "type": "text",
            },
            {
                "paramName": "limit",
                "value": 20,
                "label": "Limit",
                "show": True,
                "description": "Number of articles to show",
                "type": "number",
            },
        ],
    )
)
async def get_latest_news_widget(
    symbol: str = Query("", description="Filter by symbol"),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get latest news articles as table."""
    stmt = select(NewsArticle).order_by(desc(NewsArticle.published_at)).limit(limit)
    if symbol:
        stmt = stmt.where(NewsArticle.symbol == symbol.upper())
    
    result = await db.execute(stmt)
    articles = result.scalars().all()
    
    rows = []
    for a in articles:
        rows.append({
            "title": a.title[:100] + "..." if len(a.title) > 100 else a.title,
            "symbol": a.symbol,
            "source": a.source,
            "published_at": a.published_at.strftime("%Y-%m-%d %H:%M"),
            "url": a.url,
        })
    
    return WidgetResponse.table(rows, columns_defs=[
        {"field": "title", "headerName": "Title", "cellDataType": "text", "flex": 2},
        {"field": "symbol", "headerName": "Symbol", "cellDataType": "text"},
        {"field": "source", "headerName": "Source", "cellDataType": "text"},
        {"field": "published_at", "headerName": "Published", "cellDataType": "text"},
        {"field": "url", "headerName": "Link", "cellDataType": "text", "renderFn": "link"},
    ])


@router.get("/semantic-search")
@register_widget(
    create_base_widget_config(
        name="Semantic News Search",
        description="AI-powered semantic search for financial news",
        category="News",
        endpoint="semantic-search",
        widget_type="table",
        grid_w=50,
        grid_h=25,
        params=[
            {
                "paramName": "query",
                "value": "earnings beat",
                "label": "Search Query",
                "show": True,
                "description": "Natural language search query",
                "type": "text",
            },
            {
                "paramName": "symbol",
                "value": "",
                "label": "Symbol Filter",
                "show": True,
                "description": "Filter by stock symbol",
                "type": "text",
            },
            {
                "paramName": "limit",
                "value": 10,
                "label": "Limit",
                "show": True,
                "description": "Number of results",
                "type": "number",
            },
        ],
    )
)
async def semantic_news_search(
    query: str = Query("earnings beat"),
    symbol: str = Query(""),
    limit: int = Query(10, le=50),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Semantic search for news articles."""
    articles = await vector_service.search_similar_news(
        db=db,
        query=query,
        limit=limit,
        symbol=symbol.upper() if symbol else None,
    )
    
    rows = []
    for a in articles:
        rows.append({
            "title": a.title[:100] + "..." if len(a.title) > 100 else a.title,
            "symbol": a.symbol,
            "source": a.source,
            "published_at": a.published_at.strftime("%Y-%m-%d %H:%M"),
            "url": a.url,
            "content_preview": a.content[:200] + "..." if len(a.content) > 200 else a.content,
        })
    
    return WidgetResponse.table(rows, columns_defs=[
        {"field": "title", "headerName": "Title", "cellDataType": "text", "flex": 2},
        {"field": "symbol", "headerName": "Symbol", "cellDataType": "text"},
        {"field": "source", "headerName": "Source", "cellDataType": "text"},
        {"field": "published_at", "headerName": "Published", "cellDataType": "text"},
        {"field": "content_preview", "headerName": "Preview", "cellDataType": "text", "flex": 2},
        {"field": "url", "headerName": "Link", "cellDataType": "text", "renderFn": "link"},
    ])


@router.get("/sentiment-analysis")
@register_widget(
    create_base_widget_config(
        name="News Sentiment Analysis",
        description="Sentiment distribution for a symbol's recent news",
        category="News",
        endpoint="sentiment-analysis",
        widget_type="chart",
        chart_type="pie",
        grid_w=30,
        grid_h=20,
        params=[
            {
                "paramName": "symbol",
                "value": "AAPL",
                "label": "Symbol",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "days",
                "value": 7,
                "label": "Lookback Days",
                "show": True,
                "type": "number",
            },
            {
                "paramName": "theme",
                "value": "dark",
                "label": "Theme",
                "show": True,
                "type": "text",
                "options": [{"label": "Dark", "value": "dark"}, {"label": "Light", "value": "light"}],
            },
        ],
    )
)
async def get_sentiment_analysis(
    symbol: str = Query("AAPL"),
    days: int = Query(7),
    theme: str = Query("dark"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get sentiment analysis for news (placeholder - uses keyword-based scoring)."""
    from datetime import timedelta
    
    cutoff = datetime.now() - timedelta(days=days)
    
    stmt = select(NewsArticle).where(
        NewsArticle.symbol == symbol.upper(),
        NewsArticle.published_at >= cutoff,
    ).order_by(desc(NewsArticle.published_at)).limit(100)
    
    result = await db.execute(stmt)
    articles = result.scalars().all()
    
    # Simple keyword-based sentiment (placeholder for real NLP)
    positive_keywords = ["beat", "surge", "gain", "rise", "up", "bull", "strong", "growth", "profit", "record", "high", "upgrade", "buy"]
    negative_keywords = ["miss", "fall", "drop", "decline", "down", "bear", "weak", "loss", "low", "downgrade", "sell", "cut", "warn"]
    
    positive = 0
    negative = 0
    neutral = 0
    
    for article in articles:
        text = (article.title + " " + article.content).lower()
        pos_score = sum(1 for kw in positive_keywords if kw in text)
        neg_score = sum(1 for kw in negative_keywords if kw in text)
        
        if pos_score > neg_score:
            positive += 1
        elif neg_score > pos_score:
            negative += 1
        else:
            neutral += 1
    
    total = positive + negative + neutral
    if total == 0:
        return JSONResponse(content={"error": "No articles found"}, status_code=404)
    
    import plotly.graph_objects as go
    
    fig = go.Figure(data=[go.Pie(
        labels=["Positive", "Neutral", "Negative"],
        values=[positive, neutral, negative],
        marker=dict(colors=["#26a69a", "#78909c", "#ef5350"]),
        textinfo="label+percent",
        hole=0.4,
    )])
    
    is_dark = theme == "dark"
    bg_color = "#131722" if is_dark else "#ffffff"
    text_color = "#d1d4dc" if is_dark else "#131722"
    
    fig.update_layout(
        template="plotly_dark" if is_dark else "plotly_white",
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color),
        title=dict(text=f"{symbol.upper()} News Sentiment ({days}d)", x=0.5),
        margin=dict(l=20, r=20, t=50, b=20),
        height=400,
    )
    
    return fig.to_dict()


@router.get("/news-symbols")
@register_widget(
    create_base_widget_config(
        name="Available News Symbols",
        description="Symbols with available news coverage",
        category="News",
        endpoint="news-symbols",
        widget_type="table",
        grid_w=20,
        grid_h=30,
        params=[],
    )
)
async def get_news_symbols_widget(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get symbols with news coverage."""
    result = await db.execute(
        select(NewsArticle.symbol).distinct().where(NewsArticle.symbol != "")
    )
    symbols = sorted([r for r in result.scalars().all() if r])
    
    rows = [{"symbol": s} for s in symbols]
    
    return WidgetResponse.table(rows, columns_defs=[
        {"field": "symbol", "headerName": "Symbol", "cellDataType": "text"},
    ])