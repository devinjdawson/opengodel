from contextlib import asynccontextmanager
import re

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.openai import OpenAIIntegration
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from app.api.v1 import equity, news, ai, widgets_equity, widgets_macro, widgets_news, widgets_options, widgets_portfolio, widgets_godel, widgets_market, widgets_sentiment
from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.widget_registry import get_widgets, get_templates, set_templates, load_templates_from_file
from app.services.scheduler import shutdown_scheduler, start_scheduler


_langfuse_client = None


def get_langfuse():
    global _langfuse_client
    if _langfuse_client is None:
        if settings.langfuse_public_key and settings.langfuse_secret_key:
            from langfuse import Langfuse
            _langfuse_client = Langfuse(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                base_url=settings.langfuse_base_url,
            )
    return _langfuse_client


def _scrub_sensitive_data(value: str) -> str:
    if not isinstance(value, str):
        return value
    patterns = [
        re.compile(r'sk-[a-zA-Z0-9]{20,}'),
        re.compile(r'Bearer\s+[a-zA-Z0-9\-_\.]+'),
        re.compile(r'"openai_api_key"\s*:\s*"[^"]+"'),
        re.compile(r'"inference_api_key"\s*:\s*"[^"]+"'),
        re.compile(r'"embedding_api_key"\s*:\s*"[^"]+"'),
        re.compile(r'"marketaux_api_key"\s*:\s*"[^"]+"'),
        re.compile(r'"openbb_api_key"\s*:\s*"[^"]+"'),
        re.compile(r'"openbb_pat"\s*:\s*"[^"]+"'),
    ]
    for pattern in patterns:
        value = pattern.sub('[REDACTED]', value)
    return value


def before_send(event, hint):
    if event.get('request') and event['request'].get('data'):
        event['request']['data'] = _scrub_sensitive_data(event['request']['data'])
    if event.get('exception') and event['exception'].get('values'):
        for exc in event['exception']['values']:
            if exc.get('value'):
                exc['value'] = _scrub_sensitive_data(exc['value'])
            if exc.get('type'):
                exc['type'] = _scrub_sensitive_data(exc['type'])
    return event


# if settings.sentry_dsn:
#     sentry_sdk.init(
#         dsn=settings.sentry_dsn,
#         environment=settings.sentry_environment,
#         release=settings.sentry_release,
#         send_default_pii=False,
#         integrations=[
#             FastApiIntegration(),
#             LoggingIntegration(),
#             OpenAIIntegration(),
#         ],
#         traces_sample_rate=1.0,
#         profile_session_sample_rate=1.0,
#         profile_lifecycle="trace",
#         enable_logs=True,
#         before_send=before_send,
#     )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    redis = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    # Load templates
    templates = load_templates_from_file()
    set_templates(templates)

    # Assign Marketaux API key to OpenBB credentials in-memory (for container support)
    if settings.marketaux_api_key:
        from openbb import obb
        if not obb.user.credentials.marketaux_api_key:
            obb.user.credentials.marketaux_api_key = settings.marketaux_api_key

    await start_scheduler()

    yield

    await shutdown_scheduler()
    await close_db()
    await redis.close()

    langfuse = get_langfuse()
    if langfuse:
        langfuse.shutdown()


app = FastAPI(
    title="OpenBB Custom API",
    description="Financial data API with OpenBB, PostgreSQL + pgvector, semantic search, and OpenBB Workspace compatible widgets",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core API routers
app.include_router(equity.router)
app.include_router(news.router)
app.include_router(ai.router)

# OpenBB Workspace compatible widget routers
app.include_router(widgets_equity.router)
app.include_router(widgets_macro.router)
app.include_router(widgets_news.router)
app.include_router(widgets_options.router)
app.include_router(widgets_portfolio.router)
app.include_router(widgets_godel.router)
app.include_router(widgets_market.router)
app.include_router(widgets_sentiment.router)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/cache/stats")
async def cache_stats_endpoint() -> dict:
    from app.services.cache_service import cache_stats

    return cache_stats()


@app.post("/cache/clear")
async def cache_clear_endpoint() -> dict:
    from app.services.cache_service import clear_cache

    cleared = clear_cache()
    return {"cleared": cleared}


@app.get("/healthz")
async def healthz_check() -> dict:
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/test-json-response")
async def test_json_response():
    from fastapi.responses import JSONResponse
    return JSONResponse(content={"test": "value", "data": [1, 2, 3]})


@app.get("/test-chart-data")
async def test_chart_data():
    return {
        "type": "chart",
        "data": {
            "chart": {
                "type": "bar",
                "data": [
                    {
                        "type": "bar",
                        "x": ["2023-01-01", "2023-02-01"],
                        "y": [1.0, 2.0],
                        "name": "Dividend",
                        "marker": {"color": "#2962ff"}
                    }
                ],
                "layout": {
                    "title": "Test Chart",
                    "template": "plotly_white",
                    "paper_bgcolor": "#ffffff",
                    "plot_bgcolor": "#ffffff",
                    "font": {"color": "#131722"},
                    "xaxis": {"title": "Date", "gridcolor": "#e1e3e6"},
                    "yaxis": {"title": "Dividend ($)", "gridcolor": "#e1e3e6"},
                    "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
                    "margin": {"l": 50, "r": 50, "t": 30, "b": 50},
                    "height": 500,
                }
            }
        }
    }


@app.get("/openapi.json")
async def get_openapi_spec() -> dict:
    return app.openapi()


# OpenBB Workspace compatibility endpoints
@app.get("/widgets.json")
async def get_widgets_json():
    """OpenBB Workspace widget registry endpoint."""
    widgets = get_widgets()
    widget_list = list(widgets.values())
    print(f"DEBUG: Returning {len(widget_list)} widgets")
    print(f"DEBUG: Type is {type(widget_list)}")
    if widget_list:
        print(f"DEBUG: First widget keys: {widget_list[0].keys() if widget_list else []}")
    return widget_list


@app.get("/templates.json")
async def get_templates_json():
    """OpenBB Workspace templates endpoint."""
    templates = get_templates()
    # Return as array
    return list(templates.values()) if isinstance(templates, dict) else templates