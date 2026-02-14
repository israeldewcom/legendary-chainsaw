"""Initial migration with all tables

Revision ID: 001
Revises:
Create Date: 2025-03-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, TSVECTOR
import pgvector

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('email_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('email_verification_token', sa.String(255), unique=True),
        sa.Column('password_reset_token', sa.String(255), unique=True),
        sa.Column('password_reset_expires', sa.DateTime(timezone=True)),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('company_name', sa.String(255)),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_superuser', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('mfa_secret', sa.String(255)),
        sa.Column('mfa_enabled', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('mfa_recovery_codes', ARRAY(sa.String(32)), server_default='{}', nullable=False),
        sa.Column('failed_login_attempts', sa.Integer(), server_default='0', nullable=False),
        sa.Column('locked_until', sa.DateTime(timezone=True)),
        sa.Column('last_login_at', sa.DateTime(timezone=True)),
        sa.Column('last_active_at', sa.DateTime(timezone=True)),
        sa.Column('preferences', JSONB, server_default='{}', nullable=False),
        sa.Column('timezone', sa.String(50), server_default='UTC', nullable=False),
        sa.Column('subscription_tier', sa.String(50), server_default='free', nullable=False),
        sa.Column('subscription_status', sa.String(50), server_default='active', nullable=False),
        sa.Column('stripe_customer_id', sa.String(255), unique=True),
        sa.Column('stripe_subscription_id', sa.String(255), unique=True),
        sa.Column('monthly_transactions_used', sa.Integer(), server_default='0', nullable=False),
        sa.Column('monthly_transactions_limit', sa.Integer(), server_default='100', nullable=False),
        sa.Column('trial_end_date', sa.DateTime(timezone=True)),
        sa.Column('referral_code', sa.String(50), unique=True, nullable=False),
        sa.Column('referred_by_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('affiliate_earnings', sa.Numeric(12, 2), server_default='0', nullable=False),
        sa.Column('affiliate_balance', sa.Numeric(12, 2), server_default='0', nullable=False),
        sa.Column('affiliate_paid', sa.Numeric(12, 2), server_default='0', nullable=False),
        sa.Column('stripe_connect_account_id', sa.String(255), unique=True),
        sa.Column('paypal_email', sa.String(255)),
        sa.Column('payout_preference', sa.String(50), server_default='stripe_connect', nullable=False),
        sa.Column('data_export_requested_at', sa.DateTime(timezone=True)),
        sa.Column('data_exported_at', sa.DateTime(timezone=True)),
        sa.Column('data_export_key', sa.String(255)),
        sa.Column('deletion_requested_at', sa.DateTime(timezone=True)),
        sa.Column('deletion_scheduled_at', sa.DateTime(timezone=True)),
        sa.Column('deleted_at', sa.DateTime(timezone=True)),  # soft delete
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Clients table
    op.create_table(
        'clients',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255)),
        sa.Column('phone', sa.String(50)),
        sa.Column('address', sa.Text()),
        sa.Column('tax_year', sa.Integer()),
        sa.Column('filing_status', sa.String(50)),
        sa.Column('ein', sa.String(20)),
        sa.Column('industry', sa.String(100)),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('client_id', sa.BigInteger(), sa.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),  # denormalised for performance
        sa.Column('date', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), server_default='USD', nullable=False),
        sa.Column('category', sa.String(100)),
        sa.Column('subcategory', sa.String(100)),
        sa.Column('confidence', sa.Float()),
        sa.Column('status', sa.String(50), server_default='pending', nullable=False, index=True),
        sa.Column('reviewed', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('user_override', sa.String(100)),
        sa.Column('vendor', sa.String(255)),
        sa.Column('receipt_id', sa.BigInteger(), sa.ForeignKey('receipts.id', ondelete='SET NULL')),
        sa.Column('embedding', pgvector.VECTOR(1536)),  # OpenAI embedding dimension
        sa.Column('metadata', JSONB, server_default='{}', nullable=False),
        sa.Column('tax_year', sa.Integer()),
        sa.Column('tags', ARRAY(sa.String(50)), server_default='{}', nullable=False),
        sa.Column('is_duplicate', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('parent_id', sa.BigInteger(), sa.ForeignKey('transactions.id', ondelete='SET NULL')),
        sa.Column('reconciled', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('exported_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Receipts table
    op.create_table(
        'receipts',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('client_id', sa.BigInteger(), sa.ForeignKey('clients.id', ondelete='SET NULL')),
        sa.Column('filename', sa.String(255)),
        sa.Column('s3_key', sa.String(255), unique=True),
        sa.Column('ocr_text', sa.Text()),
        sa.Column('extracted_data', JSONB),
        sa.Column('status', sa.String(50), server_default='pending', nullable=False, index=True),
        sa.Column('error_message', sa.Text()),
        sa.Column('file_size', sa.Integer()),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('page_count', sa.Integer()),
        sa.Column('processed_at', sa.DateTime(timezone=True)),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('transaction_id', sa.BigInteger(), sa.ForeignKey('transactions.id', ondelete='SET NULL')),
    )

    # Subscriptions table (for historical tracking)
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('stripe_subscription_id', sa.String(255), unique=True),
        sa.Column('stripe_customer_id', sa.String(255)),
        sa.Column('plan_id', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('current_period_start', sa.DateTime(timezone=True)),
        sa.Column('current_period_end', sa.DateTime(timezone=True)),
        sa.Column('cancel_at_period_end', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('canceled_at', sa.DateTime(timezone=True)),
        sa.Column('trial_start', sa.DateTime(timezone=True)),
        sa.Column('trial_end', sa.DateTime(timezone=True)),
        sa.Column('coupon_id', sa.BigInteger(), sa.ForeignKey('coupons.id', ondelete='SET NULL')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Invoices table
    op.create_table(
        'invoices',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('stripe_invoice_id', sa.String(255), unique=True),
        sa.Column('invoice_number', sa.String(255)),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), server_default='USD', nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('invoice_pdf', sa.String(255)),
        sa.Column('due_date', sa.DateTime(timezone=True)),
        sa.Column('paid_at', sa.DateTime(timezone=True)),
        sa.Column('paid', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('tax_amount', sa.Numeric(12, 2), server_default='0', nullable=False),
        sa.Column('tax_rate', sa.Numeric(5, 2)),
        sa.Column('tax_country', sa.String(2)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Coupons table
    op.create_table(
        'coupons',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('description', sa.String(255)),
        sa.Column('discount_type', sa.String(20), nullable=False),  # percentage, fixed
        sa.Column('discount_amount', sa.Numeric(10, 2)),
        sa.Column('duration', sa.String(20), server_default='once', nullable=False),  # once, repeating, forever
        sa.Column('duration_in_months', sa.Integer()),
        sa.Column('max_redemptions', sa.Integer()),
        sa.Column('redeemed_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('valid_from', sa.DateTime(timezone=True)),
        sa.Column('valid_until', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Teams
    op.create_table(
        'teams',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('owner_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        'team_members',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('team_id', sa.BigInteger(), sa.ForeignKey('teams.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(50), server_default='member', nullable=False),  # admin, member, viewer
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('team_id', 'user_id', name='uq_team_members_team_user'),
    )

    # User sessions
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('session_token', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(255)),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Notifications
    op.create_table(
        'notifications',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('type', sa.String(50), nullable=False),  # info, success, warning, error
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text()),
        sa.Column('link', sa.String(255)),
        sa.Column('read_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # QuickBooks tokens
    op.create_table(
        'quickbooks_tokens',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True),
        sa.Column('realm_id', sa.String(100), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Withdrawal requests
    op.create_table(
        'withdrawal_requests',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), server_default='USD', nullable=False),
        sa.Column('method', sa.String(50), nullable=False),  # stripe_connect, paypal, bank_transfer
        sa.Column('status', sa.String(50), server_default='pending', nullable=False, index=True),
        sa.Column('admin_notes', sa.Text()),
        sa.Column('processed_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Payout batches
    op.create_table(
        'payout_batches',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('batch_date', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('total_amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), server_default='USD', nullable=False),
        sa.Column('status', sa.String(50), server_default='pending', nullable=False, index=True),
        sa.Column('processed_at', sa.DateTime(timezone=True)),
        sa.Column('metadata', JSONB),
    )

    op.create_table(
        'payout_batch_items',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('batch_id', sa.BigInteger(), sa.ForeignKey('payout_batches.id', ondelete='CASCADE'), nullable=False),
        sa.Column('withdrawal_id', sa.BigInteger(), sa.ForeignKey('withdrawal_requests.id', ondelete='CASCADE'), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('status', sa.String(50), server_default='pending', nullable=False),
        sa.Column('error_message', sa.Text()),
    )

    # Webhook events (idempotency)
    op.create_table(
        'webhook_events',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('event_id', sa.String(255), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('payload', JSONB, nullable=False),
        sa.Column('processed', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True)),
        sa.Column('retry_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('last_retry_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('provider', 'event_id', name='uq_webhook_event_provider_id'),
        sa.Index('ix_webhook_events_unprocessed', 'provider', 'processed', 'created_at'),
    )

    # Background jobs
    op.create_table(
        'background_jobs',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('job_type', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), server_default='pending', nullable=False, index=True),
        sa.Column('params', JSONB),
        sa.Column('result', JSONB),
        sa.Column('error', sa.Text()),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Index('ix_background_jobs_status_type_created', 'status', 'job_type', 'created_at'),
    )

    # User activity logs (for analytics)
    op.create_table(
        'user_activity_logs',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50)),
        sa.Column('entity_id', sa.BigInteger()),
        sa.Column('metadata', JSONB),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(255)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_user_activity_logs_user_id_created', 'user_activity_logs', ['user_id', 'created_at'])
    op.create_index('ix_user_activity_logs_action_created', 'user_activity_logs', ['action', 'created_at'])

    # Audit logs (for compliance)
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.BigInteger(), primary_key=True, index=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', sa.BigInteger()),
        sa.Column('old_values', JSONB),
        sa.Column('new_values', JSONB),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(255)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])

    # Add foreign key to transactions.receipt_id after receipts table created
    op.create_foreign_key('fk_transactions_receipt_id', 'transactions', 'receipts', ['receipt_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('user_activity_logs')
    op.drop_table('background_jobs')
    op.drop_table('webhook_events')
    op.drop_table('payout_batch_items')
    op.drop_table('payout_batches')
    op.drop_table('withdrawal_requests')
    op.drop_table('quickbooks_tokens')
    op.drop_table('notifications')
    op.drop_table('user_sessions')
    op.drop_table('team_members')
    op.drop_table('teams')
    op.drop_table('coupons')
    op.drop_table('invoices')
    op.drop_table('subscriptions')
    op.drop_table('transactions')
    op.drop_table('receipts')
    op.drop_table('clients')
    op.drop_table('users')
    op.execute('DROP EXTENSION IF EXISTS vector')
