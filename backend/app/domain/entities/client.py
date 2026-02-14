from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Client:
    id: Optional[int] = None
    user_id: int = 0
    name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_year: Optional[int] = None
    filing_status: Optional[str] = None
    ein: Optional[str] = None
    industry: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
