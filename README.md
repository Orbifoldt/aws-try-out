# aws-try-out

This is me learning AWS, using AI as a teacher (let's see how that actually works out). All code is written by me. 
Plan: use free AWS tier, create simple app with DB and storage, then add more bells and whistles. Use IAC for everything.

## Run locally
Start postgres DB:
```sh
make db-up
make db-logs
```
Start the API with
```sh
make app
```
then run `make notes-http` to create, list, and fetch a note.

Settings are read from the environment and `.env` when the app is built (pydantic settings).

## Dependency injection

We use [Dishka](https://dishka.readthedocs.io/en/stable/integrations/fastapi.html), which allows us to swap out postgres db backed storage with just in memory storage of notes. Also,
later we could do things like request-scoped dependencies (like auth etc)

## Contract-first
We first define the contract (OpenAI spec), and then generate code based on that.

1. E.g., edit `app/api/notes/notes-v1.yaml`
2. Then run `make app-generate` to regenerate models and `register_routes()`.
3. Supply every handler in the handwritten router. Missing or invalid signature will cause typechecking to fail.