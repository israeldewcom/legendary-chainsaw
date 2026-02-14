from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal


@dataclass
class PayoutBatch:
    id: Optional[int] = None
    batch_date: datetime = field(default_factory=datetime.utcnow)
    total_amount: Decimal = Decimal(0)
    currency: str = "USD"
    status: str = "pending"  # pending, processing, completed, failed
    processed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PayoutBatchItem:
    id: Optional[int] = None
    batch_id: int = 0
    withdrawal_id: int = 0
    amount: Decimal = Decimal(0)
    status: str = "pending"
    error_message: Optional[str] = None

    def mark_success(self) -> None:
        self.status = "success"

    def mark_failed(self, error: str) -> None:
        self.status = "failed"
        self.error_message = error
