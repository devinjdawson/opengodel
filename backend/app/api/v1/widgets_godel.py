from datetime import datetime, timedelta
from typing import Any, Optional
import pandas as pd
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.core.config import settings
from app.core.widget_registry import register_widget, create_base_widget_config, WidgetResponse

router = APIRouter(prefix="/widgets/og", tags=["og terminal widgets"])

from openbb import obb


@router.get("/equity-search")
@register_widget(
    create_base_widget_config(
        name="Equity Search (OG AL)",
        description="Search for equities by symbol or name (AL command)",
        category="OG Terminal",
        endpoint="equity-search",
        widget_type="table",
        grid_w=40,
        grid_h=20,
        params=[
            {
                "paramName": "query",
                "value": "AAPL",
                "label": "Search Query",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "provider",
                "value": "yfinance",
                "label": "Provider",
                "show": True,
                "type": "text",
                "options": [{"label": "YFinance", "value": "yfinance"}, {"label": "FMP", "value": "fmp"}],
            },
        ],
    )
)
async def og_equity_search(
    query: str = Query("AAPL"),
    provider: str = Query("yfinance"),
) -> Any:
    """OG AL command - equity search."""
    try:
        result = await obb.equity.search(query=query, provider=provider)
        df = result.to_df()
        
        if df.empty:
            return JSONResponse(content={"error": "No results found"}, status_code=404)
        
        rows = df.to_dict("records")
        return WidgetResponse.table(rows, columns_defs=[
            {"field": "symbol", "headerName": "Symbol", "cellDataType": "text"},
            {"field": "name", "headerName": "Name", "cellDataType": "text", "flex": 2},
            {"field": "exchange", "headerName": "Exchange", "cellDataType": "text"},
            {"field": "type", "headerName": "Type", "cellDataType": "text"},
        ])
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/company-profile")
@register_widget(
    create_base_widget_config(
        name="Company Profile (OG DES)",
        description="Company description and key info (DES command)",
        category="OG Terminal",
        endpoint="company-profile",
        widget_type="table",
        grid_w=40,
        grid_h=25,
        params=[
            {
                "paramName": "symbol",
                "value": "AAPL",
                "label": "Symbol",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "provider",
                "value": "yfinance",
                "label": "Provider",
                "show": True,
                "type": "text",
                "options": [{"label": "YFinance", "value": "yfinance"}, {"label": "FMP", "value": "fmp"}],
            },
        ],
    )
)
async def og_company_profile(
    symbol: str = Query("AAPL"),
    provider: str = Query("yfinance"),
) -> Any:
    """OG DES command - company profile."""
    try:
        result = await obb.equity.profile(symbol=symbol.upper(), provider=provider)
        df = result.to_df()
        
        if df.empty:
            return JSONResponse(content={"error": "No profile found"}, status_code=404)
        
        # Convert to key-value rows
        profile = df.iloc[0].to_dict()
        rows = [{"field": k, "value": str(v)} for k, v in profile.items() if v is not None and str(v).strip()]
        
        return WidgetResponse.table(rows, columns_defs=[
            {"field": "field", "headerName": "Field", "cellDataType": "text"},
            {"field": "value", "headerName": "Value", "cellDataType": "text", "flex": 2},
        ])
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/financial-statements")
@register_widget(
    create_base_widget_config(
        name="Financial Statements (OG FA)",
        description="Income statement, balance sheet, cash flow (FA command)",
        category="OG Terminal",
        endpoint="financial-statements",
        widget_type="table",
        grid_w=50,
        grid_h=30,
        params=[
            {
                "paramName": "symbol",
                "value": "AAPL",
                "label": "Symbol",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "statement",
                "value": "income",
                "label": "Statement",
                "show": True,
                "type": "text",
                "options": [
                    {"label": "Income Statement", "value": "income"},
                    {"label": "Balance Sheet", "value": "balance"},
                    {"label": "Cash Flow", "value": "cash"},
                ],
            },
            {
                "paramName": "period",
                "value": "annual",
                "label": "Period",
                "show": True,
                "type": "text",
                "options": [
                    {"label": "Annual", "value": "annual"},
                    {"label": "Quarterly", "value": "quarter"},
                    {"label": "TTM", "value": "ttm"},
                ],
            },
            {
                "paramName": "provider",
                "value": "fmp",
                "label": "Provider",
                "show": True,
                "type": "text",
                "options": [{"label": "FMP", "value": "fmp"}, {"label": "YFinance", "value": "yfinance"}],
            },
        ],
    )
)
async def og_financial_statements(
    symbol: str = Query("AAPL"),
    statement: str = Query("income"),
    period: str = Query("annual"),
    provider: str = Query("fmp"),
) -> Any:
    """OG FA command - financial statements."""
    try:
        if statement == "income":
            result = await obb.equity.fundamental.income(symbol=symbol.upper(), period=period, provider=provider)
        elif statement == "balance":
            result = await obb.equity.fundamental.balance(symbol=symbol.upper(), period=period, provider=provider)
        elif statement == "cash":
            result = await obb.equity.fundamental.cash(symbol=symbol.upper(), period=period, provider=provider)
        else:
            return JSONResponse(content={"error": "Invalid statement type"}, status_code=400)
        
        df = result.to_df()
        
        if df.empty:
            return JSONResponse(content={"error": "No data found"}, status_code=404)
        
        # Transpose for better display (dates as columns)
        df_t = df.T.reset_index()
        df_t.columns = ["metric"] + [str(c) for c in df.columns]
        
        rows = df_t.to_dict("records")
        
        columns_defs = [{"field": "metric", "headerName": "Metric", "cellDataType": "text", "flex": 2}]
        for col in df.columns:
            columns_defs.append({"field": str(col), "headerName": str(col), "cellDataType": "text"})
        
        return WidgetResponse.table(rows, columns_defs=columns_defs)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/key-stats")
