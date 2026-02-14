from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.client import Client


class ClientRepository(ABC):
    @abstractmethod
    async def get_by_id(self, client_id: int, user_id: int) -> Optional[Client]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Client]:
        pass

    @abstractmethod
    async def save(self, client: Client) -> Client:
        pass

    @abstractmethod
    async def delete(self, client_id: int, user_id: int) -> None:
        pass
