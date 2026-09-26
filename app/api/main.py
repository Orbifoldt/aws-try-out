from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import health_router
from app.api.notes.router import NotesAPIImpl
from app.database import engine
from app.models import Base
from app.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        if not settings.use_in_memory_db:
            if engine is None:
                raise RuntimeError("Database engine is not configured")
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)
        yield
    finally:
        if engine is not None:
            await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(health_router, prefix="/health")
app.include_router(NotesAPIImpl().router, prefix="/notes/v1")


@app.get("/")
def get_root() -> dict:
    return {"message": "Hello there!", "status": "ok"}
