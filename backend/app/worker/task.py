from app.worker.celery_app import celery_app
from app.infrastructure.database.session import sessionmanager
from app.infrastructure.database.repositories.withdrawal import SQLAlchemyWithdrawalRepository
from app.infrastructure.database.repositories.payout_batch import SQLAlchemyPayoutBatchRepository
from app.infrastructure.database.repositories.user import SQLAlchemyUserRepository
from app.infrastructure.database.repositories.transaction import SQLAlchemyTransactionRepository
from app.infrastructure.database.repositories.user_session import SQLAlchemyUserSessionRepository
from app.application.use_cases.affiliate.process_pending_withdrawals import ProcessPendingWithdrawalsUseCase
from app.application.use_cases.affiliate.create_payout import CreateAffiliatePayoutUseCase
from app.application.use_cases.notifications.send_daily_digest import SendDailyDigestUseCase
from app.infrastructure.email.smtp_sender import SMTPEmailSender
from app.infrastructure.payment.stripe import StripeService
from app.config import settings
import structlog
import asyncio

logger = structlog.get_logger()


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@celery_app.task
def process_pending_withdrawals():
    logger.info("Starting process_pending_withdrawals task")
    run_async(_process_pending_withdrawals())


async def _process_pending_withdrawals():
    sessionmanager.init(str(settings.DATABASE_URL))
    async with sessionmanager.session_factory() as session:
        withdrawal_repo = SQLAlchemyWithdrawalRepository(session)
        payout_batch_repo = SQLAlchemyPayoutBatchRepository(session)
        user_repo = SQLAlchemyUserRepository(session)
        stripe_service = StripeService()
        create_payout_use_case = CreateAffiliatePayoutUseCase(
            withdrawal_repo=withdrawal_repo,
            user_repo=user_repo,
            payout_batch_repo=payout_batch_repo,
            stripe_connect=stripe_service,
            event_bus=None,  # would need event bus
        )
        use_case = ProcessPendingWithdrawalsUseCase(
            withdrawal_repo=withdrawal_repo,
            payout_batch_repo=payout_batch_repo,
            create_payout_use_case=create_payout_use_case,
        )
        await use_case.execute()
        await session.commit()
    await sessionmanager.close()
    logger.info("Completed process_pending_withdrawals task")


@celery_app.task
def send_daily_digest():
    logger.info("Starting send_daily_digest task")
    run_async(_send_daily_digest())


async def _send_daily_digest():
    sessionmanager.init(str(settings.DATABASE_URL))
    async with sessionmanager.session_factory() as session:
        user_repo = SQLAlchemyUserRepository(session)
        tx_repo = SQLAlchemyTransactionRepository(session)
        email_sender = SMTPEmailSender()
        use_case = SendDailyDigestUseCase(
            user_repo=user_repo,
            transaction_repo=tx_repo,
            email_sender=email_sender,
        )
        await use_case.execute()
        await session.commit()
    await sessionmanager.close()
    logger.info("Completed send_daily_digest task")


@celery_app.task
def reset_monthly_usage():
    logger.info("Starting reset_monthly_usage task")
    # Implementation would reset monthly_transactions_used for all users
    run_async(_reset_monthly_usage())


async def _reset_monthly_usage():
    sessionmanager.init(str(settings.DATABASE_URL))
    async with sessionmanager.session_factory() as session:
        from sqlalchemy import update
        from app.infrastructure.database.models import UserModel
        await session.execute(
            update(UserModel).values(monthly_transactions_used=0)
        )
        await session.commit()
    await sessionmanager.close()
    logger.info("Completed reset_monthly_usage task")


@celery_app.task
def cleanup_expired_sessions():
    logger.info("Starting cleanup_expired_sessions task")
    run_async(_cleanup_expired_sessions())


async def _cleanup_expired_sessions():
    sessionmanager.init(str(settings.DATABASE_URL))
    async with sessionmanager.session_factory() as session:
        repo = SQLAlchemyUserSessionRepository(session)
        await repo.delete_expired()
        await session.commit()
    await sessionmanager.close()
    logger.info("Completed cleanup_expired_sessions task")
