import uuid
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime

class JobStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class JobManager:
    def __init__(self):
        # In-memory storage. In production, use Redis or Database.
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def create_job(self) -> str:
        """Create a new job and return its ID."""
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "id": job_id,
            "status": JobStatus.PENDING,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }
        return job_id

    def update_job(self, job_id: str, status: JobStatus, result: Optional[Any] = None, error: Optional[str] = None):
        """Update the status and result of a job."""
        if job_id not in self._jobs:
            return # Or raise exception
        
        self._jobs[job_id]["status"] = status
        self._jobs[job_id]["updated_at"] = datetime.now().isoformat()
        
        if result is not None:
            self._jobs[job_id]["result"] = result
        
        if error is not None:
            self._jobs[job_id]["error"] = error

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve job details."""
        return self._jobs.get(job_id)

# Global instance
job_manager = JobManager()
