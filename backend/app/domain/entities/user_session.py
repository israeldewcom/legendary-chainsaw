from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class UserSession:
    id: Optional[int] = None
    user_id: int = 0
    session_token: str = ""
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    expires_at: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at
