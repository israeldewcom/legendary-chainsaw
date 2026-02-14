from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.payout_batch import PayoutBatch, PayoutBatchItem


class PayoutBatchRepository(ABC):
    @abstractmethod
    async def create_batch(self, batch: PayoutBatch) -> PayoutBatch:
        pass

    @abstractmethod
    async def add_item(self, item: PayoutBatchItem) -> None:
        pass

    @abstractmethod
    async def get_pending_batch(self) -> Optional[PayoutBatch]:
        pass

    @abstractmethod
    async def get_batch_with_items(self, batch_id: int) -> Optional[PayoutBatch]:
        pass

    @abstractmethod
    async def update_batch(self, batch: PayoutBatch) -> None:
        pass
