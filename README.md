# OpenML Studio

Open-source MLOps experiment tracker. Framework-agnostic.

## Features (MVP)

- Track experiments, runs, metrics, hyperparameters
- Python SDK for any training script
- Compare runs side-by-side
- Local storage (SQLite + filesystem)
- Web UI for visualization

## Quick Start

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Example Usage

```python
from openml_studio import Client

client = Client("http://localhost:8000")

with client.start_run(project="my-project", experiment="baseline") as run:
    run.log_params({"lr": 0.001, "epochs": 10})
    
    for epoch in range(10):
        loss = train_epoch()  # your code
        run.log_metric("loss", loss, step=epoch)
    
    run.log_metric("final_accuracy", 0.95)
```

## Architecture

- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: Next.js + React + Tailwind + shadcn/ui
- **SDK**: Python client with context manager API
- **Storage**: Local filesystem for artifacts

## Status

MVP implementation. Production hardening in progress.
