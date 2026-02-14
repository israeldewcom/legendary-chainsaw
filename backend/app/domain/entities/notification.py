from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Notification:
    id: Optional[int] = None
    user_id: int = 0
    type: str = "info"  # info, success, warning, error
    title: str = ""
    content: Optional[str] = None
    link: Optional[str] = None
    read_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def mark_read(self) -> None:
        self.read_at = datetime.utcnow()
