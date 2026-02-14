from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from decimal import Decimal


@dataclass
class Coupon:
    id: Optional[int] = None
    code: str = ""
    description: Optional[str] = None
    discount_type: str = "percentage"  # percentage, fixed
    discount_amount: Optional[Decimal] = None
    duration: str = "once"  # once, repeating, forever
    duration_in_months: Optional[int] = None
    max_redemptions: Optional[int] = None
    redeemed_count: int = 0
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_valid(self) -> bool:
        now = datetime.utcnow()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.max_redemptions and self.redeemed_count >= self.max_redemptions:
            return False
        return True

    def redeem(self) -> None:
        self.redeemed_count += 1
