from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.team import Team, TeamMember


class TeamRepository(ABC):
    @abstractmethod
    async def get_by_id(self, team_id: int) -> Optional[Team]:
        pass

    @abstractmethod
    async def get_by_owner_id(self, owner_id: int) -> List[Team]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> List[Team]:
        pass

    @abstractmethod
    async def save(self, team: Team) -> Team:
        pass

    @abstractmethod
    async def delete(self, team_id: int) -> None:
        pass


class TeamMemberRepository(ABC):
    @abstractmethod
    async def get_by_team_and_user(self, team_id: int, user_id: int) -> Optional[TeamMember]:
        pass

    @abstractmethod
    async def list_by_team(self, team_id: int) -> List[TeamMember]:
        pass

    @abstractmethod
    async def save(self, member: TeamMember) -> TeamMember:
        pass

    @abstractmethod
    async def delete(self, team_id: int, user_id: int) -> None:
        pass
