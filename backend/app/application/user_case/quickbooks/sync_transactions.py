from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import httpx
from app.domain.repositories.quickbooks_token import QuickBooksTokenRepository
from app.domain.repositories.transaction import TransactionRepository
from app.application.interfaces.event_bus import EventBus
from app.common.exceptions import BusinessError
from app.config import settings
import structlog

logger = structlog.get_logger()


@dataclass
class SyncTransactionsToQuickBooksUseCase:
    token_repo: QuickBooksTokenRepository
    transaction_repo: TransactionRepository
    event_bus: EventBus

    async def execute(self, user_id: int, client_ids: Optional[List[int]] = None) -> None:
        token = await self.token_repo.get_by_user_id(user_id)
        if not token:
            raise BusinessError("QuickBooks not connected")

        # Check if token is expired
        if token.is_expired():
            # In a real implementation, we would refresh using OAuth client
            # For now, raise error
            raise BusinessError("QuickBooks token expired, please reconnect")

        # Fetch transactions not yet exported
        filters = {"exported_at": None}
        if client_ids:
            filters["client_id__in"] = client_ids
        transactions = await self.transaction_repo.get_by_user_id(user_id, filters=filters, limit=1000)

        if not transactions:
            logger.info("No transactions to sync", user_id=user_id)
            return

        # Group by client? QuickBooks may require mapping to accounts
        # For simplicity, we'll just log
        logger.info("Syncing transactions to QuickBooks", user_id=user_id, count=len(transactions))

        # Actual API call to QuickBooks
        async with httpx.AsyncClient() as client:
            headers = {
                "Authorization": f"Bearer {token.access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            base_url = f"https://{settings.QUICKBOOKS_ENVIRONMENT}.quickbooks.api.intuit.com/v3/company/{token.realm_id}"
            for tx in transactions:
                # Convert to QuickBooks format (Purchase object)
                qb_data = {
                    "TotalAmt": float(tx.amount.amount),
                    "TxnDate": tx.date.strftime("%Y-%m-%d"),
                    "PrivateNote": tx.description,
                    "Line": [
                        {
                            "Amount": float(tx.amount.amount),
                            "Description": tx.description,
                            "DetailType": "AccountBasedExpenseLineDetail",
                            "AccountBasedExpenseLineDetail": {
                                "AccountRef": {
                                    "name": tx.category.value if tx.category else "Miscellaneous"
                                }
                            }
                        }
                    ]
                }
                response = await client.post(
                    f"{base_url}/purchase",
                    headers=headers,
                    json=qb_data,
                )
                if response.status_code == 200:
                    tx.mark_exported()
                    await self.transaction_repo.save(tx)
                else:
                    logger.error("QuickBooks sync failed", status=response.status_code, response=response.text)
                    # Optionally store error in transaction metadata
                    tx.metadata["quickbooks_error"] = response.text
                    await self.transaction_repo.save(tx)

        logger.info("QuickBooks sync completed", user_id=user_id)
