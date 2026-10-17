"""OpenML Studio Python SDK"""
import requests
from typing import Any, Optional
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
import time

class Client:
    def __init__(self, api_url: str = "http://localhost:8001", timeout: int = 30):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
    
    def _retry_request(self, method: str, url: str, max_retries: int = 3, **kwargs):
        """Retry with exponential backoff"""
        for attempt in range(max_retries):
            try:
                response = self.session.request(method, url, timeout=self.timeout, **kwargs)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
    
    def create_project(self, name: str, description: Optional[str] = None) -> dict:
        """Create a new project"""
        response = self._retry_request(
            "POST",
            f"{self.api_url}/api/projects",
            json={"name": name, "description": description}
        )
        return response.json()
    
    def create_experiment(self, project: str, experiment: str) -> dict:
        """Create experiment (creates project if needed)"""
        # Get or create project
        projects = self._retry_request("GET", f"{self.api_url}/api/projects").json()
        project_obj = next((p for p in projects if p["name"] == project), None)
        
        if not project_obj:
            project_obj = self.create_project(project)
        
        # Get or create experiment
        experiments = self._retry_request(
            "GET",
            f"{self.api_url}/api/experiments",
            params={"project_id": project_obj["id"]}
        ).json()
        
        experiment_obj = next((e for e in experiments if e["name"] == experiment), None)
        if not experiment_obj:
            response = self._retry_request(
                "POST",
                f"{self.api_url}/api/experiments",
                json={"project_id": project_obj["id"], "name": experiment}
            )
            experiment_obj = response.json()
        
        return experiment_obj
    
    @contextmanager
    def start_run(
        self,
        project: str,
        experiment: str,
        name: Optional[str] = None,
        params: Optional[dict] = None,
        source_commit: Optional[str] = None,
        dataset_name: Optional[str] = None,
        dataset_version: Optional[str] = None
    ):
        """Context manager for tracking a run"""
        experiment_obj = self.create_experiment(project, experiment)
        
        # Create run
        response = self._retry_request(
            "POST",
            f"{self.api_url}/api/runs",
            json={
                "experiment_id": experiment_obj["id"],
                "name": name,
                "params": params or {},
                "source_commit": source_commit,
                "dataset_name": dataset_name,
                "dataset_version": dataset_version
            }
        )
        run_data = response.json()
        run = Run(self, run_data["id"])
        
        try:
            yield run
            # Mark as completed
            self._retry_request(
                "PATCH",
                f"{self.api_url}/api/runs/{run.run_id}",
                json={"status": "completed", "end_time": datetime.utcnow().isoformat()}
            )
        except Exception as e:
            # Mark as failed
            self._retry_request(
                "PATCH",
                f"{self.api_url}/api/runs/{run.run_id}",
                json={
                    "status": "failed",
                    "end_time": datetime.utcnow().isoformat(),
                    "error_message": str(e)
                }
            )
            raise

class Run:
    def __init__(self, client: Client, run_id: str):
        self.client = client
        self.run_id = run_id
    
    def log_params(self, params: dict):
        """Log parameters (updates existing params)"""
        run = self.client._retry_request(
            "GET",
            f"{self.client.api_url}/api/runs/{self.run_id}"
        ).json()
        
        updated_params = {**run["params"], **params}
        self.client._retry_request(
            "PATCH",
            f"{self.client.api_url}/api/runs/{self.run_id}",
            json={"params": updated_params}
        )
    
    def log_metric(self, name: str, value: float, step: int = 0):
        """Log a single metric"""
        self.log_metrics([{"name": name, "value": value, "step": step}])
    
    def log_metrics(self, metrics: list[dict]):
        """Log multiple metrics (batch)"""
        self.client._retry_request(
            "POST",
            f"{self.client.api_url}/api/runs/{self.run_id}/metrics",
            json=metrics
        )
    
    def log_artifact(self, file_path: str):
        """Upload artifact file"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Artifact not found: {file_path}")
        
        with open(path, "rb") as f:
            self.client._retry_request(
                "POST",
                f"{self.client.api_url}/api/artifacts/{self.run_id}",
                files={"file": (path.name, f)}
            )

__version__ = "0.1.0"
__all__ = ["Client", "Run"]
