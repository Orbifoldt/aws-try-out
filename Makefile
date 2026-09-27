.PHONY: app app-generate check notes-app db-up db-down db-logs notes-http

app: app-generate
	uv run uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

app-generate:
	uv run fastapi-codegen --input app/api/notes/notes-v1.yaml --output app/api/notes/generated --template-dir templates --output-model-type pydantic_v2.BaseModel --python-version 3.14 --use-annotated

check:
	#uv run python -m unittest discover -s tests -v
	uv run ruff check .
	uv run ty check

# Local PostgreSQL
db-up:
	docker compose up -d postgres

db-down:
	docker compose down

db-logs:
	docker compose logs -f postgres

# Select with HTTP_ENV=local or HTTP_ENV=deployed.
HTTP_ENV ?= local

# Runs the requests in notes.http in order
notes-http:
	MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' docker run --rm -v "$(CURDIR):/workdir" jetbrains/intellij-http-client --env-file http-client.env.json --env $(HTTP_ENV) notes.http
