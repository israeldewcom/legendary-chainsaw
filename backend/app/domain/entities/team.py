from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Team:
    id: Optional[int] = None
    owner_id: int = 0
    name: str = ""
    slug: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


@dataclass
class TeamMember:
    id: Optional[int] = None
    team_id: int = 0
    user_id: int = 0
    role: str = "member"  # admin, member, viewer
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
