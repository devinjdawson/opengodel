from datetime import datetime, timedelta
from typing import Any, Optional, List
import pandas as pd
import asyncio
import json
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.core.config import settings
from app.core.widget_registry import register_widget, create_base_widget_config, WidgetResponse
from app.services.openbb_service import openbb_service

router = APIRouter(prefix="/widgets/equity", tags=["equity widgets"])


async def _get_historical_data(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "1d",
    provider: str = "yfinance",
) -> pd.DataFrame:
    """Fetch historical price data from OpenBB via service."""
    try:
        # Run sync OpenBB call in thread pool
        loop = asyncio.get_event_loop()
        candles = await loop.run_in_executor(
            None,
            openbb_service.get_historical_prices,
            symbol,
            start_date,
            end_date,
            interval,
            provider,
        )
        
        if not candles:
            return pd.DataFrame()
        
        df = pd.DataFrame([{
            "date": c.timestamp,
            "open": c.open,
            "high": c.high,
            "low": c.low,
            "close": c.close,
            "volume": c.volume,
        } for c in candles])
        
        df = df.sort_values("date")
        df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        raise Exception(f"Failed to fetch historical data: {str(e)}")


async def _get_quote(symbol: str, provider: str = "yfinance") -> dict:
    """Get current quote from OpenBB via service."""
    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            openbb_service.get_equity_quote,
            symbol,
            provider,
        )
    except Exception as e:
        raise Exception(f"Failed to fetch quote: {str(e)}")


@router.get("/candlestick")
@register_widget(
    create_base_widget_config(
        name="Candlestick Chart",
        description="Interactive candlestick chart with volume",
        category="Equity",
        endpoint="candlestick",
        widget_type="chart",
        chart_type="candlestick",
        grid_w=50,
        grid_h=25,
        params=[
            {
                "paramName": "symbol",
                "value": "AAPL",
                "label": "Symbol",
                "show": True,
                "description": "Stock symbol to display",
                "type": "text",
            },
            {
                "paramName": "start_date",
                "value": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
                "label": "Start Date",
                "show": True,
                "description": "Start date for data",
                "type": "date",
            },
            {
                "paramName": "end_date",
                "value": datetime.now().strftime("%Y-%m-%d"),
                "label": "End Date",
                "show": True,
                "description": "End date for data",
                "type": "date",
            },
            {
                "paramName": "interval",
                "value": "1d",
                "label": "Interval",
                "show": True,
                "description": "Data interval",
                "type": "text",
                "options": [
                    {"label": "1 Minute", "value": "1m"},
                    {"label": "5 Minutes", "value": "5m"},
                    {"label": "15 Minutes", "value": "15m"},
                    {"label": "1 Hour", "value": "1h"},
                    {"label": "1 Day", "value": "1d"},
                    {"label": "1 Week", "value": "1wk"},
                    {"label": "1 Month", "value": "1mo"},
                ],
            },
            {
                "paramName": "show_volume",
                "value": True,
                "label": "Show Volume",
                "show": True,
                "description": "Display volume bars",
                "type": "boolean",
            },
            {
                "paramName": "show_ma",
                "value": True,
                "label": "Show Moving Averages",
                "show": True,
                "description": "Display 20/50/200 day MAs",
                "type": "boolean",
            },
            {
                "paramName": "theme",
                "value": "dark",
                "label": "Theme",
                "show": True,
                "description": "Chart theme",
                "type": "text",
                "options": [
                    {"label": "Dark", "value": "dark"},
                    {"label": "Light", "value": "light"},
                ],
            },
        ],
    )
)
async def get_candlestick_chart(
    symbol: str = Query("AAPL"),
    start_date: str = Query((datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")),
    end_date: str = Query(datetime.now().strftime("%Y-%m-%d")),
    interval: str = Query("1d"),
    show_volume: bool = Query(True),
    show_ma: bool = Query(True),
    theme: str = Query("dark"),
) -> Any:
    """Get candlestick chart with optional volume and moving averages."""
    try:
        df = await _get_historical_data(symbol.upper(), start_date, end_date, interval)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
    if df.empty:
        return JSONResponse(content={"error": f"No data found for {symbol}"}, status_code=404)
    
    fig = go.Figure()
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df["date"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name=symbol.upper(),
        increasing_line_color="#26a69a",
        decreasing_line_color="#ef5350",
    ))
    
    # Moving averages
    if show_ma:
        for window, color, name in [(20, "#2196f3", "MA20"), (50, "#ff9800", "MA50"), (200, "#9c27b0", "MA200")]:
            if len(df) >= window:
                ma = df["close"].rolling(window=window).mean()
                fig.add_trace(go.Scatter(
                    x=df["date"],
                    y=ma,
                    mode="lines",
                    name=name,
                    line=dict(color=color, width=1),
                    opacity=0.8,
                ))
    
    # Volume
    if show_volume:
        fig.add_trace(go.Bar(
            x=df["date"],
            y=df["volume"],
            name="Volume",
            marker_color=df.apply(
                lambda row: "#26a69a" if row["close"] >= row["open"] else "#ef5350", axis=1
            ),
            opacity=0.3,
            yaxis="y2",
        ))
        
        fig.update_layout(
            yaxis2=dict(
                title="Volume",
                overlaying="y",
                side="right",
                showgrid=False,
                range=[0, df["volume"].max() * 4],
            ),
        )
    
    # Theme
    is_dark = theme == "dark"
    bg_color = "#131722" if is_dark else "#ffffff"
    text_color = "#d1d4dc" if is_dark else "#131722"
    grid_color = "#2a2e39" if is_dark else "#e1e3e6"
    
    fig.update_layout(
        template="plotly_dark" if is_dark else "plotly_white",
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color),
        xaxis=dict(
            rangeslider=dict(visible=False),
            gridcolor=grid_color,
            type="date",
        ),
        yaxis=dict(
            title="Price",
            gridcolor=grid_color,
            side="left",
        ),
        yaxis2=dict(
            title="Volume",
            gridcolor=grid_color,
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=50, r=50, t=30, b=50),
        height=600,
    )
    
    return json.loads(fig.to_json())


