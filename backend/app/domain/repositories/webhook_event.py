from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.webhook_event import WebhookEvent


class WebhookEventRepository(ABC):
    @abstractmethod
    async def get_by_event_id(self, provider: str, event_id: str) -> Optional[WebhookEvent]:
        pass

    @abstractmethod
    async def save(self, event: WebhookEvent) -> WebhookEvent:
        pass

    @abstractmethod
    async def mark_processed(self, event_id: int) -> None:
        pass

    @abstractmethod
    async def get_unprocessed(self, provider: str, limit: int = 10) -> List[WebhookEvent]:
        pass
