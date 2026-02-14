from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any


@dataclass
class BackgroundJob:
    id: Optional[int] = None
    job_type: str = ""
    status: str = "pending"  # pending, running, completed, failed
    params: Optional[Any] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def start(self) -> None:
        self.status = "running"
        self.started_at = datetime.utcnow()

    def complete(self, result: Any) -> None:
        self.status = "completed"
        self.result = result
        self.completed_at = datetime.utcnow()

    def fail(self, error: str) -> None:
        self.status = "failed"
        self.error = error
        self.completed_at = datetime.utcnow()
