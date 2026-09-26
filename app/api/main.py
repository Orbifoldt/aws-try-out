from fastapi import FastAPI

from app.api.health import health_router
from app.api.notes.router import NotesAPIImpl

app = FastAPI()
app.include_router(health_router, prefix="/health")
app.include_router(NotesAPIImpl().router, prefix="/notes/v1")


@app.get("/")
def get_root() -> dict:
    return {"message": "Hello there!", "status": "ok"}