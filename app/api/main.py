from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine

from app.api.health import health_router
from app.api.notes.router import NotesAPIImpl
from app.dependencies import create_container
from app.models import Base
from app.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings: Settings = settings if settings is not None else Settings()
    container = create_container(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        try:
            if not settings.use_in_memory_db:
                engine = await container.get(AsyncEngine)
                async with engine.begin() as connection:
                    await connection.run_sync(Base.metadata.create_all)
            yield
        finally:
            await container.close()

    app = FastAPI(lifespan=lifespan)
    setup_dishka(container=container, app=app)
    app.include_router(health_router, prefix="/health")
    app.include_router(NotesAPIImpl().router, prefix="/notes/v1")

    @app.get("/")
    def get_root() -> dict:
        return {"message": "Hello there!", "status": "ok"}

    return app


app = create_app()
