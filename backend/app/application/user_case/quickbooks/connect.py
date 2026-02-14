from dataclasses import dataclass
from datetime import datetime, timedelta
from app.domain.entities.quickbooks_token import QuickBooksToken
from app.domain.repositories.quickbooks_token import QuickBooksTokenRepository
from app.domain.repositories.user import UserRepository
from app.common.exceptions import NotFoundError
import structlog

logger = structlog.get_logger()


@dataclass
class ConnectQuickBooksUseCase:
    token_repo: QuickBooksTokenRepository
    user_repo: UserRepository

    async def execute(self, user_id: int, realm_id: str, access_token: str, refresh_token: str, expires_in: int) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Check if token already exists
        existing = await self.token_repo.get_by_user_id(user_id)
        if existing:
            # Update existing
            existing.update(access_token, refresh_token, expires_in)
            existing.realm_id = realm_id
            await self.token_repo.save(existing)
        else:
            # Create new
            token = QuickBooksToken(
                user_id=user_id,
                realm_id=realm_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
            )
            await self.token_repo.save(token)

        logger.info("QuickBooks connected", user_id=user_id, realm_id=realm_id)
