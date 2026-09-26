.PHONY: app app-generate notes-app

app: app-generate
	uv run uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000

app-generate:
	uv run fastapi-codegen --input app/api/notes/notes-v1.yaml --output app/api/notes/generated --template-dir templates --output-model-type pydantic_v2.BaseModel --python-version 3.14 --use-annotated


