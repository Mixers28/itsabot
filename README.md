# Bot-Likelihood Analyzer (Reddit v0.1)

A web dashboard + backend that analyzes a single Reddit account’s public activity and returns an automation-likelihood score (0–100) with explainability and evidence links. Snapshot history is persisted for auditing and comparisons over time.

Spec source of truth: `docs/spec.md`.
Invariants: `docs/INVARIANTS.md`.

## What This Includes
- FastAPI backend with RQ worker, Postgres storage, Redis cache/queue.
- Reddit collector with rate limiting and header-aware backoff.
- Feature extraction (timing, repetition, content, interaction).
- Rules-first scoring with explainable reasons and evidence.
- Minimal Next.js UI for Search, Report, and History.
- Docker Compose for local Postgres + Redis.

## Repo Layout
- `backend/` API, collectors, features, scoring, worker jobs, models.
- `frontend/` Next.js UI.
- `infra/` Docker Compose for Postgres + Redis.
- `docs/spec.md` Product and architecture spec.
- `docs/` Context, invariants, and workflow docs.

## Prerequisites
- Python 3.11+
- Node 18+
- Docker (for Postgres + Redis)
- Reddit OAuth credentials

## Environment Variables
Backend expects:
- `DATABASE_URL`
- `REDIS_URL`
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT`
- Optional: `REDDIT_MAX_ITEMS` (default 200)
- Optional: `CACHE_HOURS` (default 6)
- Optional: `REDDIT_QPM_LIMIT` (default 100)

Frontend expects:
- `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`)

## Quick Start
### 1) Start Postgres + Redis
```bash
docker compose -f infra/docker-compose.yml up -d
```

### 2) Backend API
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/bot_likelihood
export REDIS_URL=redis://localhost:6379/0
export REDDIT_CLIENT_ID=bonow69
export REDDIT_CLIENT_SECRET=Ch5zbUpvYXZWLUoyZ2tjVF9mR25yV2dBSjBKNDd0M2cSB2Jvbm93NjkaBXJlYWN0
export REDDIT_USER_AGENT=bot-likelihood-analyzer/0.1

uvicorn app.main:app --reload
```

### 3) Worker
```bash
cd backend
source .venv/bin/activate
export REDIS_URL=redis://localhost:6379/0
PYTHONPATH=. rq worker -u $REDIS_URL
```

### 4) Frontend
```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```

## API Endpoints (v0.1)
- `POST /api/analyze/reddit`
- `GET /api/jobs/{job_id}`
- `GET /api/report/reddit/{username}?snapshot=latest`
- `GET /api/history/reddit/{username}`
- `GET /api/health/reddit-credentials`

## Notes
- Rate limiting and header-aware backoff are enforced for Reddit API calls.
- Credentials stay server-side and are never sent to the client.
- Scores are explainable with reasons and evidence links.
- Coordination likelihood is a single-account proxy in v0.1.

## Next Steps
- Add migrations and tests for data model and scoring.
- Expand UI with evidence filters and coverage summaries.
- Add richer coordination analysis for multi-account comparisons.