@register_widget(
    create_base_widget_config(
        name="Key Statistics (OG GR)",
        description="Growth ratios and key metrics (GR command)",
        category="OG Terminal",
        endpoint="key-stats",
        widget_type="table",
        grid_w=40,
        grid_h=25,
        params=[
            {
                "paramName": "symbol",
                "value": "AAPL",
                "label": "Symbol",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "provider",
                "value": "fmp",
                "label": "Provider",
                "show": True,
                "type": "text",
                "options": [{"label": "FMP", "value": "fmp"}, {"label": "YFinance", "value": "yfinance"}],
            },
        ],
    )
)
async def og_key_stats(
    symbol: str = Query("AAPL"),
    provider: str = Query("fmp"),
) -> Any:
    """OG GR command - key statistics and ratios."""
    try:
        result = await obb.equity.fundamental.metrics(symbol=symbol.upper(), provider=provider)
        df = result.to_df()
        
        if df.empty:
            return JSONResponse(content={"error": "No metrics found"}, status_code=404)
        
        # Get latest period
        latest = df.iloc[0] if hasattr(df, 'iloc') else df
        
        if hasattr(latest, 'to_dict'):
            metrics = latest.to_dict()
        else:
            metrics = dict(latest)
        
        # Filter key metrics
        key_metrics = [
            "marketCap", "peRatio", "pbRatio", "psRatio", "pegRatio",
            "roe", "roa", "roi", "debtToEquity", "currentRatio", "quickRatio",
            "grossMargin", "operatingMargin", "netMargin", "freeCashFlowYield",
            "dividendYield", "payoutRatio", "beta", "sharesOutstanding",
            "revenueGrowth", "earningsGrowth", "fcfGrowth",
        ]
        
        rows = []
        for metric in key_metrics:
            if metric in metrics and metrics[metric] is not None:
                val = metrics[metric]
                if isinstance(val, (int, float)):
                    if "ratio" in metric.lower() or "margin" in metric.lower() or "yield" in metric.lower() or "growth" in metric.lower():
                        rows.append({"metric": metric, "value": f"{val:.2%}" if abs(val) < 10 else f"{val:.2f}"})
                    else:
                        rows.append({"metric": metric, "value": f"{val:,.2f}" if abs(val) > 100 else f"{val:.2f}"})
                else:
                    rows.append({"metric": metric, "value": str(val)})
        
        return WidgetResponse.table(rows, columns_defs=[
            {"field": "metric", "headerName": "Metric", "cellDataType": "text"},
            {"field": "value", "headerName": "Value", "cellDataType": "text"},
        ])
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/analyst-estimates")
@register_widget(
    create_base_widget_config(
        name="Analyst Estimates (OG ERN)",
        description="Earnings estimates and revisions (ERN command)",
        category="OG Terminal",
        endpoint="analyst-estimates",
        widget_type="table",
        grid_w=45,
        grid_h=25,
        params=[
            {
                "paramName": "symbol",
                "value": "AAPL",
                "label": "Symbol",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "provider",
                "value": "fmp",
                "label": "Provider",
                "show": True,
                "type": "text",
                "options": [{"label": "FMP", "value": "fmp"}, {"label": "YFinance", "value": "yfinance"}],
            },
        ],
    )
)
async def og_analyst_estimates(
    symbol: str = Query("AAPL"),
    provider: str = Query("fmp"),
) -> Any:
    """OG ERN command - analyst estimates."""
    try:
        result = await obb.equity.estimates.forward_eps(symbol=symbol.upper(), provider=provider)
        df = result.to_df()
        
        if df.empty:
            return JSONResponse(content={"error": "No estimates found"}, status_code=404)
        
        rows = df.to_dict("records")
        return WidgetResponse.table(rows, columns_defs=[
            {"field": "fiscalPeriod", "headerName": "Period", "cellDataType": "text"},
            {"field": "estimate", "headerName": "EPS Estimate", "cellDataType": "number"},
            {"field": "estimateHigh", "headerName": "High", "cellDataType": "number"},
            {"field": "estimateLow", "headerName": "Low", "cellDataType": "number"},
            {"field": "numberOfAnalysts", "headerName": "# Analysts", "cellDataType": "number"},
            {"field": "lastUpdated", "headerName": "Updated", "cellDataType": "text"},
        ])
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/insider-trading")
@register_widget(
    create_base_widget_config(
        name="Insider Trading (OG INS)",
        description="Insider transactions (INS command)",
        category="OG Terminal",
        endpoint="insider-trading",
        widget_type="table",
        grid_w=50,
        grid_h=25,
        params=[
            {
                "paramName": "symbol",
                "value": "AAPL",
                "label": "Symbol",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "limit",
                "value": 50,
                "label": "Limit",
                "show": True,
                "type": "number",
            },
            {
                "paramName": "provider",
                "value": "fmp",
                "label": "Provider",
                "show": True,
                "type": "text",
                "options": [{"label": "FMP", "value": "fmp"}, {"label": "SEC", "value": "sec"}],
            },
        ],
    )
)
async def og_insider_trading(
    symbol: str = Query("AAPL"),
    limit: int = Query(50),
    provider: str = Query("fmp"),
) -> Any:
    """OG INS command - insider trading."""
    try:
        result = await obb.equity.ownership.insider_trading(symbol=symbol.upper(), provider=provider, limit=limit)
        df = result.to_df()
        
        if df.empty:
            return JSONResponse(content={"error": "No insider data found"}, status_code=404)
        
        rows = df.to_dict("records")
        return WidgetResponse.table(rows, columns_defs=[
            {"field": "filingDate", "headerName": "Filing Date", "cellDataType": "text"},
            {"field": "transactionDate", "headerName": "Txn Date", "cellDataType": "text"},
            {"field": "insiderName", "headerName": "Insider", "cellDataType": "text"},
            {"field": "transactionType", "headerName": "Type", "cellDataType": "text"},
            {"field": "shares", "headerName": "Shares", "cellDataType": "number"},
            {"field": "price", "headerName": "Price", "cellDataType": "number"},
            {"field": "value", "headerName": "Value", "cellDataType": "number"},
            {"field": "sharesOwned", "headerName": "Owned After", "cellDataType": "number"},
        ])
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/institutional-ownership")
@register_widget(
    create_base_widget_config(
        name="Institutional Ownership (OG IMAPI)",
        description="13F institutional holdings (IMAPI command)",
        category="OG Terminal",
        endpoint="institutional-ownership",
        widget_type="table",
        grid_w=50,
        grid_h=25,
        params=[
            {
                "paramName": "symbol",
                "value": "AAPL",
                "label": "Symbol",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "provider",
                "value": "fmp",
                "label": "Provider",
                "show": True,
                "type": "text",
                "options": [{"label": "FMP", "value": "fmp"}],
            },
        ],
    )
)
async def og_institutional_ownership(
    symbol: str = Query("AAPL"),
    provider: str = Query("fmp"),
) -> Any:
    """OG IMAPI command - institutional ownership."""
    try:
        result = await obb.equity.ownership.institutional(symbol=symbol.upper(), provider=provider)
        df = result.to_df()
        
        if df.empty:
            return JSONResponse(content={"error": "No institutional data found"}, status_code=404)
        
        rows = df.to_dict("records")
        return WidgetResponse.table(rows, columns_defs=[
            {"field": "institution", "headerName": "Institution", "cellDataType": "text", "flex": 2},
            {"field": "shares", "headerName": "Shares", "cellDataType": "number"},
            {"field": "value", "headerName": "Value", "cellDataType": "number"},
            {"field": "portfolioPct", "headerName": "% Portfolio", "cellDataType": "number"},
            {"field": "change", "headerName": "Change", "cellDataType": "number"},
            {"field": "reportDate", "headerName": "Report Date", "cellDataType": "text"},
        ])
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/dividend-history")
@register_widget(
    create_base_widget_config(
        name="Dividend History (OG DVD)",
        description="Dividend payments and yield history (DVD command)",
        category="OG Terminal",
        endpoint="dividend-history",
        widget_type="chart",
        chart_type="bar",
        grid_w=40,
        grid_h=25,
        params=[
            {
                "paramName": "symbol",
                "value": "AAPL",
                "label": "Symbol",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "provider",
                "value": "fmp",
                "label": "Provider",
                "show": True,
                "type": "text",
                "options": [{"label": "FMP", "value": "fmp"}, {"label": "YFinance", "value": "yfinance"}],
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
async def og_dividend_history(
    symbol: str = Query("AAPL"),
    provider: str = Query("fmp"),
    theme: str = Query("dark"),
) -> Any:
    """OG DVD command - dividend history."""
    try:
        result = await obb.equity.fundamental.dividends(symbol=symbol.upper(), provider=provider)
        df = result.to_df()
        
        if df.empty:
            return JSONResponse(content={"error": "No dividend data found"}, status_code=404)
        
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df["date"],
            y=df["dividend"],
            name="Dividend",
            marker_color="#2962ff",
        ))
        
        if "yield" in df.columns:
            fig.add_trace(go.Scatter(
                x=df["date"],
                y=df["yield"] * 100,
                mode="lines+markers",
                name="Yield (%)",
                line=dict(color="#ef5350", width=2),
                yaxis="y2",
            ))
            
            fig.update_layout(yaxis2=dict(
                title="Yield (%)", overlaying="y", side="right", showgrid=False,
            ))
        
        is_dark = theme == "dark"
        bg_color = "#131722" if is_dark else "#ffffff"
        text_color = "#d1d4dc" if is_dark else "#131722"
        grid_color = "#2a2e39" if is_dark else "#e1e3e6"
        
        fig.update_layout(
            template="plotly_dark" if is_dark else "plotly_white",
            paper_bgcolor=bg_color,
            plot_bgcolor=bg_color,
            font=dict(color=text_color),
            xaxis=dict(title="Date", gridcolor=grid_color),
            yaxis=dict(title="Dividend ($)", gridcolor=grid_color),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=50, r=50, t=30, b=50),
            height=500,
        )
        
        return fig.to_dict()
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)