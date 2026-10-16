from datetime import datetime
from typing import TypedDict

class RunCreate(TypedDict, total=False):
    experiment_id: int
    name: str | None
    params: dict
    source_commit: str | None
    dataset_name: str | None
    dataset_version: str | None

class RunUpdate(TypedDict, total=False):
    status: str | None
    end_time: datetime | None
    error_message: str | None

class RunResponse(TypedDict):
    id: str
    experiment_id: int
    name: str | None
    status: str
    params: dict
    start_time: datetime
    end_time: datetime | None
    source_commit: str | None
    dataset_name: str | None
    dataset_version: str | None
    error_message: str | None

class MetricCreate(TypedDict, total=False):
    name: str
    value: float
    step: int

class MetricResponse(TypedDict):
    id: int
    run_id: str
    name: str
    value: float
    step: int
    timestamp: datetime
