from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Annotated
from jose import JWTError, jwt
from app.infrastructure.database.session import sessionmanager
from app.infrastructure.database.repositories.user import SQLAlchemyUserRepository
from app.infrastructure.database.repositories.transaction import SQLAlchemyTransactionRepository
from app.infrastructure.cache.redis import redis_client
from app.application.interfaces.token_service import TokenService
from app.config import settings
from app.domain.entities.user import User
from app.common.exceptions import UnauthorizedError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_db() -> AsyncSession:
    async with sessionmanager.session_factory() as session:
        yield session


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY.get_secret_value(), algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = SQLAlchemyUserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def get_current_superuser(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


def get_token_service() -> TokenService:
    from app.infrastructure.auth.jwt import JWTTokenService
    return JWTTokenService()


# Use case dependencies
async def get_register_use_case(db: AsyncSession = Depends(get_db)):
    from app.application.use_cases.auth.register import RegisterUseCase
    from app.infrastructure.auth.password import Argon2PasswordHasher
    from app.infrastructure.event_bus.redis_event_bus import RedisEventBus
    user_repo = SQLAlchemyUserRepository(db)
    hasher = Argon2PasswordHasher()
    event_bus = RedisEventBus()  # singleton? we'd need to manage
    return RegisterUseCase(user_repo=user_repo, password_hasher=hasher, event_bus=event_bus)

# ... more dependencies
