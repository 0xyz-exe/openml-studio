from datetime import datetime
from typing import TypedDict

class ProjectCreate(TypedDict, total=False):
    name: str
    description: str | None

class ProjectResponse(TypedDict):
    id: int
    name: str
    description: str | None
    created_at: datetime
