from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional, Annotated
from app.application.dtos import TransactionResponseDTO, TransactionCreateDTO, TransactionUpdateDTO
from app.application.use_cases.transactions.list_transactions import ListTransactionsUseCase
from app.application.use_cases.transactions.get_transaction import GetTransactionUseCase
from app.application.use_cases.transactions.create_transaction import CreateTransactionUseCase
from app.application.use_cases.transactions.update_transaction import UpdateTransactionUseCase
from app.application.use_cases.transactions.delete_transaction import DeleteTransactionUseCase
from app.application.use_cases.transactions.categorize import CategorizeTransactionUseCase
from app.application.use_cases.transactions.bulk_categorize import BulkCategorizeUseCase
from app.application.use_cases.transactions.bulk_delete import BulkDeleteUseCase
from app.interfaces.api.dependencies import (
    get_list_transactions_use_case, get_get_transaction_use_case,
    get_create_transaction_use_case, get_update_transaction_use_case,
    get_delete_transaction_use_case, get_categorize_transaction_use_case,
    get_bulk_categorize_use_case, get_bulk_delete_use_case,
    get_current_user
)
from app.domain.entities.user import User

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/", response_model=List[TransactionResponseDTO])
async def list_transactions(
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    client_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    use_case: Annotated[ListTransactionsUseCase, Depends(get_list_transactions_use_case)],
):
    filters = {
        "client_id": client_id,
        "category": category,
        "status": status,
        "date_from": date_from,
        "date_to": date_to,
    }
    return await use_case.execute(current_user.id, skip, limit, filters)


@router.get("/{transaction_id}", response_model=TransactionResponseDTO)
async def get_transaction(
    transaction_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[GetTransactionUseCase, Depends(get_get_transaction_use_case)],
):
    return await use_case.execute(transaction_id, current_user.id)


@router.post("/", response_model=TransactionResponseDTO)
async def create_transaction(
    dto: TransactionCreateDTO,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[CreateTransactionUseCase, Depends(get_create_transaction_use_case)],
):
    return await use_case.execute(current_user.id, dto)


@router.patch("/{transaction_id}", response_model=TransactionResponseDTO)
async def update_transaction(
    transaction_id: int,
    dto: TransactionUpdateDTO,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[UpdateTransactionUseCase, Depends(get_update_transaction_use_case)],
):
    return await use_case.execute(transaction_id, current_user.id, dto)


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[DeleteTransactionUseCase, Depends(get_delete_transaction_use_case)],
):
    await use_case.execute(transaction_id, current_user.id)
    return {"message": "Transaction deleted"}


@router.post("/{transaction_id}/categorize")
async def categorize_transaction(
    transaction_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[CategorizeTransactionUseCase, Depends(get_categorize_transaction_use_case)],
):
    await use_case.execute(transaction_id, current_user.id)
    return {"message": "Categorization queued"}


@router.post("/bulk/categorize")
async def bulk_categorize(
    transaction_ids: List[int],
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[BulkCategorizeUseCase, Depends(get_bulk_categorize_use_case)],
):
    await use_case.execute(transaction_ids, current_user.id)
    return {"message": f"Bulk categorization started for {len(transaction_ids)} transactions"}


@router.delete("/bulk")
async def bulk_delete(
    transaction_ids: List[int],
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[BulkDeleteUseCase, Depends(get_bulk_delete_use_case)],
):
    await use_case.execute(transaction_ids, current_user.id)
    return {"message": f"{len(transaction_ids)} transactions deleted"}
