from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Experiment, Project
from ..schemas import ExperimentCreate, ExperimentResponse

router = APIRouter()

def _exp_to_dict(e):
    return {"id": e.id, "project_id": e.project_id, "name": e.name, "created_at": e.created_at.isoformat()}

@router.post("", status_code=201)
def create_experiment(experiment: dict, db: Session = Depends(get_db)):
    # Verify project exists
    project = db.query(Project).filter(Project.id == experiment["project_id"]).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_experiment = Experiment(
        project_id=experiment["project_id"],
        name=experiment["name"]
    )
    db.add(db_experiment)
    db.commit()
    db.refresh(db_experiment)
    return _exp_to_dict(db_experiment)

@router.get("")
def list_experiments(
    project_id: int | None = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Experiment)
    if project_id is not None:
        query = query.filter(Experiment.project_id == project_id)
    return [_exp_to_dict(e) for e in query.order_by(Experiment.created_at.desc()).all()]

@router.get("/{experiment_id}")
def get_experiment(experiment_id: int, db: Session = Depends(get_db)):
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return _exp_to_dict(experiment)
