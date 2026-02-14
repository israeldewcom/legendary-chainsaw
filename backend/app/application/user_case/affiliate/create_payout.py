from dataclasses import dataclass
from typing import Optional
from app.domain.repositories.withdrawal import WithdrawalRepository
from app.domain.repositories.user import UserRepository
from app.domain.repositories.payout_batch import PayoutBatchRepository
from app.domain.entities.payout_batch import PayoutBatch, PayoutBatchItem
from app.application.interfaces.stripe_connect import StripeConnectService
from app.application.interfaces.event_bus import EventBus
from app.common.exceptions import NotFoundError, BusinessError
import structlog

logger = structlog.get_logger()


@dataclass
class CreateAffiliatePayoutUseCase:
    withdrawal_repo: WithdrawalRepository
    user_repo: UserRepository
    payout_batch_repo: PayoutBatchRepository
    stripe_connect: StripeConnectService
    event_bus: EventBus

    async def execute(self, withdrawal_id: int, admin_id: Optional[int] = None) -> None:
        withdrawal = await self.withdrawal_repo.get_by_id(withdrawal_id)
        if not withdrawal:
            raise NotFoundError("Withdrawal not found")

        if withdrawal.status != "approved":
            raise BusinessError("Withdrawal is not approved")

        user = await self.user_repo.get_by_id(withdrawal.user_id)
        if not user:
            raise NotFoundError("User not found")

        # Determine payout method
        if withdrawal.method == "stripe_connect":
            if not user.stripe_connect_account_id:
                raise BusinessError("User has no Stripe Connect account")
            # Transfer via Stripe Connect
            transfer = await self.stripe_connect.create_transfer(
                amount=int(withdrawal.amount * 100),
                currency=withdrawal.currency.lower(),
                destination=user.stripe_connect_account_id,
                metadata={"withdrawal_id": withdrawal.id},
            )
            # Mark as paid
            withdrawal.mark_paid()
            await self.withdrawal_repo.save(withdrawal)

            # Publish event
            from app.domain.events.domain_events import WithdrawalPaid
            await self.event_bus.publish(WithdrawalPaid(
                withdrawal_id=withdrawal.id,
                user_id=user.id,
                amount=withdrawal.amount
            ))

        elif withdrawal.method in ["paypal", "bank_transfer"]:
            # For now, add to payout batch for manual processing
            batch = await self.payout_batch_repo.get_pending_batch()
            if not batch:
                batch = PayoutBatch(
                    total_amount=withdrawal.amount,
                    currency=withdrawal.currency,
                )
                batch = await self.payout_batch_repo.create_batch(batch)
            else:
                batch.total_amount += withdrawal.amount

            item = PayoutBatchItem(
                batch_id=batch.id,
                withdrawal_id=withdrawal.id,
                amount=withdrawal.amount,
            )
            await self.payout_batch_repo.add_item(item)

            # Update withdrawal status to 'processing' or leave as approved
            # We'll keep as approved until batch processed
            logger.info("Added withdrawal to payout batch", withdrawal_id=withdrawal.id, batch_id=batch.id)

        else:
            raise BusinessError(f"Unsupported payout method: {withdrawal.method}")

        logger.info("Affiliate payout created", withdrawal_id=withdrawal.id, user_id=user.id, amount=withdrawal.amount)
