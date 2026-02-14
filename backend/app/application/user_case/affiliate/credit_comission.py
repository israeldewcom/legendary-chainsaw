from dataclasses import dataclass
from decimal import Decimal
from app.domain.repositories.user import UserRepository
from app.domain.value_objects.money import Money
from app.application.interfaces.event_bus import EventBus
from app.common.exceptions import NotFoundError
import structlog

logger = structlog.get_logger()


@dataclass
class CreditAffiliateCommissionUseCase:
    user_repo: UserRepository
    event_bus: EventBus

    async def execute(self, user_id: int, amount: Decimal) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        money = Money(amount)
        user.credit_affiliate_commission(money)
        await self.user_repo.save(user)

        for event in user.collect_events():
            await self.event_bus.publish(event)

        logger.info("Affiliate commission credited", user_id=user_id, amount=amount)
