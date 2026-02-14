from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal


@dataclass
class UserResponseDTO:
    id: int
    email: str
    full_name: Optional[str]
    company_name: Optional[str]
    is_active: bool
    is_superuser: bool
    mfa_enabled: bool
    subscription_tier: str
    subscription_status: str
    monthly_transactions_used: int
    monthly_transactions_limit: int
    trial_end_date: Optional[datetime]
    referral_code: str
    affiliate_earnings: Decimal
    affiliate_balance: Decimal
    affiliate_paid: Decimal
    stripe_connect_account_id: Optional[str]
    paypal_email: Optional[str]
    payout_preference: str
    data_exported_at: Optional[datetime]
    created_at: datetime


@dataclass
class UserCreateDTO:
    email: str
    password: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    referral_code: Optional[str] = None


@dataclass
class UserUpdateDTO:
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None
    paypal_email: Optional[str] = None
    payout_preference: Optional[str] = None


@dataclass
class ClientResponseDTO:
    id: int
    user_id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    tax_year: Optional[int]
    filing_status: Optional[str]
    ein: Optional[str]
    industry: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


@dataclass
class ClientCreateDTO:
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_year: Optional[int] = None
    filing_status: Optional[str] = None
    ein: Optional[str] = None
    industry: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ClientUpdateDTO:
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_year: Optional[int] = None
    filing_status: Optional[str] = None
    ein: Optional[str] = None
    industry: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class TransactionResponseDTO:
    id: int
    client_id: int
    user_id: int
    date: datetime
    description: str
    amount: Decimal
    currency: str
    category: Optional[str]
    subcategory: Optional[str]
    confidence: Optional[float]
    status: str
    reviewed: bool
    user_override: Optional[str]
    vendor: Optional[str]
    receipt_id: Optional[int]
    tags: List[str]
    is_duplicate: bool
    parent_id: Optional[int]
    reconciled: bool
    exported_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]


@dataclass
class TransactionCreateDTO:
    client_id: int
    date: datetime
    description: str
    amount: Decimal
    currency: str = "USD"
    category: Optional[str] = None
    vendor: Optional[str] = None
    receipt_id: Optional[int] = None
    tags: Optional[List[str]] = None


@dataclass
class TransactionUpdateDTO:
    date: Optional[datetime] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    category: Optional[str] = None
    vendor: Optional[str] = None
    receipt_id: Optional[int] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    reviewed: Optional[bool] = None


@dataclass
class ReceiptResponseDTO:
    id: int
    user_id: int
    client_id: Optional[int]
    filename: Optional[str]
    s3_key: Optional[str]
    status: str
    error_message: Optional[str]
    file_size: Optional[int]
    mime_type: Optional[str]
    page_count: Optional[int]
    processed_at: Optional[datetime]
    uploaded_at: datetime
    transaction_id: Optional[int]


@dataclass
class ReceiptUploadDTO:
    client_id: Optional[int] = None
    transaction_id: Optional[int] = None


@dataclass
class SubscriptionResponseDTO:
    id: int
    user_id: int
    stripe_subscription_id: Optional[str]
    plan_id: str
    status: str
    current_period_start: Optional[datetime]
    current_period_end: Optional[datetime]
    cancel_at_period_end: bool
    canceled_at: Optional[datetime]
    trial_start: Optional[datetime]
    trial_end: Optional[datetime]
    coupon_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]


@dataclass
class InvoiceResponseDTO:
    id: int
    user_id: int
    stripe_invoice_id: Optional[str]
    invoice_number: Optional[str]
    amount: Decimal
    currency: str
    status: str
    invoice_pdf: Optional[str]
    due_date: Optional[datetime]
    paid_at: Optional[datetime]
    paid: bool
    tax_amount: Decimal
    tax_rate: Optional[Decimal]
    tax_country: Optional[str]
    created_at: datetime


@dataclass
class WithdrawalResponseDTO:
    id: int
    user_id: int
    amount: Decimal
    currency: str
    method: str
    status: str
    admin_notes: Optional[str]
    processed_at: Optional[datetime]
    created_at: datetime


@dataclass
class WithdrawalRequestDTO:
    amount: Decimal
    method: str
    currency: str = "USD"


@dataclass
class WithdrawalApproveDTO:
    admin_notes: Optional[str] = None


@dataclass
class WithdrawalRejectDTO:
    reason: str


@dataclass
class NotificationResponseDTO:
    id: int
    user_id: int
    type: str
    title: str
    content: Optional[str]
    link: Optional[str]
    read_at: Optional[datetime]
    created_at: datetime


@dataclass
class ActivityLogResponseDTO:
    id: int
    user_id: int
    action: str
    entity_type: Optional[str]
    entity_id: Optional[int]
    metadata: Optional[Dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime


@dataclass
class AuditLogResponseDTO:
    id: int
    user_id: Optional[int]
    action: str
    entity_type: str
    entity_id: Optional[int]
    old_values: Optional[Dict]
    new_values: Optional[Dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime


@dataclass
class TeamResponseDTO:
    id: int
    owner_id: int
    name: str
    slug: str
    created_at: datetime


@dataclass
class TeamCreateDTO:
    name: str
    slug: Optional[str] = None


@dataclass
class TeamMemberResponseDTO:
    id: int
    team_id: int
    user_id: int
    role: str
    created_at: datetime
    user_email: Optional[str] = None
    user_name: Optional[str] = None


@dataclass
class TeamMemberInviteDTO:
    email: str
    role: str = "member"


@dataclass
class CouponResponseDTO:
    id: int
    code: str
    description: Optional[str]
    discount_type: str
    discount_amount: Optional[Decimal]
    duration: str
    duration_in_months: Optional[int]
    max_redemptions: Optional[int]
    redeemed_count: int
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    created_at: datetime


@dataclass
class CouponCreateDTO:
    code: str
    discount_type: str
    discount_amount: Decimal
    description: Optional[str] = None
    duration: str = "once"
    duration_in_months: Optional[int] = None
    max_redemptions: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


@dataclass
class QuickBooksAuthUrlDTO:
    url: str


@dataclass
class QuickBooksTokenResponseDTO:
    connected: bool
    realm_id: Optional[str]
    expires_at: Optional[datetime]


@dataclass
class ExportRequestDTO:
    format: str = "csv"  # csv, excel, pdf
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    client_ids: Optional[List[int]] = None
    categories: Optional[List[str]] = None
    include_receipts: bool = False


@dataclass
class ExportResponseDTO:
    export_id: str
    status: str
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None


@dataclass
class SearchQueryDTO:
    q: str
    type: Optional[str] = None  # transactions, clients, receipts
    limit: int = 10
    offset: int = 0


@dataclass
class SearchResultDTO:
    id: int
    type: str
    title: str
    description: Optional[str]
    url: str
    score: float
