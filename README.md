# aws-try-out

This is me learning AWS, using AI as a teacher (let's see how that actually works out). All code is written by me. Plan: use free AWS tier, create simple app with DB and storage, then add more bells and whistles. Use IAC for everything.

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
