from dataclasses import dataclass
from datetime import datetime, timedelta
from app.domain.repositories.user import UserRepository
from app.domain.repositories.transaction import TransactionRepository
from app.application.interfaces.email_sender import EmailSender
import structlog

logger = structlog.get_logger()


@dataclass
class SendDailyDigestUseCase:
    user_repo: UserRepository
    transaction_repo: TransactionRepository
    email_sender: EmailSender

    async def execute(self) -> None:
        # Get users who have opted in for daily digest (via preferences)
        # In a real implementation, you'd query with a filter
        users = await self.user_repo.list(limit=10000)  # placeholder
        for user in users:
            if user.preferences.get("daily_digest", False):
                # Get yesterday's transactions
                yesterday = datetime.utcnow() - timedelta(days=1)
                start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
                end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
                tx_count = await self.transaction_repo.count_by_user_and_date_range(user.id, start, end)

                if tx_count > 0:
                    await self.email_sender.send_email(
                        to=[user.email.value],
                        subject="Your TaxFlow AI Daily Digest",
                        template_name="daily_digest.html",
                        template_context={
                            "full_name": user.full_name,
                            "transaction_count": tx_count,
                            "date": yesterday.strftime("%B %d, %Y"),
                        }
                    )
                    logger.info("Daily digest sent", user_id=user.id, count=tx_count)
