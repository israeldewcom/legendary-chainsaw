from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class QuickBooksToken:
    id: Optional[int] = None
    user_id: int = 0
    realm_id: str = ""
    access_token: str = ""
    refresh_token: str = ""
    expires_at: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        return datetime.utcnow() >= self.expires_at - timedelta(minutes=5)  # buffer

    def update(self, access_token: str, refresh_token: str, expires_in: int) -> None:
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        self.updated_at = datetime.utcnow()
