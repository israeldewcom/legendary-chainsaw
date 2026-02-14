from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.invoice import Invoice


class InvoiceRepository(ABC):
    @abstractmethod
    async def get_by_id(self, invoice_id: int, user_id: int) -> Optional[Invoice]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Invoice]:
        pass

    @abstractmethod
    async def get_by_stripe_invoice_id(self, stripe_id: str) -> Optional[Invoice]:
        pass

    @abstractmethod
    async def save(self, invoice: Invoice) -> Invoice:
        pass
