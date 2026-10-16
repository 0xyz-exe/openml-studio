from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..database import get_db
from ..models import Project

router = APIRouter()

@router.post("", status_code=201)
def create_project(project: dict, db: Session = Depends(get_db)):
    db_project = Project(name=project["name"], description=project.get("description"))
    try:
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return _project_to_dict(db_project)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Project name already exists")

def _project_to_dict(p):
    return {"id": p.id, "name": p.name, "description": p.description, "created_at": p.created_at.isoformat()}

@router.get("")
def list_projects(db: Session = Depends(get_db)):
    return [_project_to_dict(p) for p in db.query(Project).order_by(Project.created_at.desc()).all()]

@router.get("/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return _project_to_dict(project)
