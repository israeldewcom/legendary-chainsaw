from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional, List, Dict, Any
from app.domain.entities.user import User
from app.domain.entities.user_activity_log import UserActivityLog
from app.domain.repositories.user import UserRepository
from app.infrastructure.database.models import UserModel, UserActivityLogModel
from app.domain.value_objects.email import Email
from app.domain.value_objects.money import Money
import structlog

logger = structlog.get_logger()


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id, UserModel.deleted_at.is_(None))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email, UserModel.deleted_at.is_(None))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_verification_token(self, token: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email_verification_token == token, UserModel.deleted_at.is_(None))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_reset_token(self, token: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.password_reset_token == token, UserModel.deleted_at.is_(None))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_referral_code(self, code: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.referral_code == code, UserModel.deleted_at.is_(None))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_stripe_customer_id(self, customer_id: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.stripe_customer_id == customer_id, UserModel.deleted_at.is_(None))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_stripe_connect_account(self, account_id: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.stripe_connect_account_id == account_id, UserModel.deleted_at.is_(None))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, user: User) -> User:
        model = await self._to_model(user)
        self.session.add(model)
        await self.session.flush()
        user.id = model.id
        return user

    async def delete(self, user_id: int) -> None:
        # Soft delete
        await self.session.execute(
            update(UserModel).where(UserModel.id == user_id).values(deleted_at=datetime.utcnow(), is_active=False)
        )

    async def list(self, skip: int = 0, limit: int = 100, filters: Optional[dict] = None) -> List[User]:
        query = select(UserModel).where(UserModel.deleted_at.is_(None)).offset(skip).limit(limit)
        if filters:
            # Apply filters (simplified)
            pass
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def count(self, filters: Optional[dict] = None) -> int:
        query = select(UserModel).where(UserModel.deleted_at.is_(None))
        if filters:
            pass
        result = await self.session.execute(query)
        return len(result.scalars().all())

    async def log_activity(self, log: UserActivityLog) -> None:
        model = UserActivityLogModel(
            user_id=log.user_id,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            metadata=log.metadata,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            created_at=log.created_at,
        )
        self.session.add(model)
        await self.session.flush()

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=Email(model.email),
            email_verified=model.email_verified,
            email_verification_token=model.email_verification_token,
            password_reset_token=model.password_reset_token,
            password_reset_expires=model.password_reset_expires,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            company_name=model.company_name,
            is_active=model.is_active,
            is_superuser=model.is_superuser,
            mfa_secret=model.mfa_secret,
            mfa_enabled=model.mfa_enabled,
            mfa_recovery_codes=model.mfa_recovery_codes or [],
            failed_login_attempts=model.failed_login_attempts,
            locked_until=model.locked_until,
            last_login_at=model.last_login_at,
            last_active_at=model.last_active_at,
            preferences=model.preferences or {},
            timezone=model.timezone,
            subscription_tier=model.subscription_tier,
            subscription_status=model.subscription_status,
            stripe_customer_id=model.stripe_customer_id,
            stripe_subscription_id=model.stripe_subscription_id,
            monthly_transactions_used=model.monthly_transactions_used,
            monthly_transactions_limit=model.monthly_transactions_limit,
            trial_end_date=model.trial_end_date,
            referral_code=model.referral_code,
            referred_by_id=model.referred_by_id,
            affiliate_earnings=Money(model.affiliate_earnings or 0),
            affiliate_balance=Money(model.affiliate_balance or 0),
            affiliate_paid=Money(model.affiliate_paid or 0),
            stripe_connect_account_id=model.stripe_connect_account_id,
            paypal_email=model.paypal_email,
            payout_preference=model.payout_preference,
            data_export_requested_at=model.data_export_requested_at,
            data_exported_at=model.data_exported_at,
            data_export_key=model.data_export_key,
            deletion_requested_at=model.deletion_requested_at,
            deletion_scheduled_at=model.deletion_scheduled_at,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def _to_model(self, entity: User) -> UserModel:
        # If entity has id, load existing model to avoid overwriting fields
        if entity.id:
            result = await self.session.execute(select(UserModel).where(UserModel.id == entity.id))
            model = result.scalar_one_or_none()
            if model:
                # Update fields
                model.email = entity.email.value
                model.email_verified = entity.email_verified
                model.email_verification_token = entity.email_verification_token
                model.password_reset_token = entity.password_reset_token
                model.password_reset_expires = entity.password_reset_expires
                model.hashed_password = entity.hashed_password
                model.full_name = entity.full_name
                model.company_name = entity.company_name
                model.is_active = entity.is_active
                model.is_superuser = entity.is_superuser
                model.mfa_secret = entity.mfa_secret
                model.mfa_enabled = entity.mfa_enabled
                model.mfa_recovery_codes = entity.mfa_recovery_codes
                model.failed_login_attempts = entity.failed_login_attempts
                model.locked_until = entity.locked_until
                model.last_login_at = entity.last_login_at
                model.last_active_at = entity.last_active_at
                model.preferences = entity.preferences
                model.timezone = entity.timezone
                model.subscription_tier = entity.subscription_tier
                model.subscription_status = entity.subscription_status
                model.stripe_customer_id = entity.stripe_customer_id
                model.stripe_subscription_id = entity.stripe_subscription_id
                model.monthly_transactions_used = entity.monthly_transactions_used
                model.monthly_transactions_limit = entity.monthly_transactions_limit
                model.trial_end_date = entity.trial_end_date
                model.referral_code = entity.referral_code
                model.referred_by_id = entity.referred_by_id
                model.affiliate_earnings = entity.affiliate_earnings.amount
                model.affiliate_balance = entity.affiliate_balance.amount
                model.affiliate_paid = entity.affiliate_paid.amount
                model.stripe_connect_account_id = entity.stripe_connect_account_id
                model.paypal_email = entity.paypal_email
                model.payout_preference = entity.payout_preference
                model.data_export_requested_at = entity.data_export_requested_at
                model.data_exported_at = entity.data_exported_at
                model.data_export_key = entity.data_export_key
                model.deletion_requested_at = entity.deletion_requested_at
                model.deletion_scheduled_at = entity.deletion_scheduled_at
                model.deleted_at = entity.deleted_at
                return model

        # New entity
        return UserModel(
            id=entity.id,
            email=entity.email.value,
            email_verified=entity.email_verified,
            email_verification_token=entity.email_verification_token,
            password_reset_token=entity.password_reset_token,
            password_reset_expires=entity.password_reset_expires,
            hashed_password=entity.hashed_password,
            full_name=entity.full_name,
            company_name=entity.company_name,
            is_active=entity.is_active,
            is_superuser=entity.is_superuser,
            mfa_secret=entity.mfa_secret,
            mfa_enabled=entity.mfa_enabled,
            mfa_recovery_codes=entity.mfa_recovery_codes,
            failed_login_attempts=entity.failed_login_attempts,
            locked_until=entity.locked_until,
            last_login_at=entity.last_login_at,
            last_active_at=entity.last_active_at,
            preferences=entity.preferences,
            timezone=entity.timezone,
            subscription_tier=entity.subscription_tier,
            subscription_status=entity.subscription_status,
            stripe_customer_id=entity.stripe_customer_id,
            stripe_subscription_id=entity.stripe_subscription_id,
            monthly_transactions_used=entity.monthly_transactions_used,
            monthly_transactions_limit=entity.monthly_transactions_limit,
            trial_end_date=entity.trial_end_date,
            referral_code=entity.referral_code,
            referred_by_id=entity.referred_by_id,
            affiliate_earnings=entity.affiliate_earnings.amount,
            affiliate_balance=entity.affiliate_balance.amount,
            affiliate_paid=entity.affiliate_paid.amount,
            stripe_connect_account_id=entity.stripe_connect_account_id,
            paypal_email=entity.paypal_email,
            payout_preference=entity.payout_preference,
            data_export_requested_at=entity.data_export_requested_at,
            data_exported_at=entity.data_exported_at,
            data_export_key=entity.data_export_key,
            deletion_requested_at=entity.deletion_requested_at,
            deletion_scheduled_at=entity.deletion_scheduled_at,
            deleted_at=entity.deleted_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
