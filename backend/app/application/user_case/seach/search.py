from dataclasses import dataclass
from typing import List
from app.domain.repositories.transaction import TransactionRepository
from app.domain.repositories.client import ClientRepository
from app.domain.repositories.receipt import ReceiptRepository
from app.application.dtos import SearchQueryDTO, SearchResultDTO
import structlog

logger = structlog.get_logger()


@dataclass
class SearchUseCase:
    transaction_repo: TransactionRepository
    client_repo: ClientRepository
    receipt_repo: ReceiptRepository

    async def execute(self, user_id: int, query: SearchQueryDTO) -> List[SearchResultDTO]:
        results = []

        if query.type in (None, "transactions"):
            # Search transactions using full-text search (postgres)
            transactions = await self.transaction_repo.search(user_id, query.q, limit=query.limit, offset=query.offset)
            for tx in transactions:
                results.append(SearchResultDTO(
                    id=tx.id,
                    type="transaction",
                    title=tx.description[:100],
                    description=f"{tx.date.strftime('%Y-%m-%d')} - {tx.amount}",
                    url=f"/transactions/{tx.id}",
                    score=1.0,  # would come from search rank
                ))

        if query.type in (None, "clients"):
            clients = await self.client_repo.search(user_id, query.q, limit=query.limit, offset=query.offset)
            for client in clients:
                results.append(SearchResultDTO(
                    id=client.id,
                    type="client",
                    title=client.name,
                    description=client.email or "",
                    url=f"/clients/{client.id}",
                    score=1.0,
                ))

        if query.type in (None, "receipts"):
            receipts = await self.receipt_repo.search(user_id, query.q, limit=query.limit, offset=query.offset)
            for rec in receipts:
                results.append(SearchResultDTO(
                    id=rec.id,
                    type="receipt",
                    title=rec.filename or f"Receipt {rec.id}",
                    description=rec.ocr_text[:100] if rec.ocr_text else "",
                    url=f"/receipts/{rec.id}",
                    score=1.0,
                ))

        return results
