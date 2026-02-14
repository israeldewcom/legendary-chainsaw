from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.receipt import Receipt


class ReceiptRepository(ABC):
    @abstractmethod
    async def get_by_id(self, receipt_id: int, user_id: int) -> Optional[Receipt]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Receipt]:
        pass

    @abstractmethod
    async def get_by_client_id(self, client_id: int, skip: int = 0, limit: int = 100) -> List[Receipt]:
        pass

    @abstractmethod
    async def save(self, receipt: Receipt) -> Receipt:
        pass

    @abstractmethod
    async def delete(self, receipt_id: int, user_id: int) -> None:
        pass
