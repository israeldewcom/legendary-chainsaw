from dataclasses import dataclass
from datetime import datetime
from app.domain.repositories.user import UserRepository
from app.domain.repositories.client import ClientRepository
from app.domain.repositories.transaction import TransactionRepository
from app.domain.repositories.receipt import ReceiptRepository
from app.application.interfaces.storage import Storage
from app.common.exceptions import NotFoundError
from app.config import settings
import structlog

logger = structlog.get_logger()


@dataclass
class DeleteUserDataUseCase:
    user_repo: UserRepository
    client_repo: ClientRepository
    transaction_repo: TransactionRepository
    receipt_repo: ReceiptRepository
    storage: Storage

    async def execute(self, user_id: int) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Check if grace period has passed
        if user.deletion_scheduled_at and user.deletion_scheduled_at <= datetime.utcnow():
            # Delete receipts from S3
            receipts = await self.receipt_repo.get_by_user_id(user_id)
            for receipt in receipts:
                if receipt.s3_key:
                    await self.storage.delete(settings.AWS_S3_BUCKET, receipt.s3_key)

            # Delete user (cascade will handle related data)
            await self.user_repo.delete(user_id)
            logger.info("User data permanently deleted", user_id=user_id)
        else:
            logger.info("User deletion not yet scheduled", user_id=user_id)
