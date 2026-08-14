from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from app.api.v1 import equity, news, ai, widgets_equity, widgets_macro, widgets_news, widgets_options, widgets_portfolio, widgets_og, widgets_market
from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.widget_registry import get_widgets, get_templates, set_templates, load_templates_from_file
from app.services.scheduler import shutdown_scheduler, start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    redis = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    # Load templates
    templates = load_templates_from_file()
    set_templates(templates)

    await start_scheduler()

    yield

    await shutdown_scheduler()
    await close_db()
    await redis.close()


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
app.include_router(widgets_og.router)
app.include_router(widgets_market.router)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "healthy", "version": "0.1.0"}


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