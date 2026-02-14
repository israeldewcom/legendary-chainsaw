from dataclasses import dataclass
from typing import List
from app.domain.repositories.transaction import TransactionRepository
from app.application.use_cases.transactions.categorize import CategorizeTransactionUseCase
import structlog

logger = structlog.get_logger()


@dataclass
class BulkCategorizeUseCase:
    transaction_repo: TransactionRepository
    categorize_use_case: CategorizeTransactionUseCase

    async def execute(self, transaction_ids: List[int], user_id: int) -> None:
        # Verify all transactions belong to user
        for tid in transaction_ids:
            tx = await self.transaction_repo.get_by_id(tid, user_id)
            if not tx:
                logger.warning("Transaction not found for bulk categorize", transaction_id=tid, user_id=user_id)
                continue
            # Run categorization (could be parallelized)
            await self.categorize_use_case.execute(tid, user_id)
