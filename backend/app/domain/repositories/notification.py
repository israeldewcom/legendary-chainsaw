from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.notification import Notification


class NotificationRepository(ABC):
    @abstractmethod
    async def get_by_id(self, notif_id: int, user_id: int) -> Optional[Notification]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100, unread_only: bool = False) -> List[Notification]:
        pass

    @abstractmethod
    async def save(self, notification: Notification) -> Notification:
        pass

    @abstractmethod
    async def mark_read(self, notif_id: int, user_id: int) -> None:
        pass

    @abstractmethod
    async def mark_all_read(self, user_id: int) -> None:
        pass
