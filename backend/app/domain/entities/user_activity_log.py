from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class UserActivityLog:
    id: Optional[int] = None
    user_id: int = 0
    action: str = ""
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
