from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from app.api.v1 import equity, news, ai
from app.core.config import settings
from app.core.database import close_db, init_db
from app.services.scheduler import shutdown_scheduler, start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    redis = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    await start_scheduler()

    yield

    await shutdown_scheduler()
    await close_db()
    await redis.close()


app = FastAPI(
    title="OpenBB Custom API",
    description="Financial data API with OpenBB, PostgreSQL + pgvector, and semantic search",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(equity.router)
app.include_router(news.router)
app.include_router(ai.router)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/openapi.json")
async def get_openapi_spec() -> dict:
    return app.openapi()