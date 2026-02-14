from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.withdrawal import WithdrawalRequest


class WithdrawalRepository(ABC):
    @abstractmethod
    async def get_by_id(self, withdrawal_id: int) -> Optional[WithdrawalRequest]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[WithdrawalRequest]:
        pass

    @abstractmethod
    async def get_pending(self, skip: int = 0, limit: int = 100) -> List[WithdrawalRequest]:
        pass

    @abstractmethod
    async def save(self, withdrawal: WithdrawalRequest) -> WithdrawalRequest:
        pass
