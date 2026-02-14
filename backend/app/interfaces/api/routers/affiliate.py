from fastapi import APIRouter, Depends, Query, Body
from typing import List, Annotated
from app.application.dtos import WithdrawalResponseDTO, WithdrawalRequestDTO, WithdrawalApproveDTO, WithdrawalRejectDTO
from app.application.use_cases.affiliate.get_balance import GetAffiliateBalanceUseCase
from app.application.use_cases.affiliate.request_withdrawal import RequestWithdrawalUseCase
from app.application.use_cases.affiliate.list_withdrawals import ListWithdrawalsUseCase
from app.application.use_cases.affiliate.get_referral_link import GetReferralLinkUseCase
from app.interfaces.api.dependencies import (
    get_affiliate_balance_use_case, get_request_withdrawal_use_case,
    get_list_withdrawals_use_case, get_referral_link_use_case,
    get_current_user
)
from app.domain.entities.user import User

router = APIRouter(prefix="/affiliate", tags=["affiliate"])


@router.get("/balance")
async def get_balance(
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[GetAffiliateBalanceUseCase, Depends(get_affiliate_balance_use_case)],
):
    return await use_case.execute(current_user.id)


@router.get("/referral-link")
async def get_referral_link(
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[GetReferralLinkUseCase, Depends(get_referral_link_use_case)],
):
    return await use_case.execute(current_user.id)


@router.post("/withdrawals", response_model=WithdrawalResponseDTO)
async def request_withdrawal(
    dto: WithdrawalRequestDTO,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[RequestWithdrawalUseCase, Depends(get_request_withdrawal_use_case)],
):
    return await use_case.execute(current_user.id, dto.amount, dto.method, dto.currency)


@router.get("/withdrawals", response_model=List[WithdrawalResponseDTO])
async def list_withdrawals(
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    use_case: Annotated[ListWithdrawalsUseCase, Depends(get_list_withdrawals_use_case)],
):
    return await use_case.execute(current_user.id, skip, limit)
