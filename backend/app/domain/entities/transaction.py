from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal

from app.domain.value_objects.money import Money
from app.domain.value_objects.tax_category import TaxCategory


@dataclass
class Transaction:
    id: Optional[int] = None
    client_id: int = 0
    user_id: int = 0  # denormalised for performance
    date: datetime = field(default_factory=datetime.utcnow)
    description: str = ""
    amount: Money = field(default_factory=lambda: Money(0))
    currency: str = "USD"
    category: Optional[TaxCategory] = None
    subcategory: Optional[str] = None
    confidence: Optional[float] = None
    status: str = "pending"  # pending, categorized, reviewed, flagged, duplicate
    reviewed: bool = False
    user_override: Optional[str] = None
    vendor: Optional[str] = None
    receipt_id: Optional[int] = None
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tax_year: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    is_duplicate: bool = False
    parent_id: Optional[int] = None
    reconciled: bool = False
    exported_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    def categorize(self, category: TaxCategory, subcategory: Optional[str], confidence: float) -> None:
        self.category = category
        self.subcategory = subcategory
        self.confidence = confidence
        self.status = "categorized"
        self.updated_at = datetime.utcnow()

    def review(self, user_override: Optional[str] = None) -> None:
        self.reviewed = True
        self.status = "reviewed"
        if user_override:
            self.user_override = user_override
            self.category = TaxCategory(user_override)
        self.updated_at = datetime.utcnow()

    def flag(self) -> None:
        self.status = "flagged"
        self.updated_at = datetime.utcnow()

    def mark_exported(self) -> None:
        self.exported_at = datetime.utcnow()

    def mark_duplicate(self, parent_id: int) -> None:
        self.is_duplicate = True
        self.parent_id = parent_id
        self.status = "duplicate"

    def reconcile(self) -> None:
        self.reconciled = True
        self.updated_at = datetime.utcnow()
