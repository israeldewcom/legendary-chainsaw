from fastapi import APIRouter, Depends, Query
from typing import List, Annotated
from app.application.dtos import WithdrawalResponseDTO, WithdrawalApproveDTO, WithdrawalRejectDTO
from app.application.use_cases.admin.withdrawals.list_withdrawals import AdminListWithdrawalsUseCase
from app.application.use_cases.admin.withdrawals.approve_withdrawal import ApproveWithdrawalUseCase
from app.application.use_cases.admin.withdrawals.reject_withdrawal import RejectWithdrawalUseCase
from app.interfaces.api.dependencies import get_current_superuser, get_admin_list_withdrawals_use_case, etc.
from app.domain.entities.user import User

router = APIRouter(prefix="/withdrawals", tags=["admin-withdrawals"])


@router.get("/", response_model=List[WithdrawalResponseDTO])
async def list_withdrawals(
    current_user: Annotated[User, Depends(get_current_superuser)],
    status: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    use_case: Annotated[AdminListWithdrawalsUseCase, Depends(get_admin_list_withdrawals_use_case)],
):
    return await use_case.execute(status=status, skip=skip, limit=limit)


@router.post("/{withdrawal_id}/approve")
async def approve_withdrawal(
    withdrawal_id: int,
    dto: WithdrawalApproveDTO,
    current_user: Annotated[User, Depends(get_current_superuser)],
    use_case: Annotated[ApproveWithdrawalUseCase, Depends(get_admin_approve_withdrawal_use_case)],
):
    await use_case.execute(withdrawal_id, current_user.id, dto.admin_notes)
    return {"message": "Withdrawal approved"}


@router.post("/{withdrawal_id}/reject")
async def reject_withdrawal(
    withdrawal_id: int,
    dto: WithdrawalRejectDTO,
    current_user: Annotated[User, Depends(get_current_superuser)],
    use_case: Annotated[RejectWithdrawalUseCase, Depends(get_admin_reject_withdrawal_use_case)],
):
    await use_case.execute(withdrawal_id, dto.reason)
    return {"message": "Withdrawal rejected"}
