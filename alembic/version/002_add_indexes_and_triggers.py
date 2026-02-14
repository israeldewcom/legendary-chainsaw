"""Add additional indexes and triggers

Revision ID: 002
Revises: 001
Create Date: 2025-03-15 11:00:00.000000

"""
from alembic import op

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Additional indexes for performance
    op.create_index('ix_transactions_client_id_date', 'transactions', ['client_id', 'date'])
    op.create_index('ix_transactions_user_id_date', 'transactions', ['user_id', 'date'])
    op.create_index('ix_transactions_category_confidence', 'transactions', ['category', 'confidence'])
    op.create_index('ix_transactions_status_created', 'transactions', ['status', 'created_at'])
    op.create_index('ix_receipts_user_id_uploaded_at', 'receipts', ['user_id', 'uploaded_at'])
    op.create_index('ix_receipts_status_uploaded_at', 'receipts', ['status', 'uploaded_at'])
    op.create_index('ix_clients_user_id_name', 'clients', ['user_id', 'name'])

    # Partial index for active sessions
    op.execute('''
        CREATE INDEX ix_user_sessions_active
        ON user_sessions (user_id, expires_at)
        WHERE expires_at > NOW()
    ''')

    # Partial index for pending withdrawals
    op.execute('''
        CREATE INDEX ix_withdrawal_requests_pending
        ON withdrawal_requests (created_at)
        WHERE status = 'pending'
    ''')

    # Full‑text search index on transactions.description
    op.execute('''
        CREATE INDEX ix_transactions_description_gin
        ON transactions USING gin(to_tsvector('english', description));
    ''')

    # GIN index on tags
    op.create_index('ix_transactions_tags_gin', 'transactions', ['tags'], postgresql_using='gin')

    # GIN index on metadata
    op.create_index('ix_transactions_metadata_gin', 'transactions', ['metadata'], postgresql_using='gin')

    # Trigger to update updated_at columns
    op.execute('''
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    ''')

    tables = ['users', 'clients', 'transactions', 'subscriptions', 'quickbooks_tokens', 'teams', 'team_members']
    for table in tables:
        op.execute(f'''
            CREATE TRIGGER update_{table}_updated_at
                BEFORE UPDATE ON {table}
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        ''')


def downgrade() -> None:
    op.drop_index('ix_transactions_client_id_date')
    op.drop_index('ix_transactions_user_id_date')
    op.drop_index('ix_transactions_category_confidence')
    op.drop_index('ix_transactions_status_created')
    op.drop_index('ix_receipts_user_id_uploaded_at')
    op.drop_index('ix_receipts_status_uploaded_at')
    op.drop_index('ix_clients_user_id_name')
    op.execute('DROP INDEX IF EXISTS ix_user_sessions_active')
    op.execute('DROP INDEX IF EXISTS ix_withdrawal_requests_pending')
    op.execute('DROP INDEX IF EXISTS ix_transactions_description_gin')
    op.drop_index('ix_transactions_tags_gin')
    op.drop_index('ix_transactions_metadata_gin')
    for table in ['users', 'clients', 'transactions', 'subscriptions', 'quickbooks_tokens', 'teams', 'team_members']:
        op.execute(f'DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}')
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column')
