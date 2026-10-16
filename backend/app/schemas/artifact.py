from datetime import datetime
from typing import TypedDict

class ArtifactResponse(TypedDict):
    id: int
    run_id: str
    filename: str
    size_bytes: int | None
    created_at: datetime
