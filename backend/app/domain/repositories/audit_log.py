from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.audit_log import AuditLog


class AuditLogRepository(ABC):
    @abstractmethod
    async def log(self, log: AuditLog) -> None:
        pass

    @abstractmethod
    async def get_by_entity(self, entity_type: str, entity_id: int, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        pass
