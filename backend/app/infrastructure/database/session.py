from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.pool import NullPool
from typing import Optional
from app.config import settings
import structlog

logger = structlog.get_logger()


class DatabaseSessionManager:
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._sessionmaker: Optional[async_sessionmaker[AsyncSession]] = None

    def init(self, host: str):
        self._engine = create_async_engine(
            host,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_timeout=settings.DATABASE_POOL_TIMEOUT,
            pool_recycle=settings.DATABASE_POOL_RECYCLE,
            echo=settings.DATABASE_ECHO,
            pool_pre_ping=True,
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        logger.info("Database session manager initialized")

    async def close(self):
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None
            logger.info("Database connections closed")

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager not initialized")
        return self._sessionmaker

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise Exception("DatabaseSessionManager not initialized")
        return self._engine


sessionmanager = DatabaseSessionManager()