@router.get("/technical-indicators")
@register_widget(
    create_base_widget_config(
        name="Technical Indicators",
        description="RSI, MACD, Bollinger Bands, and Stochastic",
        category="Equity",
        endpoint="technical-indicators",
        widget_type="chart",
        chart_type="line",
        grid_w=50,
        grid_h=30,
        params=[
            {
                "paramName": "symbol",
                "value": "AAPL",
                "label": "Symbol",
                "show": True,
                "description": "Stock symbol",
                "type": "text",
            },
            {
                "paramName": "start_date",
                "value": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
                "label": "Start Date",
                "show": True,
                "type": "date",
            },
            {
                "paramName": "indicators",
                "value": "RSI,MACD,BB",
                "label": "Indicators",
                "show": True,
                "description": "Comma-separated indicators",
                "type": "text",
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
async def get_technical_indicators(
    symbol: str = Query("AAPL"),
    start_date: str = Query((datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")),
    indicators: str = Query("RSI,MACD,BB"),
    theme: str = Query("dark"),
) -> Any:
    """Get technical indicators chart."""
    end_date = datetime.now().strftime("%Y-%m-%d")
    try:
        df = await _get_historical_data(symbol.upper(), start_date, end_date)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
    if df.empty:
        return JSONResponse(content={"error": f"No data found for {symbol}"}, status_code=404)
    
    indicator_list = [i.strip().upper() for i in indicators.split(",")]
    
    # Calculate indicators
    close = df["close"]
    
    fig = make_subplots(
        rows=len(indicator_list) + 1,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5] + [0.5 / len(indicator_list)] * len(indicator_list),
        subplot_titles=[f"{symbol.upper()} Price"] + indicator_list,
    )
    
    # Price with Bollinger Bands
    if "BB" in indicator_list:
        ma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper = ma20 + 2 * std20
        lower = ma20 - 2 * std20
        
        fig.add_trace(go.Scatter(x=df["date"], y=close, mode="lines", name="Close", line=dict(color="#2962ff")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["date"], y=upper, mode="lines", name="BB Upper", line=dict(color="#26a69a", dash="dash")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["date"], y=lower, mode="lines", name="BB Lower", line=dict(color="#ef5350", dash="dash"), fill="tonexty", fillcolor="rgba(38,166,154,0.1)"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["date"], y=ma20, mode="lines", name="MA20", line=dict(color="#ff9800")), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(x=df["date"], y=close, mode="lines", name="Close", line=dict(color="#2962ff")), row=1, col=1)
    
    row = 2
    if "RSI" in indicator_list:
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        fig.add_trace(go.Scatter(x=df["date"], y=rsi, mode="lines", name="RSI", line=dict(color="#9c27b0")), row=row, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="#ef5350", row=row, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#26a69a", row=row, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="#78909c", row=row, col=1)
        fig.update_yaxes(range=[0, 100], row=row, col=1)
        row += 1
    
    if "MACD" in indicator_list:
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        fig.add_trace(go.Scatter(x=df["date"], y=macd, mode="lines", name="MACD", line=dict(color="#2962ff")), row=row, col=1)
        fig.add_trace(go.Scatter(x=df["date"], y=signal, mode="lines", name="Signal", line=dict(color="#ff9800")), row=row, col=1)
        fig.add_trace(go.Bar(x=df["date"], y=histogram, name="Histogram", marker_color=histogram.apply(lambda x: "#26a69a" if x >= 0 else "#ef5350")), row=row, col=1)
        row += 1
    
    if "STOCH" in indicator_list:
        low14 = df["low"].rolling(14).min()
        high14 = df["high"].rolling(14).max()
        k = 100 * (close - low14) / (high14 - low14)
        d = k.rolling(3).mean()
        
        fig.add_trace(go.Scatter(x=df["date"], y=k, mode="lines", name="%K", line=dict(color="#2962ff")), row=row, col=1)
        fig.add_trace(go.Scatter(x=df["date"], y=d, mode="lines", name="%D", line=dict(color="#ff9800")), row=row, col=1)
        fig.add_hline(y=80, line_dash="dash", line_color="#ef5350", row=row, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="#26a69a", row=row, col=1)
        fig.update_yaxes(range=[0, 100], row=row, col=1)
    
    is_dark = theme == "dark"
    bg_color = "#131722" if is_dark else "#ffffff"
    text_color = "#d1d4dc" if is_dark else "#131722"
    grid_color = "#2a2e39" if is_dark else "#e1e3e6"
    
    fig.update_layout(
        template="plotly_dark" if is_dark else "plotly_white",
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color, size=10),
        xaxis=dict(rangeslider=dict(visible=False), gridcolor=grid_color),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=50, b=50),
        height=800,
    )
    
    return json.loads(fig.to_json())


@router.get("/quote-summary")
@register_widget(
    create_base_widget_config(
        name="Quote Summary",
        description="Real-time quote with key statistics",
        category="Equity",
        endpoint="quote-summary",
        widget_type="table",
        grid_w=25,
        grid_h=20,
        params=[
            {
                "paramName": "symbol",
                "value": "AAPL",
                "label": "Symbol",
                "show": True,
                "type": "text",
            },
        ],
    )
)
async def get_quote_summary(
    symbol: str = Query("AAPL"),
) -> Any:
    """Get quote summary table."""
    try:
        quote = await _get_quote(symbol.upper())
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
    if not quote:
        return JSONResponse(content={"error": f"No quote found for {symbol}"}, status_code=404)
    
    # Get profile for market_cap and pe_ratio
    profile = None
    try:
        loop = asyncio.get_event_loop()
        profile = await loop.run_in_executor(
            None,
            openbb_service.get_company_profile,
            symbol.upper(),
            "yfinance",
        )
    except Exception:
        pass
    
    # Calculate change from last_price and prev_close
    last_price = quote.get('last_price', 0) or 0
    prev_close = quote.get('prev_close', 0) or 0
    change = last_price - prev_close if prev_close else 0
    change_percent = (change / prev_close * 100) if prev_close else 0
    
    # Format key metrics
    metrics = [
        {"metric": "Last Price", "value": f"${last_price:,.2f}"},
        {"metric": "Change", "value": f"${change:,.2f}"},
        {"metric": "Change %", "value": f"{change_percent:,.2f}%"},
        {"metric": "Volume", "value": f"{quote.get('volume', 0):,.0f}"},
        {"metric": "Avg Volume", "value": f"{quote.get('volume_average', 0):,.0f}"},
        {"metric": "Market Cap", "value": f"${(profile or {}).get('market_cap', 0):,.0f}" if profile else "N/A"},
        {"metric": "P/E Ratio", "value": f"{(profile or {}).get('pe_ratio', 0):,.2f}" if profile and (profile or {}).get('pe_ratio') else "N/A"},
        {"metric": "52W High", "value": f"${quote.get('year_high', 0):,.2f}"},
        {"metric": "52W Low", "value": f"${quote.get('year_low', 0):,.2f}"},
        {"metric": "Open", "value": f"${quote.get('open', 0):,.2f}"},
        {"metric": "High", "value": f"${quote.get('high', 0):,.2f}"},
        {"metric": "Low", "value": f"${quote.get('low', 0):,.2f}"},
    ]
    
    return WidgetResponse.table(metrics, columns_defs=[
        {"field": "metric", "headerName": "Metric", "cellDataType": "text"},
        {"field": "value", "headerName": "Value", "cellDataType": "text"},
    ])