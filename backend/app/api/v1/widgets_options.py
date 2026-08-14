from datetime import datetime, timedelta
from typing import Any, Optional
import pandas as pd
import numpy as np
import asyncio
import functools
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app.core.config import settings
from app.core.widget_registry import register_widget, create_base_widget_config, WidgetResponse

router = APIRouter(prefix="/widgets/options", tags=["options widgets"])

from openbb import obb


async def _run_obb_sync(func, *args, **kwargs):
    """Run synchronous OpenBB SDK call in thread pool."""
    loop = asyncio.get_event_loop()
    if kwargs:
        return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
    return await loop.run_in_executor(None, func, *args)


async def _get_options_chain(
    symbol: str,
    expiration: str = "",
    provider: str = "cboe",
) -> pd.DataFrame:
    """Fetch options chain data."""
    try:
        params = {"symbol": symbol, "provider": provider}
        if expiration:
            params["expiration"] = expiration
        result = await _run_obb_sync(obb.derivatives.options.chains, **params)
        df = result.to_df()
        return df
    except Exception as e:
        return pd.DataFrame()


async def _get_historical_price(
    symbol: str,
    start_date: str,
    end_date: str,
    interval: str = "1d",
    provider: str = "yfinance",
) -> pd.DataFrame:
    """Fetch historical price data."""
    try:
        result = await _run_obb_sync(obb.equity.price.historical,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            provider=provider,
        )
        df = result.to_df()
        if not df.empty:
            df = df.sort_values("date")
            df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        return pd.DataFrame()


