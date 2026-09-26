from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.settings import get_settings


class NullSession:
    """Per-request marker used when the in-memory store is enabled."""


settings = get_settings()
engine: AsyncEngine | None = None
session_factory: async_sessionmaker[AsyncSession] | None = None

if not settings.use_in_memory_db:
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession | NullSession]:
    if settings.use_in_memory_db:
        yield NullSession()
        return

    if session_factory is None:
        raise RuntimeError("Database sessions are not configured")

    async with session_factory() as session:
        yield session
