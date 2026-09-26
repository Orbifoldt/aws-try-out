from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def get_root() -> dict:
    return {"message": "Hello there!", "status": "ok"}