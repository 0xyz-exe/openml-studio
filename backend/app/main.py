from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import projects, experiments, runs, artifacts
from .database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OpenML Studio", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(experiments.router, prefix="/api/experiments", tags=["experiments"])
app.include_router(runs.router, prefix="/api/runs", tags=["runs"])
app.include_router(artifacts.router, prefix="/api/artifacts", tags=["artifacts"])

@app.get("/")
def root():
    return {"message": "OpenML Studio API", "version": "0.1.0"}
