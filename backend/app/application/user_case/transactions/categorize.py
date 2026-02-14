from dataclasses import dataclass
from typing import Optional
from app.domain.repositories.transaction import TransactionRepository
from app.domain.repositories.client import ClientRepository
from app.domain.value_objects.tax_category import TaxCategory
from app.application.interfaces.ai_categorizer import AICategorizer
from app.application.interfaces.event_bus import EventBus
from app.common.exceptions import NotFoundError, BusinessError
import structlog

logger = structlog.get_logger()


@dataclass
class CategorizeTransactionUseCase:
    transaction_repo: TransactionRepository
    client_repo: ClientRepository
    ai_categorizer: AICategorizer
    event_bus: EventBus

    async def execute(self, transaction_id: int, user_id: int, force: bool = False) -> None:
        transaction = await self.transaction_repo.get_by_id(transaction_id, user_id)
        if not transaction:
            raise NotFoundError("Transaction not found")

        # Don't recategorize if already reviewed and not forced
        if transaction.reviewed and not force:
            return

        # Get client for context
        client = await self.client_repo.get_by_id(transaction.client_id, user_id)

        # Use AI to categorize
        category, subcategory, confidence = await self.ai_categorizer.categorize(
            description=transaction.description,
            amount=float(transaction.amount.amount),
            vendor=transaction.vendor,
            client_industry=client.industry if client else None,
        )

        # Update transaction
        transaction.categorize(TaxCategory(category), subcategory, confidence)
        await self.transaction_repo.save(transaction)

        # Publish events
        for event in transaction.collect_events():
            await self.event_bus.publish(event)

        logger.info("Transaction categorized", transaction_id=transaction_id, category=category, confidence=confidence)
