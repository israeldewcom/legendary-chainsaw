from dataclasses import dataclass
from typing import Dict, Any
from app.domain.repositories.user import UserRepository
from app.domain.repositories.notification import NotificationRepository
from app.domain.entities.notification import Notification
import structlog

logger = structlog.get_logger()


@dataclass
class EmailBounceWebhookUseCase:
    user_repo: UserRepository
    notif_repo: NotificationRepository

    async def execute(self, payload: Dict[str, Any]) -> None:
        # Parse payload (SendGrid format)
        email = payload.get("email")
        event_type = payload.get("event")  # bounce, dropped, etc.
        reason = payload.get("reason")

        if not email:
            logger.warning("Email bounce webhook missing email")
            return

        # Find user by email
        user = await self.user_repo.get_by_email(email)
        if not user:
            logger.warning("User not found for bounced email", email=email)
            return

        # Create notification
        notification = Notification(
            user_id=user.id,
            type="warning",
            title="Email Delivery Issue",
            content=f"We encountered an issue delivering emails to {email}. Reason: {reason}. Please update your email address if needed.",
        )
        await self.notif_repo.save(notification)

        # Optionally mark email as invalid in user preferences
        if "preferences" not in user.preferences:
            user.preferences = {}
        user.preferences["email_bounced"] = True
        user.preferences["email_bounce_reason"] = reason
        user.preferences["email_bounce_at"] = datetime.utcnow().isoformat()
        await self.user_repo.save(user)

        logger.info("Email bounce recorded", user_id=user.id, email=email, reason=reason)
