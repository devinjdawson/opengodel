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

router = APIRouter(prefix="/widgets/macro", tags=["macro widgets"])


async def _run_obb_sync(func, *args, **kwargs):
    """Run synchronous OpenBB call in thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


async def _get_fred_series(series_id: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch FRED series data."""
    try:
        from openbb import obb
        result = await _run_obb_sync(obb.economy.fred_series, symbol=series_id, start_date=start_date, end_date=end_date)
        df = result.to_df()
        if not df.empty:
            df = df.sort_values("date")
            df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        raise Exception(f"Failed to fetch FRED series: {str(e)}")


async def _get_economy_indicator(
    symbol: str,
    country: str = "united_states",
    start_date: str = "",
    end_date: str = "",
    frequency: str = "monthly",
    transform: str = "yoy",
) -> pd.DataFrame:
    """Fetch economy indicator."""
    try:
        from openbb import obb
        result = await _run_obb_sync(
            obb.economy.indicators,
            symbol=symbol,
            country=country,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            transform=transform,
        )
        df = result.to_df()
        if not df.empty:
            df = df.sort_values("date")
            df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        raise Exception(f"Failed to fetch economy indicator: {str(e)}")


@router.get("/yield-curve")
@register_widget(
    create_base_widget_config(
        name="US Treasury Yield Curve",
        description="Current and historical yield curve",
        category="Macro",
        endpoint="yield-curve",
        widget_type="chart",
        chart_type="line",
        grid_w=40,
        grid_h=20,
        params=[
            {
                "paramName": "date",
                "value": datetime.now().strftime("%Y-%m-%d"),
                "label": "Date",
                "show": True,
                "type": "date",
            },
            {
                "paramName": "show_history",
                "value": True,
                "label": "Show Historical",
                "show": True,
                "type": "boolean",
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
async def get_yield_curve(
    date: str = Query(datetime.now().strftime("%Y-%m-%d")),
    show_history: bool = Query(True),
    theme: str = Query("dark"),
) -> Any:
    """Get yield curve chart."""
    try:
        from openbb import obb
        result = await _run_obb_sync(obb.fixedincome.government.yield_curve, provider="fred", date=date)
        df = result.to_df()
        
        if df.empty:
            return JSONResponse(content={"error": f"No yield curve data for {date}"}, status_code=404)
        
        # Reset index to get date as column
        if df.index.name == 'date' or 'date' not in df.columns:
            df = df.reset_index()
        
        fig = go.Figure()
        
        # Maturities in order
        maturity_labels = {
            "month_1": "1 Mo",
            "month_3": "3 Mo",
            "month_6": "6 Mo",
            "year_1": "1 Yr",
            "year_2": "2 Yr",
            "year_3": "3 Yr",
            "year_5": "5 Yr",
            "year_7": "7 Yr",
            "year_10": "10 Yr",
            "year_20": "20 Yr",
            "year_30": "30 Yr",
        }
        
        # Filter and sort by maturity_years
        curve_df = df[df['maturity'].isin(maturity_labels.keys())].copy()
        curve_df['maturity_label'] = curve_df['maturity'].map(maturity_labels)
        curve_df['maturity_order'] = curve_df['maturity'].map({
            "month_1": 1, "month_3": 2, "month_6": 3,
            "year_1": 4, "year_2": 5, "year_3": 6,
            "year_5": 7, "year_7": 8, "year_10": 9,
            "year_20": 10, "year_30": 11,
        })
        curve_df = curve_df.sort_values('maturity_order')
        
        x_vals = curve_df['maturity_label'].tolist()
        y_vals = (curve_df['rate'] * 100).tolist()  # Convert to percentage
        
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_vals, mode="lines+markers",
            name=f"Curve ({date})",
            line=dict(color="#2962ff", width=2),
            marker=dict(size=8),
        ))
        
        if show_history:
            # Add curves from 1Y ago, 6M ago, 1M ago
            for days_ago, color, name in [(365, "#ef5350", "1 Year Ago"), (180, "#ff9800", "6 Months Ago"), (30, "#26a69a", "1 Month Ago")]:
                hist_date = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                try:
                    hist_result = await _run_obb_sync(obb.fixedincome.government.yield_curve, provider="fred", date=hist_date)
                    hist_df = hist_result.to_df()
                    if not hist_df.empty:
                        if hist_df.index.name == 'date' or 'date' not in hist_df.columns:
                            hist_df = hist_df.reset_index()
                        
                        hist_curve = hist_df[hist_df['maturity'].isin(maturity_labels.keys())].copy()
                        hist_curve['maturity_order'] = hist_curve['maturity'].map({
                            "month_1": 1, "month_3": 2, "month_6": 3,
                            "year_1": 4, "year_2": 5, "year_3": 6,
                            "year_5": 7, "year_7": 8, "year_10": 9,
                            "year_20": 10, "year_30": 11,
                        })
                        hist_curve = hist_curve.sort_values('maturity_order')
                        
                        hy_vals = (hist_curve['rate'] * 100).tolist()
                        if len(hy_vals) == len(x_vals):
                            fig.add_trace(go.Scatter(
                                x=x_vals, y=hy_vals, mode="lines",
                                name=name, line=dict(color=color, width=1, dash="dash"),
                            ))
                except Exception:
                    pass
        
        is_dark = theme == "dark"
        bg_color = "#131722" if is_dark else "#ffffff"
        text_color = "#d1d4dc" if is_dark else "#131722"
        grid_color = "#2a2e39" if is_dark else "#e1e3e6"
        
        fig.update_layout(
            template="plotly_dark" if is_dark else "plotly_white",
            paper_bgcolor=bg_color,
            plot_bgcolor=bg_color,
            font=dict(color=text_color),
            xaxis=dict(title="Maturity", gridcolor=grid_color),
            yaxis=dict(title="Yield (%)", gridcolor=grid_color),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=50, r=50, t=30, b=50),
            height=500,
        )
        
        return json.loads(fig.to_json())
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/inflation-dashboard")
@register_widget(
    create_base_widget_config(
        name="Inflation Dashboard",
        description="CPI, PCE, PPI with YoY and MoM changes",
        category="Macro",
        endpoint="inflation-dashboard",
        widget_type="chart",
        chart_type="line",
        grid_w=50,
        grid_h=30,
        params=[
            {
                "paramName": "start_date",
                "value": (datetime.now() - timedelta(days=5*365)).strftime("%Y-%m-%d"),
                "label": "Start Date",
                "show": True,
                "type": "date",
            },
            {
                "paramName": "indicators",
                "value": "CPI,PCE,PPI",
                "label": "Indicators",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "transform",
                "value": "yoy",
                "label": "Transform",
                "show": True,
                "type": "text",
                "options": [
                    {"label": "YoY %", "value": "yoy"},
                    {"label": "MoM %", "value": "period"},
                    {"label": "Index", "value": "index"},
                ],
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
async def get_inflation_dashboard(
    start_date: str = Query((datetime.now() - timedelta(days=5*365)).strftime("%Y-%m-%d")),
    indicators: str = Query("CPI,PCE,PPI"),
    transform: str = Query("yoy"),
    theme: str = Query("dark"),
) -> Any:
    """Get inflation indicators chart."""
    end_date = datetime.now().strftime("%Y-%m-%d")
    indicator_list = [i.strip().upper() for i in indicators.split(",")]
    
    fig = make_subplots(
        rows=len(indicator_list),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=indicator_list,
    )
    
    for i, indicator in enumerate(indicator_list):
        row = i + 1
        try:
            if indicator == "CPI":
                df = await _get_economy_indicator("CPI", "united_states", start_date, end_date, "monthly", transform)
                if not df.empty:
                    fig.add_trace(go.Scatter(
                        x=df["date"], y=df["value"], mode="lines",
                        name="CPI", line=dict(color="#2962ff"),
                    ), row=row, col=1)
            elif indicator == "PCE":
                df = await _get_economy_indicator("PCE", "united_states", start_date, end_date, "monthly", transform)
                if not df.empty:
                    fig.add_trace(go.Scatter(
                        x=df["date"], y=df["value"], mode="lines",
                        name="PCE", line=dict(color="#26a69a"),
                    ), row=row, col=1)
            elif indicator == "PPI":
                df = await _get_economy_indicator("PPI", "united_states", start_date, end_date, "monthly", transform)
                if not df.empty:
                    fig.add_trace(go.Scatter(
                        x=df["date"], y=df["value"], mode="lines",
                        name="PPI", line=dict(color="#ff9800"),
                    ), row=row, col=1)
        except Exception:
            pass
    
    is_dark = theme == "dark"
    bg_color = "#131722" if is_dark else "#ffffff"
    text_color = "#d1d4dc" if is_dark else "#131722"
    grid_color = "#2a2e39" if is_dark else "#e1e3e6"
    
    fig.update_layout(
        template="plotly_dark" if is_dark else "plotly_white",
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color, size=10),
        xaxis=dict(gridcolor=grid_color),
        yaxis=dict(title=f"Change ({transform.upper()})", gridcolor=grid_color),
        showlegend=False,
        margin=dict(l=50, r=50, t=50, b=50),
        height=800,
    )
    
    return json.loads(fig.to_json())


@router.get("/fed-balance-sheet")
@register_widget(
    create_base_widget_config(
        name="Fed Balance Sheet",
        description="Federal Reserve assets and liabilities",
        category="Macro",
        endpoint="fed-balance-sheet",
        widget_type="chart",
        chart_type="bar",
        grid_w=50,
        grid_h=25,
        params=[
            {
                "paramName": "start_date",
                "value": (datetime.now() - timedelta(days=10*365)).strftime("%Y-%m-%d"),
                "label": "Start Date",
                "show": True,
                "type": "date",
            },
            {
                "paramName": "view",
                "value": "stacked",
                "label": "View",
                "show": True,
                "type": "text",
                "options": [
                    {"label": "Stacked", "value": "stacked"},
                    {"label": "Assets Only", "value": "assets"},
                    {"label": "Liabilities Only", "value": "liabilities"},
                    {"label": "Net Liquidity", "value": "net_liquidity"},
                ],
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
async def get_fed_balance_sheet(
    start_date: str = Query((datetime.now() - timedelta(days=10*365)).strftime("%Y-%m-%d")),
    view: str = Query("stacked"),
    theme: str = Query("dark"),
) -> Any:
    """Get Fed balance sheet chart."""
    try:
        from openbb import obb
        result = await _run_obb_sync(
            obb.economy.central_bank_holdings,
            provider="federal_reserve",
            start_date=start_date,
            holding_type="all_treasury",
            monthly=True,
        )
        df = result.to_df()
        
        if df.empty:
            return JSONResponse(content={"error": "No Fed balance sheet data"}, status_code=404)
        
        fig = go.Figure()
        
        if view == "net_liquidity":
            # Net liquidity = WALCL - RRP - TGA
            if "WALCL" in df.columns and "RRP" in df.columns and "TGA" in df.columns:
                df["net_liquidity"] = df["WALCL"] - df["RRP"] - df["TGA"]
                fig.add_trace(go.Scatter(
                    x=df["date"], y=df["net_liquidity"], mode="lines",
                    name="Net Liquidity", line=dict(color="#26a69a", width=2),
                ))
                fig.add_trace(go.Scatter(
                    x=df["date"], y=df["WALCL"], mode="lines",
                    name="WALCL (Assets)", line=dict(color="#2962ff", width=1, dash="dash"),
                ))
                fig.add_trace(go.Scatter(
                    x=df["date"], y=df["RRP"] + df["TGA"], mode="lines",
                    name="RRP + TGA (Liabilities)", line=dict(color="#ef5350", width=1, dash="dash"),
                ))
        else:
            # Stacked area chart
            numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
            for col in numeric_cols:
                fig.add_trace(go.Scatter(
                    x=df["date"], y=df[col], mode="lines",
                    name=col, stackgroup="one",
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
            xaxis=dict(gridcolor=grid_color),
            yaxis=dict(title="Billions USD", gridcolor=grid_color),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=50, r=50, t=30, b=50),
            height=600,
        )
        
        return json.loads(fig.to_json())
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/employment-dashboard")
@register_widget(
    create_base_widget_config(
        name="Employment Dashboard",
        description="Nonfarm payrolls, unemployment rate, labor force participation",
        category="Macro",
        endpoint="employment-dashboard",
        widget_type="chart",
        chart_type="line",
        grid_w=50,
        grid_h=30,
        params=[
            {
                "paramName": "start_date",
                "value": (datetime.now() - timedelta(days=5*365)).strftime("%Y-%m-%d"),
                "label": "Start Date",
                "show": True,
                "type": "date",
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
async def get_employment_dashboard(
    start_date: str = Query((datetime.now() - timedelta(days=5*365)).strftime("%Y-%m-%d")),
    theme: str = Query("dark"),
) -> Any:
    """Get employment indicators chart."""
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=["Nonfarm Payrolls (Monthly Change)", "Unemployment Rate (%)", "Labor Force Participation (%)"],
    )
    
    try:
        # Nonfarm payrolls
        df = await _get_economy_indicator("PAYEMS", "united_states", start_date, end_date, "monthly", "period")
        if not df.empty:
            fig.add_trace(go.Bar(
                x=df["date"], y=df["value"], name="NFP",
                marker_color=df["value"].apply(lambda x: "#26a69a" if x >= 0 else "#ef5350"),
            ), row=1, col=1)
        
        # Unemployment rate
        df = await _get_economy_indicator("UNRATE", "united_states", start_date, end_date, "monthly", "index")
        if not df.empty:
            fig.add_trace(go.Scatter(
                x=df["date"], y=df["value"], mode="lines",
                name="Unemployment", line=dict(color="#ef5350", width=2),
            ), row=2, col=1)
        
        # Labor force participation
        df = await _get_economy_indicator("CIVPART", "united_states", start_date, end_date, "monthly", "index")
        if not df.empty:
            fig.add_trace(go.Scatter(
                x=df["date"], y=df["value"], mode="lines",
                name="Participation", line=dict(color="#2962ff", width=2),
            ), row=3, col=1)
    except Exception:
        pass
    
    is_dark = theme == "dark"
    bg_color = "#131722" if is_dark else "#ffffff"
    text_color = "#d1d4dc" if is_dark else "#131722"
    grid_color = "#2a2e39" if is_dark else "#e1e3e6"
    
    fig.update_layout(
        template="plotly_dark" if is_dark else "plotly_white",
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color, size=10),
        xaxis=dict(gridcolor=grid_color),
        yaxis=dict(gridcolor=grid_color),
        showlegend=False,
        margin=dict(l=50, r=50, t=50, b=50),
        height=800,
    )
    
    return json.loads(fig.to_json())


@router.get("/macro-table")
@register_widget(
    create_base_widget_config(
        name="Macro Indicators Table",
        description="Latest values for key macro indicators",
        category="Macro",
        endpoint="macro-table",
        widget_type="table",
        grid_w=30,
        grid_h=25,
        params=[
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
async def get_macro_table(
    theme: str = Query("dark"),
) -> Any:
    """Get macro indicators summary table."""
    indicators = [
        ("GDP", "GDP", "quarter", "index"),
        ("CPI YoY", "CPI", "monthly", "yoy"),
        ("Core CPI YoY", "CPILFESL", "monthly", "yoy"),
        ("PCE YoY", "PCEPI", "monthly", "yoy"),
        ("Core PCE YoY", "PCEPILFE", "monthly", "yoy"),
        ("Unemployment", "UNRATE", "monthly", "index"),
        ("NFP", "PAYEMS", "monthly", "period"),
        ("Fed Funds", "FEDFUNDS", "monthly", "index"),
        ("10Y Treasury", "GS10", "monthly", "index"),
        ("2Y Treasury", "GS2", "monthly", "index"),
        ("DXY", "DTWEXBGS", "monthly", "index"),
        ("VIX", "VIXCLS", "monthly", "index"),
    ]
    
    rows = []
    for name, symbol, freq, transform in indicators:
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            df = await _get_economy_indicator(symbol, "united_states", start_date, end_date, freq, transform)
            if not df.empty:
                latest = df.iloc[-1]
                prev = df.iloc[-2] if len(df) > 1 else None
                change = latest["value"] - prev["value"] if prev is not None else 0
                rows.append({
                    "indicator": name,
                    "value": f"{latest['value']:,.2f}",
                    "change": f"{change:+,.2f}",
                    "date": latest["date"].strftime("%Y-%m-%d") if hasattr(latest["date"], "strftime") else str(latest["date"]),
                })
        except Exception:
            rows.append({
                "indicator": name,
                "value": "N/A",
                "change": "N/A",
                "date": "N/A",
            })
    
    return WidgetResponse.table(rows, columns_defs=[
        {"field": "indicator", "headerName": "Indicator", "cellDataType": "text"},
        {"field": "value", "headerName": "Value", "cellDataType": "text"},
        {"field": "change", "headerName": "Change", "cellDataType": "text", "renderFn": "greenRed"},
        {"field": "date", "headerName": "As Of", "cellDataType": "text"},
    ])