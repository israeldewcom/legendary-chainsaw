from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.background_job import BackgroundJob


class BackgroundJobRepository(ABC):
    @abstractmethod
    async def create(self, job: BackgroundJob) -> BackgroundJob:
        pass

    @abstractmethod
    async def get_pending(self, job_type: str, limit: int = 10) -> List[BackgroundJob]:
        pass

    @abstractmethod
    async def update(self, job: BackgroundJob) -> None:
        pass
