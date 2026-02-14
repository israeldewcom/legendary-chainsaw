from sqlalchemy import (
    Column, BigInteger, String, Boolean, DateTime, ForeignKey, Text, Numeric, Integer, Float, JSON, ARRAY, Index, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB
import pgvector
from pgvector.sqlalchemy import Vector

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    email_verified = Column(Boolean, server_default="false", nullable=False)
    email_verification_token = Column(String(255), unique=True)
    password_reset_token = Column(String(255), unique=True)
    password_reset_expires = Column(DateTime(timezone=True))
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    company_name = Column(String(255))
    is_active = Column(Boolean, server_default="true", nullable=False)
    is_superuser = Column(Boolean, server_default="false", nullable=False)
    mfa_secret = Column(String(255))
    mfa_enabled = Column(Boolean, server_default="false", nullable=False)
    mfa_recovery_codes = Column(ARRAY(String(32)), server_default="{}", nullable=False)
    failed_login_attempts = Column(Integer, server_default="0", nullable=False)
    locked_until = Column(DateTime(timezone=True))
    last_login_at = Column(DateTime(timezone=True))
    last_active_at = Column(DateTime(timezone=True))
    preferences = Column(JSONB, server_default="{}", nullable=False)
    timezone = Column(String(50), server_default="UTC", nullable=False)
    subscription_tier = Column(String(50), server_default="free", nullable=False)
    subscription_status = Column(String(50), server_default="active", nullable=False)
    stripe_customer_id = Column(String(255), unique=True)
    stripe_subscription_id = Column(String(255), unique=True)
    monthly_transactions_used = Column(Integer, server_default="0", nullable=False)
    monthly_transactions_limit = Column(Integer, server_default="100", nullable=False)
    trial_end_date = Column(DateTime(timezone=True))
    referral_code = Column(String(50), unique=True, nullable=False)
    referred_by_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    affiliate_earnings = Column(Numeric(12, 2), server_default="0", nullable=False)
    affiliate_balance = Column(Numeric(12, 2), server_default="0", nullable=False)
    affiliate_paid = Column(Numeric(12, 2), server_default="0", nullable=False)
    stripe_connect_account_id = Column(String(255), unique=True)
    paypal_email = Column(String(255))
    payout_preference = Column(String(50), server_default="stripe_connect", nullable=False)
    data_export_requested_at = Column(DateTime(timezone=True))
    data_exported_at = Column(DateTime(timezone=True))
    data_export_key = Column(String(255))
    deletion_requested_at = Column(DateTime(timezone=True))
    deletion_scheduled_at = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate="now()")

    # Relationships
    referred = relationship("UserModel", remote_side=[id])
    clients = relationship("ClientModel", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("TransactionModel", back_populates="user", cascade="all, delete-orphan")
    receipts = relationship("ReceiptModel", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("SubscriptionModel", back_populates="user", cascade="all, delete-orphan")
    invoices = relationship("InvoiceModel", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSessionModel", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("NotificationModel", back_populates="user", cascade="all, delete-orphan")
    quickbooks_token = relationship("QuickBooksTokenModel", back_populates="user", uselist=False, cascade="all, delete-orphan")
    withdrawals = relationship("WithdrawalRequestModel", back_populates="user", cascade="all, delete-orphan")
    activity_logs = relationship("UserActivityLogModel", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLogModel", back_populates="user")


class ClientModel(Base):
    __tablename__ = "clients"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    tax_year = Column(Integer)
    filing_status = Column(String(50))
    ein = Column(String(20))
    industry = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate="now()")

    user = relationship("UserModel", back_populates="clients")
    transactions = relationship("TransactionModel", back_populates="client", cascade="all, delete-orphan")
    receipts = relationship("ReceiptModel", back_populates="client", cascade="all, delete-orphan")


class TransactionModel(Base):
    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True, index=True)
    client_id = Column(BigInteger, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    description = Column(Text, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), server_default="USD", nullable=False)
    category = Column(String(100))
    subcategory = Column(String(100))
    confidence = Column(Float)
    status = Column(String(50), server_default="pending", nullable=False, index=True)
    reviewed = Column(Boolean, server_default="false", nullable=False)
    user_override = Column(String(100))
    vendor = Column(String(255))
    receipt_id = Column(BigInteger, ForeignKey("receipts.id", ondelete="SET NULL"))
    embedding = Column(Vector(1536))
    metadata = Column(JSONB, server_default="{}", nullable=False)
    tax_year = Column(Integer)
    tags = Column(ARRAY(String(50)), server_default="{}", nullable=False)
    is_duplicate = Column(Boolean, server_default="false", nullable=False)
    parent_id = Column(BigInteger, ForeignKey("transactions.id", ondelete="SET NULL"))
    reconciled = Column(Boolean, server_default="false", nullable=False)
    exported_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate="now()")

    client = relationship("ClientModel", back_populates="transactions")
    user = relationship("UserModel", back_populates="transactions")
    receipt = relationship("ReceiptModel", back_populates="transaction")
    parent = relationship("TransactionModel", remote_side=[id])


class ReceiptModel(Base):
    __tablename__ = "receipts"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(BigInteger, ForeignKey("clients.id", ondelete="SET NULL"))
    filename = Column(String(255))
    s3_key = Column(String(255), unique=True)
    ocr_text = Column(Text)
    extracted_data = Column(JSONB)
    status = Column(String(50), server_default="pending", nullable=False, index=True)
    error_message = Column(Text)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    page_count = Column(Integer)
    processed_at = Column(DateTime(timezone=True))
    uploaded_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    transaction_id = Column(BigInteger, ForeignKey("transactions.id", ondelete="SET NULL"))

    user = relationship("UserModel", back_populates="receipts")
    client = relationship("ClientModel", back_populates="receipts")
    transaction = relationship("TransactionModel", back_populates="receipt")


class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    stripe_subscription_id = Column(String(255), unique=True)
    stripe_customer_id = Column(String(255))
    plan_id = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    cancel_at_period_end = Column(Boolean, server_default="false", nullable=False)
    canceled_at = Column(DateTime(timezone=True))
    trial_start = Column(DateTime(timezone=True))
    trial_end = Column(DateTime(timezone=True))
    coupon_id = Column(BigInteger, ForeignKey("coupons.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate="now()")

    user = relationship("UserModel", back_populates="subscriptions")
    coupon = relationship("CouponModel")


class InvoiceModel(Base):
    __tablename__ = "invoices"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    stripe_invoice_id = Column(String(255), unique=True)
    invoice_number = Column(String(255))
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), server_default="USD", nullable=False)
    status = Column(String(50), nullable=False)
    invoice_pdf = Column(String(255))
    due_date = Column(DateTime(timezone=True))
    paid_at = Column(DateTime(timezone=True))
    paid = Column(Boolean, server_default="false", nullable=False)
    tax_amount = Column(Numeric(12, 2), server_default="0", nullable=False)
    tax_rate = Column(Numeric(5, 2))
    tax_country = Column(String(2))
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)

    user = relationship("UserModel", back_populates="invoices")


