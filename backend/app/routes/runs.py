from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import uuid4
from datetime import datetime
from ..database import get_db
from ..models import Run, Experiment, Metric
from ..schemas import RunCreate, RunUpdate, RunResponse, MetricCreate, MetricResponse

router = APIRouter()

def _run_to_dict(r):
    return {
        "id": r.id, "experiment_id": r.experiment_id, "name": r.name, "status": r.status.value,
        "params": r.params, "start_time": r.start_time.isoformat(), 
        "end_time": r.end_time.isoformat() if r.end_time else None,
        "source_commit": r.source_commit, "dataset_name": r.dataset_name,
        "dataset_version": r.dataset_version, "error_message": r.error_message
    }

def _metric_to_dict(m):
    return {"id": m.id, "run_id": m.run_id, "name": m.name, "value": m.value, "step": m.step, "timestamp": m.timestamp.isoformat()}

@router.post("", status_code=201)
def create_run(run: dict, db: Session = Depends(get_db)):
    # Verify experiment exists
    experiment = db.query(Experiment).filter(Experiment.id == run["experiment_id"]).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    db_run = Run(
        id=str(uuid4()),
        experiment_id=run["experiment_id"],
        name=run.get("name") or f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        params=run.get("params", {}),
        source_commit=run.get("source_commit"),
        dataset_name=run.get("dataset_name"),
        dataset_version=run.get("dataset_version")
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return _run_to_dict(db_run)

@router.get("")
def list_runs(
    experiment_id: int | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    query = db.query(Run)
    if experiment_id is not None:
        query = query.filter(Run.experiment_id == experiment_id)
    if status is not None:
        query = query.filter(Run.status == status)
    return [_run_to_dict(r) for r in query.order_by(Run.start_time.desc()).limit(limit).all()]

@router.get("/{run_id}")
def get_run(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _run_to_dict(run)

@router.patch("/{run_id}")
def update_run(run_id: str, update: dict, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    if "status" in update:
        run.status = update["status"]
    if "end_time" in update:
        run.end_time = datetime.fromisoformat(update["end_time"])
    if "error_message" in update:
        run.error_message = update["error_message"]
    
    db.commit()
    db.refresh(run)
    return _run_to_dict(run)

@router.post("/{run_id}/metrics", status_code=201)
def log_metrics(
    run_id: str,
    metrics: list[dict],
    db: Session = Depends(get_db)
):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    db_metrics = []
    for metric in metrics:
        db_metric = Metric(
            run_id=run_id,
            name=metric["name"],
            value=metric["value"],
            step=metric.get("step", 0)
        )
        db.add(db_metric)
        db_metrics.append(db_metric)
    
    db.commit()
    for m in db_metrics:
        db.refresh(m)
    return [_metric_to_dict(m) for m in db_metrics]

@router.get("/{run_id}/metrics")
def get_metrics(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return [_metric_to_dict(m) for m in db.query(Metric).filter(Metric.run_id == run_id).order_by(Metric.step).all()]

@router.get("/compare", response_model=dict)
def compare_runs(run_ids: str = Query(...), db: Session = Depends(get_db)):
    ids = [rid.strip() for rid in run_ids.split(",")]
    runs = db.query(Run).filter(Run.id.in_(ids)).all()
    
    if len(runs) != len(ids):
        raise HTTPException(status_code=404, detail="One or more runs not found")
    
    # Get final metrics (max step) for each run
    comparison = []
    for run in runs:
        final_metrics = (
            db.query(Metric.name, Metric.value)
            .filter(Metric.run_id == run.id)
            .group_by(Metric.name)
            .having(Metric.step == func.max(Metric.step))
            .all()
        )
        
        comparison.append({
            "run_id": run.id,
            "name": run.name,
            "status": run.status,
            "params": run.params,
            "metrics": {m.name: m.value for m in final_metrics}
        })
    
    return {"runs": comparison}
