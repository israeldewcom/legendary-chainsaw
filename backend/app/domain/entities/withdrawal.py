from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from decimal import Decimal


@dataclass
class WithdrawalRequest:
    id: Optional[int] = None
    user_id: int = 0
    amount: Decimal = Decimal(0)
    currency: str = "USD"
    method: str = "stripe_connect"  # stripe_connect, paypal, bank_transfer
    status: str = "pending"  # pending, approved, rejected, paid
    admin_notes: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def approve(self) -> None:
        self.status = "approved"

    def reject(self, reason: str) -> None:
        self.status = "rejected"
        self.admin_notes = reason

    def mark_paid(self) -> None:
        self.status = "paid"
        self.processed_at = datetime.utcnow()
