from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from app.domain.value_objects.money import Money


@dataclass
class DomainEvent:
    occurred_at: datetime = datetime.utcnow()


@dataclass
class UserRegistered(DomainEvent):
    user_id: int
    email: str
    verification_token: str


@dataclass
class UserEmailVerified(DomainEvent):
    user_id: int


@dataclass
class UserPasswordReset(DomainEvent):
    user_id: int


@dataclass
class UserMFAEnabled(DomainEvent):
    user_id: int


@dataclass
class UserMFADisabled(DomainEvent):
    user_id: int


@dataclass
class UserSubscribed(DomainEvent):
    user_id: int
    tier: str
    old_tier: str


@dataclass
class UserLoginFailed(DomainEvent):
    user_id: int
    attempts: int


@dataclass
class UserAccountLocked(DomainEvent):
    user_id: int


@dataclass
class UserDataExported(DomainEvent):
    user_id: int


@dataclass
class UserDeletionRequested(DomainEvent):
    user_id: int


@dataclass
class UserActivityLogged(DomainEvent):
    user_id: int
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    metadata: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class TransactionCategorized(DomainEvent):
    transaction_id: int
    client_id: int
    category: str
    confidence: float


@dataclass
class ReceiptProcessed(DomainEvent):
    receipt_id: int
    user_id: int
    status: str
    transaction_id: Optional[int] = None


@dataclass
class AffiliateCommissionCredited(DomainEvent):
    user_id: int
    amount: Money


@dataclass
class WithdrawalRequested(DomainEvent):
    user_id: int
    withdrawal_id: int
    amount: Money


@dataclass
class WithdrawalApproved(DomainEvent):
    withdrawal_id: int
    user_id: int
    amount: Money


@dataclass
class WithdrawalPaid(DomainEvent):
    withdrawal_id: int
    user_id: int
    amount: Money


@dataclass
class NotificationCreated(DomainEvent):
    user_id: int
    notification_id: int
    type: str


@dataclass
class QuickBooksTokenRefreshed(DomainEvent):
    user_id: int
    realm_id: str
