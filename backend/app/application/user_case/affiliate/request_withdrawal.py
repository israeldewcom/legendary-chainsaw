from dataclasses import dataclass
from decimal import Decimal
from app.domain.entities.withdrawal import WithdrawalRequest
from app.domain.repositories.withdrawal import WithdrawalRepository
from app.domain.repositories.user import UserRepository
from app.domain.value_objects.money import Money
from app.application.interfaces.event_bus import EventBus
from app.common.exceptions import BusinessError, NotFoundError
from app.config import settings
import structlog

logger = structlog.get_logger()


@dataclass
class RequestWithdrawalUseCase:
    user_repo: UserRepository
    withdrawal_repo: WithdrawalRepository
    event_bus: EventBus

    async def execute(self, user_id: int, amount: Decimal, method: str, currency: str = "USD") -> WithdrawalRequest:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Check minimum withdrawal
        min_amount = Money(settings.AFFILIATE_MIN_WITHDRAWAL / 100)
        if amount < min_amount.amount:
            raise BusinessError(f"Minimum withdrawal amount is {min_amount}")

        # Check balance
        if user.affiliate_balance.amount < amount:
            raise BusinessError("Insufficient balance")

        # Create withdrawal request
        withdrawal = WithdrawalRequest(
            user_id=user_id,
            amount=amount,
            currency=currency,
            method=method,
        )
        saved = await self.withdrawal_repo.save(withdrawal)

        # Debit user balance
        user.debit_affiliate_balance(Money(amount))
        await self.user_repo.save(user)

        # Publish event
        await self.event_bus.publish(withdrawal.collect_events()? Actually WithdrawalRequest doesn't have events yet; we'll add event later.
        # For now, we can manually publish an event.
        from app.domain.events.domain_events import WithdrawalRequested
        await self.event_bus.publish(WithdrawalRequested(
            user_id=user_id,
            withdrawal_id=saved.id,
            amount=Money(amount)
        ))

        logger.info("Withdrawal requested", user_id=user_id, withdrawal_id=saved.id, amount=amount)
        return saved
