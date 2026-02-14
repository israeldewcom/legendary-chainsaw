from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.user_session import UserSession


class UserSessionRepository(ABC):
    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[UserSession]:
        pass

    @abstractmethod
    async def save(self, session: UserSession) -> UserSession:
        pass

    @abstractmethod
    async def delete_expired(self) -> None:
        pass

    @abstractmethod
    async def delete_by_user_id(self, user_id: int) -> None:
        pass
