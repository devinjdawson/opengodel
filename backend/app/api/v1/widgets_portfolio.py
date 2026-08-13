from datetime import datetime, timedelta
from typing import Any, Optional
import pandas as pd
import numpy as np
from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.config import settings
from app.core.database import get_db
from app.core.widget_registry import register_widget, create_base_widget_config, WidgetResponse
from app.db.models import StockCandle

router = APIRouter(prefix="/widgets/portfolio", tags=["portfolio widgets"])

from openbb import obb


@router.get("/performance")
@register_widget(
    create_base_widget_config(
        name="Portfolio Performance",
        description="Portfolio returns, drawdown, and risk metrics",
        category="Portfolio",
        endpoint="performance",
        widget_type="chart",
        chart_type="line",
        grid_w=50,
        grid_h=25,
        params=[
            {
                "paramName": "symbols",
                "value": "AAPL,GOOGL,MSFT",
                "label": "Symbols (comma-separated)",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "weights",
                "value": "0.33,0.33,0.34",
                "label": "Weights (comma-separated, sum=1)",
                "show": True,
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
                "paramName": "benchmark",
                "value": "SPY",
                "label": "Benchmark",
                "show": True,
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
async def get_portfolio_performance(
    symbols: str = Query("AAPL,GOOGL,MSFT"),
    weights: str = Query("0.33,0.33,0.34"),
    start_date: str = Query((datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")),
    benchmark: str = Query("SPY"),
    theme: str = Query("dark"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Calculate portfolio performance metrics."""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        weight_list = [float(w.strip()) for w in weights.split(",")]
        
        if len(symbol_list) != len(weight_list):
            return JSONResponse(content={"error": "Number of symbols must match number of weights"}, status_code=400)
        
        if abs(sum(weight_list) - 1.0) > 0.01:
            return JSONResponse(content={"error": "Weights must sum to 1.0"}, status_code=400)
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        # Fetch data for all symbols + benchmark
        all_symbols = symbol_list + [benchmark.upper()]
        price_data = {}
        
        for sym in all_symbols:
            stmt = select(StockCandle).where(
                StockCandle.symbol == sym,
                StockCandle.timestamp >= start_date,
                StockCandle.timestamp <= end_date,
            ).order_by(StockCandle.timestamp)
            
            result = await db.execute(stmt)
            candles = result.scalars().all()
            
            if candles:
                df = pd.DataFrame([{
                    "date": c.timestamp,
                    "close": c.close,
                } for c in candles])
                df = df.set_index("date")["close"]
                price_data[sym] = df
        
        if len(price_data) < len(all_symbols):
            missing = set(all_symbols) - set(price_data.keys())
            return JSONResponse(content={"error": f"Missing data for: {', '.join(missing)}"}, status_code=404)
        
        # Align dates
        price_df = pd.DataFrame(price_data)
        price_df = price_df.dropna()
        
        if price_df.empty:
            return JSONResponse(content={"error": "No overlapping data"}, status_code=404)
        
        # Calculate returns
        returns = price_df.pct_change().dropna()
        
        # Portfolio returns
        portfolio_returns = (returns[symbol_list] * weight_list).sum(axis=1)
        portfolio_cumulative = (1 + portfolio_returns).cumprod()
        benchmark_returns = returns[benchmark.upper()]
        benchmark_cumulative = (1 + benchmark_returns).cumprod()
        
        # Metrics
        total_return = portfolio_cumulative.iloc[-1] - 1
        benchmark_total_return = benchmark_cumulative.iloc[-1] - 1
        
        # Annualized metrics
        trading_days = len(portfolio_returns)
        years = trading_days / 252
        ann_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        ann_vol = portfolio_returns.std() * np.sqrt(252)
        sharpe = ann_return / ann_vol if ann_vol > 0 else 0
        
        # Max drawdown
        cumulative = portfolio_cumulative
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_dd = drawdown.min()
        
        # Beta
        covariance = portfolio_returns.cov(benchmark_returns)
        benchmark_var = benchmark_returns.var()
        beta = covariance / benchmark_var if benchmark_var > 0 else 1
        
        # Alpha
        ann_bench_return = (1 + benchmark_total_return) ** (1 / years) - 1 if years > 0 else 0
        rf = 0.04  # Risk-free rate assumption
        alpha = ann_return - (rf + beta * (ann_bench_return - rf))
        
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=["Cumulative Returns", "Drawdown", "Rolling 30D Volatility", "Monthly Returns Heatmap"],
            specs=[[{"colspan": 2}, None], [{"type": "xy"}, {"type": "xy"}]],
        )
        
        # Cumulative returns
        fig.add_trace(go.Scatter(
            x=portfolio_cumulative.index, y=portfolio_cumulative.values,
            mode="lines", name="Portfolio", line=dict(color="#2962ff", width=2),
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=benchmark_cumulative.index, y=benchmark_cumulative.values,
            mode="lines", name=benchmark.upper(), line=dict(color="#78909c", width=1, dash="dash"),
        ), row=1, col=1)
        
        # Drawdown
        fig.add_trace(go.Scatter(
            x=drawdown.index, y=drawdown.values * 100,
            mode="lines", name="Drawdown", line=dict(color="#ef5350", width=1),
            fill="tozeroy", fillcolor="rgba(239,83,80,0.2)",
        ), row=2, col=1)
        
        # Rolling volatility
        rolling_vol = portfolio_returns.rolling(30).std() * np.sqrt(252) * 100
        fig.add_trace(go.Scatter(
            x=rolling_vol.index, y=rolling_vol.values,
            mode="lines", name="30D Vol", line=dict(color="#ff9800", width=1),
        ), row=2, col=2)
        
        # Monthly returns heatmap
        monthly = portfolio_cumulative.resample("M").last().pct_change().dropna()
        monthly.index = monthly.index.to_period("M")
        monthly_pivot = monthly.groupby([monthly.index.year, monthly.index.month]).first()
        
        if len(monthly_pivot) > 0:
            years = sorted(monthly_pivot.index.get_level_values(0).unique())
            months = list(range(1, 13))
            z = []
            text = []
            for y in years:
                row_z = []
                row_text = []
                for m in months:
                    if (y, m) in monthly_pivot.index:
                        val = monthly_pivot.loc[(y, m)] * 100
                        row_z.append(val)
                        row_text.append(f"{val:.2f}%")
                    else:
                        row_z.append(None)
                        row_text.append("")
                z.append(row_z)
                text.append(row_text)
            
            fig.add_trace(go.Heatmap(
                z=z,
                x=[datetime(2000, m, 1).strftime("%b") for m in months],
                y=[str(y) for y in years],
                colorscale="RdYlGn",
                zmid=0,
                text=text,
                texttemplate="%{text}",
                showscale=True,
            ), row=2, col=2)
        
        is_dark = theme == "dark"
        bg_color = "#131722" if is_dark else "#ffffff"
        text_color = "#d1d4dc" if is_dark else "#131722"
        grid_color = "#2a2e39" if is_dark else "#e1e3e6"
        
        fig.update_layout(
            template="plotly_dark" if is_dark else "plotly_white",
            paper_bgcolor=bg_color,
            plot_bgcolor=bg_color,
            font=dict(color=text_color, size=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=50, r=50, t=50, b=50),
            height=700,
        )
        
        # Add metrics as annotations
        metrics_text = (
            f"Total Return: {total_return:.2%} | "
            f"Ann. Return: {ann_return:.2%} | "
            f"Ann. Vol: {ann_vol:.2%} | "
            f"Sharpe: {sharpe:.2f} | "
            f"Max DD: {max_dd:.2%} | "
            f"Alpha: {alpha:.2%} | "
            f"Beta: {beta:.2f}"
        )
        
        fig.add_annotation(
            text=metrics_text,
            xref="paper", yref="paper",
            x=0.5, y=1.08,
            showarrow=False,
            font=dict(size=11, color=text_color),
            align="center",
        )
        
        return fig.to_dict()
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/allocation")
@register_widget(
    create_base_widget_config(
        name="Portfolio Allocation",
        description="Current portfolio allocation by symbol/sector",
        category="Portfolio",
        endpoint="allocation",
        widget_type="chart",
        chart_type="pie",
        grid_w=30,
        grid_h=20,
        params=[
            {
                "paramName": "symbols",
                "value": "AAPL,GOOGL,MSFT",
                "label": "Symbols",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "weights",
                "value": "0.33,0.33,0.34",
                "label": "Weights",
                "show": True,
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
async def get_portfolio_allocation(
    symbols: str = Query("AAPL,GOOGL,MSFT"),
    weights: str = Query("0.33,0.33,0.34"),
    theme: str = Query("dark"),
) -> Any:
    """Portfolio allocation pie chart."""
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    weight_list = [float(w.strip()) for w in weights.split(",")]
    
    if len(symbol_list) != len(weight_list):
        return JSONResponse(content={"error": "Symbols and weights must match"}, status_code=400)
    
    import plotly.graph_objects as go
    
    fig = go.Figure(data=[go.Pie(
        labels=symbol_list,
        values=weight_list,
        hole=0.4,
        textinfo="label+percent",
        marker=dict(colors=["#2962ff", "#26a69a", "#ff9800", "#9c27b0", "#ef5350", "#78909c", "#00bcd4", "#ff5722"][:len(symbol_list)]),
    )])
    
    is_dark = theme == "dark"
    bg_color = "#131722" if is_dark else "#ffffff"
    text_color = "#d1d4dc" if is_dark else "#131722"
    
    fig.update_layout(
        template="plotly_dark" if is_dark else "plotly_white",
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color),
        title=dict(text="Portfolio Allocation", x=0.5),
        margin=dict(l=20, r=20, t=50, b=20),
        height=400,
    )
    
    return fig.to_dict()


@router.get("/correlation-matrix")
@register_widget(
    create_base_widget_config(
        name="Correlation Matrix",
        description="Asset correlation heatmap",
        category="Portfolio",
        endpoint="correlation-matrix",
        widget_type="chart",
        chart_type="heatmap",
        grid_w=35,
        grid_h=25,
        params=[
            {
                "paramName": "symbols",
                "value": "AAPL,GOOGL,MSFT,AMZN,META,NVDA",
                "label": "Symbols",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "start_date",
                "value": (datetime.now() - timedelta(days=252)).strftime("%Y-%m-%d"),
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
async def get_correlation_matrix(
    symbols: str = Query("AAPL,GOOGL,MSFT,AMZN,META,NVDA"),
    start_date: str = Query((datetime.now() - timedelta(days=252)).strftime("%Y-%m-%d")),
    theme: str = Query("dark"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Correlation matrix heatmap."""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        price_data = {}
        for sym in symbol_list:
            stmt = select(StockCandle).where(
                StockCandle.symbol == sym,
                StockCandle.timestamp >= start_date,
                StockCandle.timestamp <= end_date,
            ).order_by(StockCandle.timestamp)
            
            result = await db.execute(stmt)
            candles = result.scalars().all()
            
            if candles:
                df = pd.DataFrame([{"date": c.timestamp, "close": c.close} for c in candles])
                df = df.set_index("date")["close"]
                price_data[sym] = df
        
        if len(price_data) < 2:
            return JSONResponse(content={"error": "Need at least 2 symbols with data"}, status_code=400)
        
        price_df = pd.DataFrame(price_data).dropna()
        returns = price_df.pct_change().dropna()
        corr = returns.corr()
        
        import plotly.graph_objects as go
        
        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.index,
            colorscale="RdBu",
            zmid=0,
            zmin=-1,
            zmax=1,
            text=corr.values.round(2),
            texttemplate="%{text}",
            showscale=True,
        ))
        
        is_dark = theme == "dark"
        bg_color = "#131722" if is_dark else "#ffffff"
        text_color = "#d1d4dc" if is_dark else "#131722"
        
        fig.update_layout(
            template="plotly_dark" if is_dark else "plotly_white",
            paper_bgcolor=bg_color,
            plot_bgcolor=bg_color,
            font=dict(color=text_color),
            title=dict(text="Asset Correlation Matrix", x=0.5),
            margin=dict(l=50, r=50, t=50, b=50),
            height=600,
        )
        
        return fig.to_dict()
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/risk-metrics")
@register_widget(
    create_base_widget_config(
        name="Risk Metrics Table",
        description="VaR, CVaR, Beta, and other risk metrics",
        category="Portfolio",
        endpoint="risk-metrics",
        widget_type="table",
        grid_w=35,
        grid_h=20,
        params=[
            {
                "paramName": "symbols",
                "value": "AAPL,GOOGL,MSFT",
                "label": "Symbols",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "weights",
                "value": "0.33,0.33,0.34",
                "label": "Weights",
                "show": True,
                "type": "text",
            },
            {
                "paramName": "confidence",
                "value": 0.95,
                "label": "Confidence Level",
                "show": True,
                "type": "number",
            },
        ],
    )
)
async def get_risk_metrics(
    symbols: str = Query("AAPL,GOOGL,MSFT"),
    weights: str = Query("0.33,0.33,0.34"),
    confidence: float = Query(0.95),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Risk metrics table."""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        weight_list = [float(w.strip()) for w in weights.split(",")]
        
        if len(symbol_list) != len(weight_list):
            return JSONResponse(content={"error": "Symbols and weights must match"}, status_code=400)
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=252)).strftime("%Y-%m-%d")
        
        price_data = {}
        for sym in symbol_list:
            stmt = select(StockCandle).where(
                StockCandle.symbol == sym,
                StockCandle.timestamp >= start_date,
                StockCandle.timestamp <= end_date,
            ).order_by(StockCandle.timestamp)
            
            result = await db.execute(stmt)
            candles = result.scalars().all()
            
            if candles:
                df = pd.DataFrame([{"date": c.timestamp, "close": c.close} for c in candles])
                df = df.set_index("date")["close"]
                price_data[sym] = df
        
        if len(price_data) < len(symbol_list):
            return JSONResponse(content={"error": "Missing data for some symbols"}, status_code=404)
        
        price_df = pd.DataFrame(price_data).dropna()
        returns = price_df.pct_change().dropna()
        
        # Portfolio returns
        portfolio_returns = (returns * weight_list).sum(axis=1)
        
        # VaR and CVaR
        var = np.percentile(portfolio_returns, (1 - confidence) * 100)
        cvar = portfolio_returns[portfolio_returns <= var].mean()
        
        # Volatility
        daily_vol = portfolio_returns.std()
        ann_vol = daily_vol * np.sqrt(252)
        
        # Skewness and Kurtosis
        skew = portfolio_returns.skew()
        kurt = portfolio_returns.kurtosis()
        
        # Max drawdown
        cum = (1 + portfolio_returns).cumprod()
        running_max = cum.expanding().max()
        dd = (cum - running_max) / running_max
        max_dd = dd.min()
        
        # Downside deviation
        downside = portfolio_returns[portfolio_returns < 0]
        downside_dev = downside.std() * np.sqrt(252) if len(downside) > 0 else 0
        
        # Sortino ratio (assuming 4% risk-free)
        rf_daily = 0.04 / 252
        excess = portfolio_returns - rf_daily
        sortino = excess.mean() / downside_dev * np.sqrt(252) if downside_dev > 0 else 0
        
        rows = [
            {"metric": "Daily VaR (95%)", "value": f"{var:.4%}"},
            {"metric": "Daily CVaR (95%)", "value": f"{cvar:.4%}"},
            {"metric": "Annualized Volatility", "value": f"{ann_vol:.2%}"},
            {"metric": "Max Drawdown", "value": f"{max_dd:.2%}"},
            {"metric": "Skewness", "value": f"{skew:.4f}"},
            {"metric": "Excess Kurtosis", "value": f"{kurt:.4f}"},
            {"metric": "Downside Deviation (Ann.)", "value": f"{downside_dev:.2%}"},
            {"metric": "Sortino Ratio", "value": f"{sortino:.4f}"},
        ]
        
        return WidgetResponse.table(rows, columns_defs=[
            {"field": "metric", "headerName": "Metric", "cellDataType": "text"},
            {"field": "value", "headerName": "Value", "cellDataType": "text"},
        ])
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)