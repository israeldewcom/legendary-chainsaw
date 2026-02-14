from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.user_activity_log import UserActivityLog


class UserActivityLogRepository(ABC):
    @abstractmethod
    async def log(self, log: UserActivityLog) -> None:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[UserActivityLog]:
        pass
