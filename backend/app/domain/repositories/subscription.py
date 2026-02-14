from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.subscription import Subscription


class SubscriptionRepository(ABC):
    @abstractmethod
    async def get_by_id(self, sub_id: int) -> Optional[Subscription]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Optional[Subscription]:
        pass

    @abstractmethod
    async def get_by_stripe_subscription_id(self, stripe_id: str) -> Optional[Subscription]:
        pass

    @abstractmethod
    async def save(self, subscription: Subscription) -> Subscription:
        pass

    @abstractmethod
    async def delete(self, sub_id: int) -> None:
        pass
