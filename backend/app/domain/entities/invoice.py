from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from decimal import Decimal


@dataclass
class Invoice:
    id: Optional[int] = None
    user_id: int = 0
    stripe_invoice_id: Optional[str] = None
    invoice_number: Optional[str] = None
    amount: Decimal = Decimal(0)
    currency: str = "USD"
    status: str = "draft"  # draft, open, paid, void, uncollectible
    invoice_pdf: Optional[str] = None
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    paid: bool = False
    tax_amount: Decimal = Decimal(0)
    tax_rate: Optional[Decimal] = None
    tax_country: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def mark_paid(self, paid_at: Optional[datetime] = None) -> None:
        self.status = "paid"
        self.paid = True
        self.paid_at = paid_at or datetime.utcnow()

    def update_from_stripe(self, stripe_invoice: dict) -> None:
        self.amount = Decimal(stripe_invoice["amount_due"]) / 100
        self.currency = stripe_invoice["currency"].upper()
        self.status = stripe_invoice["status"]
        self.invoice_pdf = stripe_invoice.get("invoice_pdf")
        self.due_date = datetime.fromtimestamp(stripe_invoice["due_date"]) if stripe_invoice.get("due_date") else None
        self.paid = stripe_invoice["status"] == "paid"
        if self.paid:
            self.paid_at = datetime.utcnow()
