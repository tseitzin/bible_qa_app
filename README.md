# Bible Q&A Monorepo

This repository contains a FastAPI backend and a Vue 3 + Vite frontend for an AI-powered Bible Question & Answer application.

## Components

- `backend/` – FastAPI application providing REST endpoints
- `frontend/` – Vue 3 SPA consuming the API
- `docker-compose.yml` – Orchestrates Postgres, backend, and frontend services

## Prerequisites

- Python 3.11+
- Node.js 20+
- npm 10+
- Docker & Docker Compose (for containerized setup)

## Quick Start (Local Without Docker)

### 1. Clone & enter repo

```bash
git clone <repo-url>
cd bible_qa_app
```

### 2. Set environment variables

Create `.env` in repo root (already present). At minimum set:

```
OPENAI_API_KEY=sk-...your-key...
```

Backend expects `OPENAI_API_KEY` and optional `ALLOWED_ORIGINS` (defaults to localhost dev ports).

### 3. Start Postgres locally (options)

- Use Docker just for DB:

```bash
docker run --name bible_qa_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=bible_qa -p 5432:5432 -d postgres:15-alpine
```

- Or install Postgres natively and create database `bible_qa`.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# (Optional) Apply schema if scripts/create_tables.sql exists
# psql -h localhost -U postgres -d bible_qa -f scripts/create_tables.sql
uvicorn app.main:app --reload --port 8000
```

Backend now at http://localhost:8000

### 5. Frontend setup

Open a new terminal:

```bash
cd frontend
npm install
# Create frontend .env if needed (example)
# echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

Frontend now at http://localhost:5173

## Quick Start (Full Docker)

From repo root ensure `.env` contains `OPENAI_API_KEY`.

```bash
docker compose up --build
```

Services:

- Postgres: localhost:5432
- Backend API: http://localhost:8000
- Frontend (static server): http://localhost:5173

To rebuild after changes:

```bash
docker compose build --no-cache
```

To stop:

```bash
docker compose down
```

Persisted data lives in the named volume `postgres_data`.

### Frontend Dev vs Production

The compose file builds the frontend with the `dev` target so you get hot-reload via Vite (`npm run dev`).

If you prefer the production static server container (no hot reload, built assets only):

1. Remove `target: dev` under `frontend.build`.
2. Add `command: node server.js` (or omit if using default CMD).
3. Rebuild:
   ```bash
   docker compose build frontend && docker compose up -d frontend
   ```

Dev container advantages:

- Rapid iteration (instant reloads)
- Source maps

Prod container advantages:

- Smaller image & faster start
- Matches deployment behavior

## Running Tests

### Backend

```bash
cd backend
pytest -m "not integration" -v
```

For full coverage:

```bash
pytest -v --cov=app --cov-report=term-missing
```

Integration tests require a real Postgres instance and appropriate env vars.

### Frontend

```bash
cd frontend
npm test
```

End-to-end tests (ensure backend running & optionally seeded data):

```bash
npm run test:e2e
```

## Environment Variables

Root `.env` consumed by Docker Compose injecting:

- `OPENAI_API_KEY` – Required for backend OpenAI calls
- (Add more as needed: `ALLOWED_ORIGINS`, etc.)

Backend-specific (can also be set in shell):

- `DATABASE_URL` – Compose sets automatically for container usage
- `OPENAI_MODEL` – Overrides default model

Frontend `.env`:

- `VITE_API_URL` – Points to backend (dev default http://localhost:8000)

## Common Issues

| Symptom                                      | Fix                                                                                                                                         |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 401 from OpenAI                              | Check `OPENAI_API_KEY` and no stray quotes.                                                                                                 |
| CORS errors in browser                       | Ensure frontend origin added to `ALLOWED_ORIGINS`.                                                                                          |
| Cannot connect to Postgres                   | Confirm container healthy or local DB running; match port.                                                                                  |
| Docker build fails for backend psycopg2      | Ensure build-essential & libpq-dev installed (handled in Dockerfile).                                                                       |
| Frontend 404s after refresh                  | Production server includes SPA fallback; during dev use Vite dev server.                                                                    |
| COPY path errors in Docker build             | Ensure Dockerfile COPY paths omit leading `backend/` or `frontend/` since build context is already that directory.                          |
| Postgres port conflict (5432 already in use) | Either stop local Postgres (`brew services stop postgresql`) or change host port in compose (now using 5433:5432). Access DB via port 5433. |

## API Usage

POST `http://localhost:8000/api/ask`

```json
{ "question": "What is faith?", "user_id": 1 }
```

Response:

```json
{ "answer": "Faith is ...", "question_id": 42 }
```

GET `http://localhost:8000/api/history/1?limit=10`

## Alembic Migrations

This project uses Alembic for schema management.

### Files

- `backend/alembic.ini` – Alembic configuration (uses container service `db`).
- `backend/alembic/` – Environment plus versions folder.
- `backend/alembic/versions/0001_create_questions_answers.py` – Initial idempotent migration.
- `backend/start.sh` – Runs `alembic upgrade head` before starting Uvicorn.
- `backend/Dockerfile` – Invokes `start.sh` as container CMD ensuring migrations apply each start.

### Basic Commands

```bash
cd backend
alembic upgrade head      # Apply all migrations
alembic current           # Show current DB revision
alembic history --verbose # List migration history
```

### Creating a Migration

```bash
alembic revision -m "add topic column to questions"
# Edit file in alembic/versions/, then:
alembic upgrade head
```

### Downgrading (Be Careful)

```bash
alembic downgrade -1
```

### Using Environment Variable for Local DB

```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5433/bible_qa
alembic upgrade head
```

### Troubleshooting

| Issue                   | Resolution                                                                          |
| ----------------------- | ----------------------------------------------------------------------------------- |
| DuplicateTable errors   | Migration already applied; make ops idempotent or create proper separate revisions. |
| Missing alembic_version | Ensure `alembic upgrade head` ran; inspect backend logs.                            |
| Wrong database          | Check `DATABASE_URL` env and `alembic.ini`.                                         |
| Partial migration       | Inspect tables via psql, create corrective follow-up revision.                      |

### Production Tips

- Run migrations once per deploy before scaling replicas.
- Avoid destructive downgrades without backups.
- Use separate migration job or init container for Kubernetes.

## Next Steps / Enhancements

- Add `.env.example` templates for root/frontend/backend.
- Add CI workflow for tests & lint.
- Add rate limiting & caching layer.
- Add frontend UI for history browsing.

## License

MIT
