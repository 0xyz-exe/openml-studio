from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from uuid import uuid4
import os
from ..database import get_db
from ..models import Run, Artifact

router = APIRouter()

ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)

def _artifact_to_dict(a):
    return {"id": a.id, "run_id": a.run_id, "filename": a.filename, "size_bytes": a.size_bytes, "created_at": a.created_at.isoformat()}

@router.post("/{run_id}", status_code=201)
async def upload_artifact(
    run_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    # Create run-specific directory
    run_dir = ARTIFACTS_DIR / run_id
    run_dir.mkdir(exist_ok=True)
    
    # Generate storage path with UUID to prevent conflicts
    storage_filename = f"{uuid4()}_{file.filename}"
    storage_path = run_dir / storage_filename
    
    # Save file
    content = await file.read()
    with open(storage_path, "wb") as f:
        f.write(content)
    
    # Create DB record
    db_artifact = Artifact(
        run_id=run_id,
        filename=file.filename,
        storage_path=str(storage_path),
        size_bytes=len(content)
    )
    db.add(db_artifact)
    db.commit()
    db.refresh(db_artifact)
    
    return _artifact_to_dict(db_artifact)

@router.get("/{run_id}")
def list_artifacts(run_id: str, db: Session = Depends(get_db)):
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return [_artifact_to_dict(a) for a in db.query(Artifact).filter(Artifact.run_id == run_id).all()]

@router.get("/download/{artifact_id}")
def download_artifact(artifact_id: int, db: Session = Depends(get_db)):
    artifact = db.query(Artifact).filter(Artifact.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    if not os.path.exists(artifact.storage_path):
        raise HTTPException(status_code=404, detail="Artifact file not found")
    
    return FileResponse(
        artifact.storage_path,
        filename=artifact.filename,
        media_type="application/octet-stream"
    )
