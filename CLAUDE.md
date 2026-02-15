# Bible QA App — Developer Guide

## Tech Stack
- **Backend:** FastAPI (Python 3.11), PostgreSQL 15, Redis 7, OpenAI API
- **Frontend:** Vue 3 (Composition API), Vite 7, Tailwind CSS 4, Vue Router 4, Axios
- **Deployment:** Docker Compose (local), Heroku (production)
- **Testing:** pytest (backend), Vitest + Playwright (frontend)

## Project Structure
```
bible_qa_app/
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── main.py        # App entry, routes for /api/ask, health check
│   │   ├── config.py      # Pydantic Settings (env-based config)
│   │   ├── database.py    # Connection pool + backward-compat re-exports
│   │   ├── auth.py        # JWT auth, CSRF, guest users
│   │   ├── repositories/  # Database repositories (extracted from database.py)
│   │   ├── routers/       # API route handlers (9 modules)
│   │   ├── services/      # Business logic (9 modules)
│   │   ├── middleware/     # CSRF + API request logging
│   │   ├── mcp/           # Model Context Protocol tools
│   │   ├── models/schemas.py  # All Pydantic request/response models
│   │   └── utils/         # Exceptions, network helpers
│   ├── alembic/           # Database migrations
│   ├── tests/             # pytest tests
│   └── requirements.txt
├── frontend/              # Vue 3 application
│   ├── src/
│   │   ├── views/         # Page components (13 routes)
│   │   ├── components/    # Reusable components + kids/ + ui/
│   │   ├── composables/   # Vue composition logic (useAuth, useBibleQA, etc.)
│   │   ├── services/      # API clients (axios-based)
│   │   ├── constants/     # Bible books, chapter counts
│   │   ├── utils/         # Reference parsers
│   │   └── styles/        # CSS variables, base styles
│   └── tests/             # Playwright E2E tests
└── docker-compose.yml     # Local dev stack (db, redis, backend, frontend)
```

## Key Architecture Decisions
- **Raw SQL over ORM:** Uses psycopg2 with connection pooling, not SQLAlchemy ORM (SQLAlchemy in deps is only for Alembic migrations)
- **Composables over Vuex/Pinia:** Frontend state management uses Vue 3 composables with shared refs
- **Cookie-based auth:** JWT tokens in HTTP-only cookies with CSRF double-submit pattern
- **Guest user system:** Unauthenticated users get auto-created guest accounts for Q&A access
- **Repository pattern:** Database operations extracted into `app/repositories/` modules

## Running Locally

### With Docker
```bash
docker compose up --build
```
Backend at http://localhost:8000, Frontend at http://localhost:5173

### Without Docker
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Running Tests
```bash
# Backend
cd backend
pytest -m "not integration" -v          # Unit tests
pytest --cov=app --cov-report=html      # Coverage report
ruff check app/                         # Lint
ruff format app/                        # Format

# Frontend
cd frontend
npm run test:run                        # Unit tests
npm run test:coverage                   # Coverage
npm run test:e2e                        # E2E (Playwright)
```

## Environment Variables
- Backend: see `backend/.env.example`
- Frontend: set `VITE_API_URL` (defaults to http://localhost:8000)

## Database Migrations
```bash
cd backend
alembic upgrade head        # Apply all migrations
alembic revision --autogenerate -m "description"  # Create new migration
```

## Coding Conventions
- Backend: Python type hints, Pydantic models for all request/response schemas
- Frontend: Vue 3 Composition API, PascalCase components, "Base" prefix for UI components
- All new Pydantic models go in `app/models/schemas.py`
- All new repository classes go in `app/repositories/`
- All new API routes go in `app/routers/` (not in main.py)
