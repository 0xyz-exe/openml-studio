# Architecture

## Stack

- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: Next.js 14 (App Router) + React + Tailwind CSS + shadcn/ui
- **SDK**: Python package with requests + retry logic
- **Storage**: Filesystem for artifacts
- **Testing**: pytest + Playwright

## Components

```
┌─────────────┐
│   Web UI    │ (Next.js)
└──────┬──────┘
       │ HTTP
┌──────▼──────┐     ┌────────────┐
│  FastAPI    │────▶│   SQLite   │
│   Backend   │     └────────────┘
└──────┬──────┘
       │             ┌────────────┐
       └────────────▶│ Artifacts/ │
                     │ Filesystem │
                     └────────────┘
       ▲
       │ HTTP
┌──────┴──────┐
│ Python SDK  │ (training scripts)
└─────────────┘
```

## Database Schema

**projects**
- id (PK)
- name (unique)
- description
- created_at

**experiments**
- id (PK)
- project_id (FK)
- name
- created_at

**runs**
- id (PK, UUID)
- experiment_id (FK)
- name
- status (queued, running, completed, failed)
- params (JSON)
- start_time
- end_time
- source_commit
- dataset_name
- dataset_version

**metrics**
- id (PK)
- run_id (FK)
- name
- value (float)
- step (int)
- timestamp

**artifacts**
- id (PK)
- run_id (FK)
- filename
- storage_path
- size_bytes
- created_at

## API Endpoints

```
POST   /api/projects
GET    /api/projects
GET    /api/projects/{id}

POST   /api/experiments
GET    /api/experiments?project_id=X
GET    /api/experiments/{id}

POST   /api/runs
GET    /api/runs?experiment_id=X
GET    /api/runs/{id}
PATCH  /api/runs/{id}  (status, end_time)

POST   /api/runs/{id}/metrics  (batch)
GET    /api/runs/{id}/metrics

POST   /api/runs/{id}/artifacts (multipart upload)
GET    /api/runs/{id}/artifacts
GET    /api/artifacts/{id}/download

GET    /api/compare?run_ids=a,b,c
```

## Security

- Artifact paths: UUID-based, no user input in paths
- File uploads: size limit 500MB, validate extensions
- SQL injection: SQLAlchemy parameterized queries
- Path traversal: artifacts stored as `artifacts/{run_id}/{uuid}_{filename}`

## Deployment (MVP)

Single-machine:
```
backend/   → uvicorn on :8001
frontend/  → next dev on :3001 (or next build + start)
```

## Limitations (MVP)

- Single user (no auth)
- Local storage only
- No distributed lock for concurrent metric writes
- No artifact deduplication
