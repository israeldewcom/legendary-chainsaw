from app.infrastructure.event_bus.redis_event_bus import RedisEventBus
from app.domain.events.domain_events import (
    UserRegistered, UserActivityLogged, AffiliateCommissionCredited,
    WithdrawalRequested, WithdrawalApproved, WithdrawalPaid,
    TransactionCategorized, ReceiptProcessed, UserSubscribed
)
from app.infrastructure.database.session import sessionmanager
from app.infrastructure.database.repositories.user import SQLAlchemyUserRepository
from app.infrastructure.database.repositories.notification import SQLAlchemyNotificationRepository
from app.infrastructure.email.smtp_sender import SMTPEmailSender
from app.infrastructure.analytics.mixpanel import MixpanelClient
from app.config import settings
import structlog

logger = structlog.get_logger()


async def register_handlers(event_bus: RedisEventBus):
    event_bus.subscribe(UserRegistered, handle_user_registered)
    event_bus.subscribe(UserActivityLogged, handle_user_activity_logged)
    event_bus.subscribe(AffiliateCommissionCredited, handle_affiliate_commission)
    event_bus.subscribe(WithdrawalRequested, handle_withdrawal_requested)
    event_bus.subscribe(WithdrawalApproved, handle_withdrawal_approved)
    event_bus.subscribe(WithdrawalPaid, handle_withdrawal_paid)
    event_bus.subscribe(TransactionCategorized, handle_transaction_categorized)
    event_bus.subscribe(ReceiptProcessed, handle_receipt_processed)
    event_bus.subscribe(UserSubscribed, handle_user_subscribed)
    logger.info("Event handlers registered")


async def handle_user_registered(event: UserRegistered):
    # Send welcome email
    email_sender = SMTPEmailSender()
    verification_link = f"{settings.FRONTEND_URL}/verify-email?token={event.verification_token}"
    await email_sender.send_email(
        to=[event.email],
        subject="Welcome to TaxFlow AI",
        template_name="welcome.html",
        template_context={"verification_link": verification_link}
    )
    # Track in analytics
    if settings.MIXPANEL_TOKEN:
        mixpanel = MixpanelClient()
        mixpanel.track(event.user_id, "User Registered", {"email": event.email})
    logger.info("Welcome email sent", user_id=event.user_id)


async def handle_user_activity_logged(event: UserActivityLogged):
    # Store in database
    async with sessionmanager.session_factory() as session:
        user_repo = SQLAlchemyUserRepository(session)
        from app.domain.entities.user_activity_log import UserActivityLog
        log = UserActivityLog(
            user_id=event.user_id,
            action=event.action,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            metadata=event.metadata,
            ip_address=event.ip_address,
            user_agent=event.user_agent,
            created_at=event.occurred_at,
        )
        await user_repo.log_activity(log)
        await session.commit()


async def handle_affiliate_commission(event: AffiliateCommissionCredited):
    # Create notification
    async with sessionmanager.session_factory() as session:
        notif_repo = SQLAlchemyNotificationRepository(session)
        from app.domain.entities.notification import Notification
        notif = Notification(
            user_id=event.user_id,
            type="success",
            title="Affiliate Commission Credited",
            content=f"You've earned ${event.amount.amount:.2f} in affiliate commission.",
        )
        await notif_repo.save(notif)
        await session.commit()
    logger.info("Affiliate commission notification created", user_id=event.user_id)


async def handle_withdrawal_requested(event: WithdrawalRequested):
    # Notify admin (could be email)
    logger.info("Withdrawal requested", withdrawal_id=event.withdrawal_id, user_id=event.user_id)


async def handle_withdrawal_approved(event: WithdrawalApproved):
    # Notify user
    async with sessionmanager.session_factory() as session:
        notif_repo = SQLAlchemyNotificationRepository(session)
        from app.domain.entities.notification import Notification
        notif = Notification(
            user_id=event.user_id,
            type="info",
            title="Withdrawal Approved",
            content=f"Your withdrawal of ${event.amount.amount:.2f} has been approved and is being processed.",
        )
        await notif_repo.save(notif)
        await session.commit()
    logger.info("Withdrawal approved notification sent", user_id=event.user_id)


async def handle_withdrawal_paid(event: WithdrawalPaid):
    # Notify user
    async with sessionmanager.session_factory() as session:
        notif_repo = SQLAlchemyNotificationRepository(session)
        from app.domain.entities.notification import Notification
        notif = Notification(
            user_id=event.user_id,
            type="success",
            title="Withdrawal Completed",
            content=f"Your withdrawal of ${event.amount.amount:.2f} has been sent.",
        )
        await notif_repo.save(notif)
        await session.commit()
    logger.info("Withdrawal paid notification sent", user_id=event.user_id)


async def handle_transaction_categorized(event: TransactionCategorized):
    # Could update analytics or send notification if low confidence
    if event.confidence < 0.6:
        async with sessionmanager.session_factory() as session:
            notif_repo = SQLAlchemyNotificationRepository(session)
            from app.domain.entities.notification import Notification
            notif = Notification(
                user_id=event.user_id,
                type="warning",
                title="Transaction Needs Review",
                content=f"Transaction {event.transaction_id} was categorized with low confidence. Please review.",
            )
            await notif_repo.save(notif)
            await session.commit()
    logger.debug("Transaction categorized", transaction_id=event.transaction_id, category=event.category)


async def handle_receipt_processed(event: ReceiptProcessed):
    # Notify user
    if event.status == "processed":
        async with sessionmanager.session_factory() as session:
            notif_repo = SQLAlchemyNotificationRepository(session)
            from app.domain.entities.notification import Notification
            notif = Notification(
                user_id=event.user_id,
                type="success",
                title="Receipt Processed",
                content="Your receipt has been processed successfully.",
            )
            await notif_repo.save(notif)
            await session.commit()
    elif event.status == "failed":
        async with sessionmanager.session_factory() as session:
            notif_repo = SQLAlchemyNotificationRepository(session)
            from app.domain.entities.notification import Notification
            notif = Notification(
                user_id=event.user_id,
                type="error",
                title="Receipt Processing Failed",
                content="There was an error processing your receipt. Please try again.",
            )
            await notif_repo.save(notif)
            await session.commit()
    logger.info("Receipt processed notification", user_id=event.user_id, status=event.status)


async def handle_user_subscribed(event: UserSubscribed):
    # Track in analytics
    if settings.MIXPANEL_TOKEN:
        mixpanel = MixpanelClient()
        mixpanel.track(event.user_id, "Subscription Changed", {"tier": event.tier, "old_tier": event.old_tier})
    logger.info("User subscription changed", user_id=event.user_id, tier=event.tier)
