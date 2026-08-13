from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from sqlmodel import SQLModel

from app.core.config import settings


engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "development",
    poolclass=NullPool if settings.app_env == "development" else None,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))


async def close_db() -> None:
    await engine.dispose()