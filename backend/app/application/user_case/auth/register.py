from dataclasses import dataclass
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.repositories.user import UserRepository
from app.application.interfaces.password_hasher import PasswordHasher
from app.application.interfaces.event_bus import EventBus
from app.application.dtos import UserCreateDTO, UserResponseDTO
from app.common.exceptions import BusinessError
import structlog

logger = structlog.get_logger()


@dataclass
class RegisterUseCase:
    user_repo: UserRepository
    password_hasher: PasswordHasher
    event_bus: EventBus

    async def execute(self, dto: UserCreateDTO) -> UserResponseDTO:
        # Check if user exists
        existing = await self.user_repo.get_by_email(dto.email)
        if existing:
            raise BusinessError("User with this email already exists")

        # Create user entity
        email = Email(dto.email)
        user = User(email=email, full_name=dto.full_name, company_name=dto.company_name)

        # Hash password and register
        hashed = self.password_hasher.hash(dto.password)
        user.register(hashed, dto.referral_code)

        # Save
        saved_user = await self.user_repo.save(user)

        # Publish events
        for event in user.collect_events():
            await self.event_bus.publish(event)

        logger.info("User registered", user_id=saved_user.id, email=email.value)

        # Return DTO
        return UserResponseDTO(
            id=saved_user.id,
            email=saved_user.email.value,
            full_name=saved_user.full_name,
            company_name=saved_user.company_name,
            is_active=saved_user.is_active,
            is_superuser=saved_user.is_superuser,
            mfa_enabled=saved_user.mfa_enabled,
            subscription_tier=saved_user.subscription_tier,
            subscription_status=saved_user.subscription_status,
            monthly_transactions_used=saved_user.monthly_transactions_used,
            monthly_transactions_limit=saved_user.monthly_transactions_limit,
            trial_end_date=saved_user.trial_end_date,
            referral_code=saved_user.referral_code,
            affiliate_earnings=saved_user.affiliate_earnings.amount,
            affiliate_balance=saved_user.affiliate_balance.amount,
            affiliate_paid=saved_user.affiliate_paid.amount,
            stripe_connect_account_id=saved_user.stripe_connect_account_id,
            paypal_email=saved_user.paypal_email,
            payout_preference=saved_user.payout_preference,
            data_exported_at=saved_user.data_exported_at,
            created_at=saved_user.created_at,
        )
