from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class WebhookEvent:
    id: Optional[int] = None
    provider: str = ""  # stripe, quickbooks, etc.
    event_id: str = ""
    event_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False
    processed_at: Optional[datetime] = None
    retry_count: int = 0
    last_retry_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def mark_processed(self) -> None:
        self.processed = True
        self.processed_at = datetime.utcnow()

    def increment_retry(self) -> None:
        self.retry_count += 1
        self.last_retry_at = datetime.utcnow()
