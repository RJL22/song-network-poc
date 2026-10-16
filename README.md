# Song Network POC

Song Network is a FastAPI + React application for crowdsourcing song-similarity relationships. Users search for songs, connect similar songs, and see which connections have attracted the most support.

## Current milestone

The current implementation includes:

- FastAPI, SQLAlchemy, PostgreSQL, Alembic, and Docker-based local development.
- Username/password authentication with JWTs stored in an HttpOnly cookie.
- Local-first song search with MusicBrainz fallback and catalog caching.
- Idempotent, symmetric song connections with supporter counts and points.
- A React/TypeScript frontend with login, signup, discovery, connection, supporter, and connection-history flows.
- Backend API and configuration tests.

The project is still a proof of concept. User profiles, friends, richer frontend routing, and broader automated coverage remain future work.

## Architecture documentation

- [Song search and connection architecture](docs/architecture/song-search-and-connections.md)
- [ADR 0001: Local song cache and connection lifecycle](docs/adr/0001-local-song-cache-and-connection-lifecycle.md)
- [Developer notes and roadmap](devREADME.md)

## Running locally

### Prerequisites

- Docker
- Python 3.11+
- Node.js compatible with the frontend toolchain

### Start PostgreSQL

```bash
docker compose up -d
```

### Set up the backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Create `backend/.env` with values based on [`backend/.env.example`](backend/.env.example). Do not commit the real `.env` file.

Run migrations and start the API:

```bash
.venv/bin/alembic upgrade head
.venv/bin/python -m uvicorn app.main:app --reload
```

The API and OpenAPI documentation are available at `http://localhost:8000` and `http://localhost:8000/docs`.

### Set up the frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend defaults to `http://localhost:8000` for the API. Set `VITE_API_URL` when the API runs elsewhere.

## Tests

From the repository root:

```bash
backend/.venv/bin/python -m pytest
```

The repository-level `pytest.ini` limits collection to `backend/tests/`; the legacy `backend/test_orm.py` file is a manual database-inspection script.

## Database note

The migration that adds `uq_connections_song_pair` assumes existing connection rows already use normalized song-pair ordering and contain no duplicate pairs. Check existing data before applying it to a populated database.
