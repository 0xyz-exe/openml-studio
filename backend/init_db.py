"""Initialize database tables"""
from app.database import engine, Base
from app.models import Project, Experiment, Run, Metric, Artifact

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized")

if __name__ == "__main__":
    init_db()
