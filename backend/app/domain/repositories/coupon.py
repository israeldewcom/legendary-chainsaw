from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.coupon import Coupon


class CouponRepository(ABC):
    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[Coupon]:
        pass

    @abstractmethod
    async def save(self, coupon: Coupon) -> Coupon:
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[Coupon]:
        pass
