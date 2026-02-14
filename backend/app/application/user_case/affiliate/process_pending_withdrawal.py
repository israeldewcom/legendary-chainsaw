from dataclasses import dataclass
from datetime import datetime
from app.domain.repositories.withdrawal import WithdrawalRepository
from app.domain.repositories.payout_batch import PayoutBatchRepository
from app.application.use_cases.affiliate.create_payout import CreateAffiliatePayoutUseCase
from app.config import settings
import structlog

logger = structlog.get_logger()


@dataclass
class ProcessPendingWithdrawalsUseCase:
    withdrawal_repo: WithdrawalRepository
    payout_batch_repo: PayoutBatchRepository
    create_payout_use_case: CreateAffiliatePayoutUseCase

    async def execute(self) -> None:
        # Fetch pending withdrawals
        pending = await self.withdrawal_repo.get_pending()
        if not pending:
            return

        # Auto-approve those under threshold
        auto_approve = []
        manual = []
        for w in pending:
            if w.amount * 100 <= settings.AFFILIATE_AUTO_PAYOUT_THRESHOLD:
                auto_approve.append(w)
            else:
                manual.append(w)

        # Approve and add to payout batch
        for withdrawal in auto_approve:
            withdrawal.approve()
            await self.withdrawal_repo.save(withdrawal)
            await self.create_payout_use_case.execute(withdrawal.id, None)  # admin not needed

        logger.info("Processed pending withdrawals", auto_approved=len(auto_approve), manual=len(manual))