@router.get("/volatility-surface")
@register_widget(
    create_base_widget_config(
        name="Volatility Surface",
        description="3D implied volatility surface across strikes and expirations",
        category="Options",
        endpoint="volatility-surface",
        widget_type="chart",
        chart_type="surface",
        grid_w=50,
        grid_h=30,
        params=[
            {
                "paramName": "symbol",
                "value": "SPY",
                "label": "Symbol",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "provider",
                "value": "cboe",
                "label": "Provider",
                "show": True,
                "type": "text",
                "options": [{"label": "CBOE", "value": "cboe"}, {"label": "YFinance", "value": "yfinance"}],
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
async def get_volatility_surface(
    symbol: str = Query("SPY"),
    provider: str = Query("cboe"),
    theme: str = Query("dark"),
) -> Any:
    """Get implied volatility surface."""
    try:
        # Get options chains for multiple expirations
        chains_result = await _run_obb_sync(obb.derivatives.options.chains,symbol=symbol.upper(), provider=provider)
        df = chains_result.to_df()
        
        if df.empty or "implied_volatility" not in df.columns:
            return JSONResponse(content={"error": "No options data with IV available"}, status_code=404)
        
        # Filter valid IV data
        df = df.dropna(subset=["implied_volatility", "strike", "expiration", "option_type"])
        df["implied_volatility"] = pd.to_numeric(df["implied_volatility"], errors="coerce")
        df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
        df = df.dropna(subset=["implied_volatility", "strike"])
        df = df[(df["implied_volatility"] > 0) & (df["implied_volatility"] < 5)]
        
        if df.empty:
            return JSONResponse(content={"error": "No valid IV data"}, status_code=404)
        
        # Get current price for moneyness
        quote_result = await _run_obb_sync(obb.equity.price.quote,symbol=symbol.upper(), provider="yfinance")
        quote_df = quote_result.to_df()
        spot = quote_df.iloc[0].get("close", quote_df.iloc[0].get("last_price", 0)) if not quote_df.empty else 0
        
        # Calculate DTE and moneyness
        df["expiration"] = pd.to_datetime(df["expiration"])
        df["dte"] = (df["expiration"] - pd.Timestamp.now()).dt.days
        df = df[(df["dte"] > 0) & (df["dte"] < 365)]
        
        if spot > 0:
            df["moneyness"] = df["strike"] / spot
        
        # Separate calls and puts
        calls = df[df["option_type"].str.lower() == "call"]
        puts = df[df["option_type"].str.lower() == "put"]
        
        # Create 3D surface for calls
        if not calls.empty:
            pivot_calls = calls.pivot_table(
                values="implied_volatility",
                index="strike",
                columns="dte",
                aggfunc="mean",
            )
            
            fig = go.Figure(data=[go.Surface(
                z=pivot_calls.values,
                x=pivot_calls.columns,
                y=pivot_calls.index,
                colorscale="Viridis",
                name="Calls IV",
                showscale=True,
            )])
            
            # Add puts as second surface
            if not puts.empty:
                pivot_puts = puts.pivot_table(
                    values="implied_volatility",
                    index="strike",
                    columns="dte",
                    aggfunc="mean",
                )
                fig.add_trace(go.Surface(
                    z=pivot_puts.values,
                    x=pivot_puts.columns,
                    y=pivot_puts.index,
                    colorscale="Reds",
                    name="Puts IV",
                    showscale=False,
                    opacity=0.7,
                ))
            
            is_dark = theme == "dark"
            bg_color = "#131722" if is_dark else "#ffffff"
            text_color = "#d1d4dc" if is_dark else "#131722"
            
            fig.update_layout(
                template="plotly_dark" if is_dark else "plotly_white",
                paper_bgcolor=bg_color,
                plot_bgcolor=bg_color,
                font=dict(color=text_color),
                scene=dict(
                    xaxis_title="Days to Expiration",
                    yaxis_title="Strike",
                    zaxis_title="Implied Volatility",
                    xaxis=dict(gridcolor="#2a2e39" if is_dark else "#e1e3e6"),
                    yaxis=dict(gridcolor="#2a2e39" if is_dark else "#e1e3e6"),
                    zaxis=dict(gridcolor="#2a2e39" if is_dark else "#e1e3e6"),
                ),
                title=dict(text=f"{symbol.upper()} Implied Volatility Surface", x=0.5),
                margin=dict(l=0, r=0, t=50, b=0),
                height=700,
            )
            
            return fig.to_dict()
        else:
            return JSONResponse(content={"error": "No call options data"}, status_code=404)
            
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/option-chain")
@register_widget(
    create_base_widget_config(
        name="Option Chain",
        description="Options chain with Greeks and IV",
        category="Options",
        endpoint="option-chain",
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
            },
            {
                "paramName": "expiration",
                "value": "",
                "label": "Expiration",
                "show": True,
                "description": "Expiration date (YYYY-MM-DD)",
                "type": "date",
            },
            {
                "paramName": "provider",
                "value": "cboe",
                "label": "Provider",
                "show": True,
                "type": "text",
                "options": [{"label": "CBOE", "value": "cboe"}, {"label": "YFinance", "value": "yfinance"}],
            },
        ],
    )
)
async def get_option_chain(
    symbol: str = Query("AAPL"),
    expiration: str = Query(""),
    provider: str = Query("cboe"),
) -> Any:
    """Get option chain table."""
    try:
        df = await _get_options_chain(symbol.upper(), expiration, provider)
        
        if df.empty:
            return JSONResponse(content={"error": "No options data"}, status_code=404)
        
        # Filter and format columns
        display_cols = []
        for col in ["expiration", "strike", "option_type", "bid", "ask", "last_price", "volume", "open_interest", "implied_volatility", "delta", "gamma", "theta", "vega", "rho"]:
            if col in df.columns:
                display_cols.append(col)
        
        if not display_cols:
            return JSONResponse(content={"error": "No relevant columns in options data"}, status_code=404)
        
        df = df[display_cols].copy()
        
        # Format numeric columns
        for col in ["bid", "ask", "last_price", "strike"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").round(2)
        
        for col in ["implied_volatility", "delta", "gamma", "theta", "vega", "rho"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").round(4)
        
        for col in ["volume", "open_interest"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        
        # Sort by expiration, option_type, strike
        sort_cols = [c for c in ["expiration", "option_type", "strike"] if c in df.columns]
        df = df.sort_values(sort_cols)
        
        rows = df.to_dict("records")
        
        columns_defs = [
            {"field": "expiration", "headerName": "Expiration", "cellDataType": "text"},
            {"field": "strike", "headerName": "Strike", "cellDataType": "number"},
            {"field": "option_type", "headerName": "Type", "cellDataType": "text"},
            {"field": "bid", "headerName": "Bid", "cellDataType": "number"},
            {"field": "ask", "headerName": "Ask", "cellDataType": "number"},
            {"field": "last_price", "headerName": "Last", "cellDataType": "number"},
            {"field": "volume", "headerName": "Volume", "cellDataType": "number"},
            {"field": "open_interest", "headerName": "OI", "cellDataType": "number"},
            {"field": "implied_volatility", "headerName": "IV", "cellDataType": "number", "renderFn": "percent"},
            {"field": "delta", "headerName": "Delta", "cellDataType": "number"},
            {"field": "gamma", "headerName": "Gamma", "cellDataType": "number"},
            {"field": "theta", "headerName": "Theta", "cellDataType": "number"},
            {"field": "vega", "headerName": "Vega", "cellDataType": "number"},
            {"field": "rho", "headerName": "Rho", "cellDataType": "number"},
        ]
        
        # Filter to only columns that exist
        existing_fields = set(df.columns)
        columns_defs = [c for c in columns_defs if c["field"] in existing_fields]
        
        return WidgetResponse.table(rows, columns_defs=columns_defs)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/iv-term-structure")
@register_widget(
    create_base_widget_config(
        name="IV Term Structure",
        description="Implied volatility by expiration (ATM)",
        category="Options",
        endpoint="iv-term-structure",
        widget_type="chart",
        chart_type="line",
        grid_w=40,
        grid_h=20,
        params=[
            {
                "paramName": "symbol",
                "value": "SPY",
                "label": "Symbol",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "provider",
                "value": "cboe",
                "label": "Provider",
                "show": True,
                "type": "text",
                "options": [{"label": "CBOE", "value": "cboe"}, {"label": "YFinance", "value": "yfinance"}],
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
async def get_iv_term_structure(
    symbol: str = Query("SPY"),
    provider: str = Query("cboe"),
    theme: str = Query("dark"),
) -> Any:
    """Get ATM IV term structure."""
    try:
        # Get current price
        quote_result = await _run_obb_sync(obb.equity.price.quote,symbol=symbol.upper(), provider="yfinance")
        quote_df = quote_result.to_df()
        spot = quote_df.iloc[0].get("close", quote_df.iloc[0].get("last_price", 0)) if not quote_df.empty else 0
        
        if spot == 0:
            return JSONResponse(content={"error": "Could not get spot price"}, status_code=404)
        
        # Get options chains
        chains_result = await _run_obb_sync(obb.derivatives.options.chains,symbol=symbol.upper(), provider=provider)
        df = chains_result.to_df()
        
        if df.empty or "implied_volatility" not in df.columns:
            return JSONResponse(content={"error": "No options data"}, status_code=404)
        
        df = df.dropna(subset=["implied_volatility", "strike", "expiration", "option_type"])
        df["implied_volatility"] = pd.to_numeric(df["implied_volatility"], errors="coerce")
        df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
        df = df[(df["implied_volatility"] > 0) & (df["implied_volatility"] < 5)]
        
        df["expiration"] = pd.to_datetime(df["expiration"])
        df["dte"] = (df["expiration"] - pd.Timestamp.now()).dt.days
        df = df[(df["dte"] > 0) & (df["dte"] < 365)]
        df["moneyness"] = abs(df["strike"] - spot) / spot
        
        # Get ATM options (closest to spot) for each expiration
        atm_data = []
        for exp in df["expiration"].unique():
            exp_df = df[df["expiration"] == exp]
            for opt_type in ["call", "put"]:
                type_df = exp_df[exp_df["option_type"].str.lower() == opt_type]
                if not type_df.empty:
                    atm_row = type_df.loc[type_df["moneyness"].idxmin()]
                    atm_data.append({
                        "expiration": exp,
                        "dte": atm_row["dte"],
                        "iv": atm_row["implied_volatility"],
                        "type": opt_type.upper(),
                    })
        
        if not atm_data:
            return JSONResponse(content={"error": "No ATM data"}, status_code=404)
        
        atm_df = pd.DataFrame(atm_data)
        
        fig = go.Figure()
        
        for opt_type, color, name in [("CALL", "#26a69a", "Calls"), ("PUT", "#ef5350", "Puts")]:
            type_df = atm_df[atm_df["type"] == opt_type].sort_values("dte")
            if not type_df.empty:
                fig.add_trace(go.Scatter(
                    x=type_df["dte"],
                    y=type_df["iv"] * 100,
                    mode="lines+markers",
                    name=name,
                    line=dict(color=color, width=2),
                    marker=dict(size=6),
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
            xaxis=dict(title="Days to Expiration", gridcolor=grid_color),
            yaxis=dict(title="ATM Implied Volatility (%)", gridcolor=grid_color),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=50, r=50, t=30, b=50),
            height=500,
        )
        
        return fig.to_dict()
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/greeks-dashboard")
@register_widget(
    create_base_widget_config(
        name="Greeks Dashboard",
        description="Option Greeks analysis for a position",
        category="Options",
        endpoint="greeks-dashboard",
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
                "paramName": "expiration",
                "value": "",
                "label": "Expiration",
                "show": True,
                "type": "date",
            },
            {
                "paramName": "strike",
                "value": 0,
                "label": "Strike (0=ATM)",
                "show": True,
                "type": "number",
            },
            {
                "paramName": "option_type",
                "value": "call",
                "label": "Option Type",
                "show": True,
                "type": "text",
                "options": [{"label": "Call", "value": "call"}, {"label": "Put", "value": "put"}],
            },
            {
                "paramName": "provider",
                "value": "cboe",
                "label": "Provider",
                "show": True,
                "type": "text",
                "options": [{"label": "CBOE", "value": "cboe"}, {"label": "YFinance", "value": "yfinance"}],
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
async def get_greeks_dashboard(
    symbol: str = Query("AAPL"),
    expiration: str = Query(""),
    strike: float = Query(0),
    option_type: str = Query("call"),
    provider: str = Query("cboe"),
    theme: str = Query("dark"),
) -> Any:
    """Get Greeks for a specific option."""
    try:
        df = await _get_options_chain(symbol.upper(), expiration, provider)
        
        if df.empty:
            return JSONResponse(content={"error": "No options data"}, status_code=404)
        
        df = df.dropna(subset=["strike", "option_type", "expiration"])
        df["strike"] = pd.to_numeric(df["strike"], errors="coerce")
        df["expiration"] = pd.to_datetime(df["expiration"])
        
        # Filter by expiration if provided
        if expiration:
            df = df[df["expiration"].dt.strftime("%Y-%m-%d") == expiration]
        
        # Filter by option type
        df = df[df["option_type"].str.lower() == option_type.lower()]
        
        if df.empty:
            return JSONResponse(content={"error": "No matching options"}, status_code=404)
        
        # If strike=0, find ATM
        if strike == 0:
            quote_result = await _run_obb_sync(obb.equity.price.quote,symbol=symbol.upper(), provider="yfinance")
            quote_df = quote_result.to_df()
            spot = quote_df.iloc[0].get("close", quote_df.iloc[0].get("last_price", 0)) if not quote_df.empty else 0
            if spot > 0:
                strike = spot
        
        # Find closest strike
        df["strike_diff"] = abs(df["strike"] - strike)
        target = df.loc[df["strike_diff"].idxmin()]
        
        greeks = ["delta", "gamma", "theta", "vega", "rho"]
        available_greeks = [g for g in greeks if g in target.index and pd.notna(target[g])]
        
        if not available_greeks:
            return JSONResponse(content={"error": "No Greeks data available"}, status_code=404)
        
        import plotly.graph_objects as go
        
        fig = go.Figure()
        
        values = []
        labels = []
        for g in available_greeks:
            val = float(target[g])
            values.append(val)
            labels.append(g.upper())
        
        colors = ["#2962ff", "#26a69a", "#ff9800", "#9c27b0", "#ef5350"][:len(values)]
        
        fig.add_trace(go.Bar(
            x=labels,
            y=values,
            marker_color=colors,
            text=[f"{v:.4f}" for v in values],
            textposition="auto",
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
            xaxis=dict(title="Greek", gridcolor=grid_color),
            yaxis=dict(title="Value", gridcolor=grid_color),
            title=dict(text=f"{symbol.upper()} {option_type.upper()} {target['strike']:.0f} Exp {target['expiration'].strftime('%Y-%m-%d')} Greeks", x=0.5),
            margin=dict(l=50, r=50, t=50, b=50),
            height=500,
        )
        
        return fig.to_dict()
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)