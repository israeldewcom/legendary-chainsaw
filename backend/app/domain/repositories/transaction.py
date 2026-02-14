from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from datetime import datetime
from app.domain.entities.transaction import Transaction


class TransactionRepository(ABC):
    @abstractmethod
    async def get_by_id(self, transaction_id: int, user_id: Optional[int] = None) -> Optional[Transaction]:
        pass

    @abstractmethod
    async def get_by_client_id(self, client_id: int, skip: int = 0, limit: int = 100) -> List[Transaction]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100, filters: Optional[dict] = None) -> List[Transaction]:
        pass

    @abstractmethod
    async def save(self, transaction: Transaction) -> Transaction:
        pass

    @abstractmethod
    async def delete(self, transaction_id: int, client_id: int) -> None:
        pass

    @abstractmethod
    async def find_duplicates(self, client_id: int, amount: float, date: datetime, description: str) -> List[Transaction]:
        pass

    @abstractmethod
    async def count_by_user_and_month(self, user_id: int, year: int, month: int) -> int:
        pass

    @abstractmethod
    async def bulk_update(self, transactions: List[Transaction]) -> None:
        pass

    @abstractmethod
    async def count_by_user_and_date_range(self, user_id: int, start: datetime, end: datetime) -> int:
        pass
