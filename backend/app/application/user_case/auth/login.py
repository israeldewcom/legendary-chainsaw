from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from app.domain.repositories.user import UserRepository
from app.application.interfaces.password_hasher import PasswordHasher
from app.application.interfaces.token_service import TokenService
from app.application.interfaces.event_bus import EventBus
from app.common.exceptions import UnauthorizedError, ForbiddenError
from app.config import settings
import structlog

logger = structlog.get_logger()


@dataclass
class LoginUseCase:
    user_repo: UserRepository
    password_hasher: PasswordHasher
    token_service: TokenService
    event_bus: EventBus

    async def execute(self, email: str, password: str, mfa_code: Optional[str] = None, ip: Optional[str] = None, user_agent: Optional[str] = None) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user:
            # Simulate timing to avoid user enumeration
            self.password_hasher.dummy_verify()
            raise UnauthorizedError("Invalid credentials")

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise ForbiddenError("Account locked due to too many failed attempts")

        # Verify password
        if not self.password_hasher.verify(password, user.hashed_password):
            user.record_failed_login()
            await self.user_repo.save(user)
            for event in user.collect_events():
                await self.event_bus.publish(event)
            raise UnauthorizedError("Invalid credentials")

        # Check MFA if enabled
        if user.mfa_enabled:
            if not mfa_code:
                raise UnauthorizedError("MFA code required")
            # Verify TOTP
            import pyotp
            totp = pyotp.TOTP(user.mfa_secret)
            if not totp.verify(mfa_code):
                raise UnauthorizedError("Invalid MFA code")
            # If code is recovery code
            if mfa_code in user.mfa_recovery_codes:
                # Invalidate that recovery code
                user.mfa_recovery_codes.remove(mfa_code)
                await self.user_repo.save(user)

        # Reset failed attempts
        user.reset_failed_logins()
        user.record_login(ip, user_agent)
        await self.user_repo.save(user)

        # Generate tokens
        access_token = self.token_service.create_access_token(user.id)
        refresh_token = self.token_service.create_refresh_token(user.id)

        # Publish events
        for event in user.collect_events():
            await self.event_bus.publish(event)

        logger.info("User logged in", user_id=user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
