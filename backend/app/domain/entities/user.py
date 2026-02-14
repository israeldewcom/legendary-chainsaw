from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
import hashlib
import base64
import secrets

from app.domain.value_objects.email import Email
from app.domain.value_objects.money import Money
from app.domain.events.domain_events import (
    UserRegistered, UserSubscribed, AffiliateCommissionCredited,
    UserEmailVerified, UserPasswordReset, UserMFAEnabled, UserMFADisabled,
    UserLoginFailed, UserAccountLocked, UserDataExported, UserDeletionRequested,
    UserActivityLogged
)
from app.config import settings


@dataclass
class User:
    id: Optional[int] = None
    email: Email = field(default_factory=Email)
    email_verified: bool = False
    email_verification_token: Optional[str] = None
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None
    hashed_password: str = ""
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    mfa_secret: Optional[str] = None
    mfa_enabled: bool = False
    mfa_recovery_codes: List[str] = field(default_factory=list)
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    last_active_at: Optional[datetime] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    timezone: str = "UTC"
    subscription_tier: str = "free"
    subscription_status: str = "active"
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    monthly_transactions_used: int = 0
    monthly_transactions_limit: int = 100
    trial_end_date: Optional[datetime] = None
    referral_code: str = ""
    referred_by_id: Optional[int] = None
    affiliate_earnings: Money = field(default_factory=lambda: Money(0))
    affiliate_balance: Money = field(default_factory=lambda: Money(0))
    affiliate_paid: Money = field(default_factory=lambda: Money(0))
    stripe_connect_account_id: Optional[str] = None
    paypal_email: Optional[str] = None
    payout_preference: str = "stripe_connect"
    data_export_requested_at: Optional[datetime] = None
    data_exported_at: Optional[datetime] = None
    data_export_key: Optional[str] = None
    deletion_requested_at: Optional[datetime] = None
    deletion_scheduled_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    # Domain events
    _events: List[object] = field(default_factory=list, init=False, repr=False)

    def register(self, password_hash: str, referral_code: Optional[str] = None) -> None:
        self.hashed_password = password_hash
        self.referral_code = self._generate_referral_code()
        self.email_verification_token = secrets.token_urlsafe(32)
        if referral_code:
            self.referred_by_id = None  # Will be set by repository
        self._events.append(UserRegistered(
            user_id=self.id,
            email=self.email.value,
            verification_token=self.email_verification_token
        ))

    def verify_email(self) -> None:
        self.email_verified = True
        self.email_verification_token = None
        self._events.append(UserEmailVerified(user_id=self.id))

    def initiate_password_reset(self) -> str:
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_expires = datetime.utcnow() + timedelta(hours=24)
        return self.password_reset_token

    def reset_password(self, new_password_hash: str) -> None:
        self.hashed_password = new_password_hash
        self.password_reset_token = None
        self.password_reset_expires = None
        self._events.append(UserPasswordReset(user_id=self.id))

    def activate_mfa(self, secret: str) -> None:
        self.mfa_secret = secret
        self.mfa_enabled = True
        # Generate recovery codes
        self.mfa_recovery_codes = [secrets.token_hex(8) for _ in range(settings.MFA_RECOVERY_CODES_COUNT)]
        self._events.append(UserMFAEnabled(user_id=self.id))

    def disable_mfa(self) -> None:
        self.mfa_secret = None
        self.mfa_enabled = False
        self.mfa_recovery_codes = []
        self._events.append(UserMFADisabled(user_id=self.id))

    def record_failed_login(self) -> None:
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            self.locked_until = datetime.utcnow() + timedelta(minutes=settings.LOGIN_ATTEMPT_LOCKOUT_MINUTES)
            self._events.append(UserAccountLocked(user_id=self.id))

    def reset_failed_logins(self) -> None:
        self.failed_login_attempts = 0
        self.locked_until = None

    def record_login(self, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> None:
        self.last_login_at = datetime.utcnow()
        self.last_active_at = datetime.utcnow()
        self._events.append(UserActivityLogged(
            user_id=self.id,
            action="login",
            ip_address=ip_address,
            user_agent=user_agent
        ))

    def update_last_active(self) -> None:
        self.last_active_at = datetime.utcnow()

    def update_subscription(self, tier: str, status: str = "active") -> None:
        old_tier = self.subscription_tier
        self.subscription_tier = tier
        self.subscription_status = status
        self._events.append(UserSubscribed(user_id=self.id, tier=tier, old_tier=old_tier))

    def increment_transaction_usage(self, count: int = 1) -> None:
        self.monthly_transactions_used += count

    def reset_monthly_usage(self) -> None:
        self.monthly_transactions_used = 0

    def credit_affiliate_commission(self, amount: Money) -> None:
        self.affiliate_earnings += amount
        self.affiliate_balance += amount
        self._events.append(AffiliateCommissionCredited(user_id=self.id, amount=amount))

    def debit_affiliate_balance(self, amount: Money) -> None:
        self.affiliate_balance -= amount
        self.affiliate_paid += amount

    def request_data_export(self) -> None:
        self.data_export_requested_at = datetime.utcnow()
        self._events.append(UserDataExported(user_id=self.id))

    def request_deletion(self) -> None:
        self.deletion_requested_at = datetime.utcnow()
        self.deletion_scheduled_at = datetime.utcnow() + timedelta(days=30)
        self._events.append(UserDeletionRequested(user_id=self.id))

    def soft_delete(self) -> None:
        self.deleted_at = datetime.utcnow()
        self.is_active = False

    def _generate_referral_code(self) -> str:
        hash_obj = hashlib.sha256(self.email.value.encode())
        return base64.urlsafe_b64encode(hash_obj.digest())[:8].decode().upper()

    def collect_events(self) -> List[object]:
        events = self._events.copy()
        self._events.clear()
        return events
