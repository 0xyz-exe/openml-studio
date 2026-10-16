from datetime import datetime
from typing import TypedDict

class ExperimentCreate(TypedDict):
    project_id: int
    name: str

class ExperimentResponse(TypedDict):
    id: int
    project_id: int
    name: str
    created_at: datetime
