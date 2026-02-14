from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.user import User
from app.domain.entities.user_activity_log import UserActivityLog


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_verification_token(self, token: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_reset_token(self, token: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_referral_code(self, code: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_stripe_customer_id(self, customer_id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_stripe_connect_account(self, account_id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        pass

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100, filters: Optional[dict] = None) -> List[User]:
        pass

    @abstractmethod
    async def count(self, filters: Optional[dict] = None) -> int:
        pass

    @abstractmethod
    async def log_activity(self, log: UserActivityLog) -> None:
        pass
