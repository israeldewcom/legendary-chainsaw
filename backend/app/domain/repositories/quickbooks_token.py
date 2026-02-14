from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.quickbooks_token import QuickBooksToken


class QuickBooksTokenRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Optional[QuickBooksToken]:
        pass

    @abstractmethod
    async def save(self, token: QuickBooksToken) -> QuickBooksToken:
        pass

    @abstractmethod
    async def delete_by_user_id(self, user_id: int) -> None:
        pass