class CouponModel(Base):
    __tablename__ = "coupons"

    id = Column(BigInteger, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255))
    discount_type = Column(String(20), nullable=False)  # percentage, fixed
    discount_amount = Column(Numeric(10, 2))
    duration = Column(String(20), server_default="once", nullable=False)
    duration_in_months = Column(Integer)
    max_redemptions = Column(Integer)
    redeemed_count = Column(Integer, server_default="0", nullable=False)
    valid_from = Column(DateTime(timezone=True))
    valid_until = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)


class TeamModel(Base):
    __tablename__ = "teams"

    id = Column(BigInteger, primary_key=True, index=True)
    owner_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate="now()")

    members = relationship("TeamMemberModel", back_populates="team", cascade="all, delete-orphan")


class TeamMemberModel(Base):
    __tablename__ = "team_members"

    id = Column(BigInteger, primary_key=True, index=True)
    team_id = Column(BigInteger, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), server_default="member", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate="now()")

    __table_args__ = (UniqueConstraint("team_id", "user_id", name="uq_team_members_team_user"),)

    team = relationship("TeamModel", back_populates="members")
    user = relationship("UserModel")


class UserSessionModel(Base):
    __tablename__ = "user_sessions"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)

    user = relationship("UserModel", back_populates="sessions")


class NotificationModel(Base):
    __tablename__ = "notifications"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    link = Column(String(255))
    read_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)

    user = relationship("UserModel", back_populates="notifications")


class QuickBooksTokenModel(Base):
    __tablename__ = "quickbooks_tokens"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    realm_id = Column(String(100), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate="now()")

    user = relationship("UserModel", back_populates="quickbooks_token")


class WithdrawalRequestModel(Base):
    __tablename__ = "withdrawal_requests"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), server_default="USD", nullable=False)
    method = Column(String(50), nullable=False)
    status = Column(String(50), server_default="pending", nullable=False, index=True)
    admin_notes = Column(Text)
    processed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)

    user = relationship("UserModel", back_populates="withdrawals")


class PayoutBatchModel(Base):
    __tablename__ = "payout_batches"

    id = Column(BigInteger, primary_key=True, index=True)
    batch_date = Column(DateTime(timezone=True), server_default="now()", nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), server_default="USD", nullable=False)
    status = Column(String(50), server_default="pending", nullable=False, index=True)
    processed_at = Column(DateTime(timezone=True))
    metadata = Column(JSONB)

    items = relationship("PayoutBatchItemModel", back_populates="batch", cascade="all, delete-orphan")


class PayoutBatchItemModel(Base):
    __tablename__ = "payout_batch_items"

    id = Column(BigInteger, primary_key=True, index=True)
    batch_id = Column(BigInteger, ForeignKey("payout_batches.id", ondelete="CASCADE"), nullable=False)
    withdrawal_id = Column(BigInteger, ForeignKey("withdrawal_requests.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(50), server_default="pending", nullable=False)
    error_message = Column(Text)

    batch = relationship("PayoutBatchModel", back_populates="items")
    withdrawal = relationship("WithdrawalRequestModel")


class WebhookEventModel(Base):
    __tablename__ = "webhook_events"

    id = Column(BigInteger, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)
    event_id = Column(String(255), nullable=False)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSONB, nullable=False)
    processed = Column(Boolean, server_default="false", nullable=False)
    processed_at = Column(DateTime(timezone=True))
    retry_count = Column(Integer, server_default="0", nullable=False)
    last_retry_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)

    __table_args__ = (UniqueConstraint("provider", "event_id", name="uq_webhook_event_provider_id"),)
    __table_args__ = (Index("ix_webhook_events_unprocessed", "provider", "processed", "created_at"),)


class BackgroundJobModel(Base):
    __tablename__ = "background_jobs"

    id = Column(BigInteger, primary_key=True, index=True)
    job_type = Column(String(100), nullable=False)
    status = Column(String(50), server_default="pending", nullable=False, index=True)
    params = Column(JSONB)
    result = Column(JSONB)
    error = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)

    __table_args__ = (Index("ix_background_jobs_status_type_created", "status", "job_type", "created_at"),)


class UserActivityLogModel(Base):
    __tablename__ = "user_activity_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(BigInteger)
    metadata = Column(JSONB)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)

    user = relationship("UserModel", back_populates="activity_logs")


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(BigInteger)
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default="now()", nullable=False)

    user = relationship("UserModel", back_populates="audit_logs")
