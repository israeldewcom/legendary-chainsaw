from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Subscription:
    id: Optional[int] = None
    user_id: int = 0
    stripe_subscription_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    plan_id: str = ""
    status: str = "incomplete"  # incomplete, active, past_due, canceled, etc.
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False
    canceled_at: Optional[datetime] = None
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    coupon_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def cancel(self, at_period_end: bool = True) -> None:
        self.cancel_at_period_end = at_period_end
        if not at_period_end:
            self.status = "canceled"
            self.canceled_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        self.status = "active"
        self.cancel_at_period_end = False
        self.updated_at = datetime.utcnow()

    def mark_past_due(self) -> None:
        self.status = "past_due"
        self.updated_at = datetime.utcnow()

    def update_from_stripe(self, stripe_sub: dict) -> None:
        self.status = stripe_sub["status"]
        self.current_period_start = datetime.fromtimestamp(stripe_sub["current_period_start"])
        self.current_period_end = datetime.fromtimestamp(stripe_sub["current_period_end"])
        self.cancel_at_period_end = stripe_sub["cancel_at_period_end"]
        self.updated_at = datetime.utcnow()
