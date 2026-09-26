from app.health import health_router
from fastapi import FastAPI

app = FastAPI()
app.include_router(health_router, prefix="/health")


@app.get("/")
def get_root() -> dict:
    return {"message": "Hello there!", "status": "ok"}