from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Annotated
from app.application.dtos import UserCreateDTO, UserResponseDTO
from app.application.use_cases.auth.register import RegisterUseCase
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.auth.refresh import RefreshTokenUseCase
from app.application.use_cases.auth.logout import LogoutUseCase
from app.application.use_cases.auth.mfa import SetupMFAUseCase, VerifyMFAUseCase
from app.application.use_cases.auth.password_reset import RequestPasswordResetUseCase, ResetPasswordUseCase
from app.interfaces.api.dependencies import (
    get_register_use_case, get_login_use_case, get_refresh_use_case,
    get_logout_use_case, get_setup_mfa_use_case, get_verify_mfa_use_case,
    get_request_password_reset_use_case, get_reset_password_use_case,
    get_current_user
)
from app.domain.entities.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=dict)
async def register(
    dto: UserCreateDTO,
    use_case: Annotated[RegisterUseCase, Depends(get_register_use_case)],
):
    user = await use_case.execute(dto)
    # In a real implementation, you'd return tokens or redirect to login
    return {"message": "User registered successfully", "user_id": user.id}


@router.post("/login")
async def login(
    request: Request,
    email: str = Body(...),
    password: str = Body(...),
    mfa_code: str = Body(None),
    use_case: Annotated[LoginUseCase, Depends(get_login_use_case)],
):
    result = await use_case.execute(
        email=email,
        password=password,
        mfa_code=mfa_code,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return result


@router.post("/refresh")
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    use_case: Annotated[RefreshTokenUseCase, Depends(get_refresh_use_case)],
):
    return await use_case.execute(refresh_token)


@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[LogoutUseCase, Depends(get_logout_use_case)],
):
    await use_case.execute(current_user.id)
    return {"message": "Logged out"}


@router.post("/mfa/setup")
async def setup_mfa(
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[SetupMFAUseCase, Depends(get_setup_mfa_use_case)],
):
    return await use_case.execute(current_user.id)


@router.post("/mfa/verify")
async def verify_mfa(
    current_user: Annotated[User, Depends(get_current_user)],
    code: str = Body(...),
    use_case: Annotated[VerifyMFAUseCase, Depends(get_verify_mfa_use_case)],
):
    await use_case.execute(current_user.id, code)
    return {"message": "MFA enabled"}


@router.post("/password-reset/request")
async def request_password_reset(
    email: str = Body(...),
    use_case: Annotated[RequestPasswordResetUseCase, Depends(get_request_password_reset_use_case)],
):
    await use_case.execute(email)
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/password-reset/reset")
async def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    use_case: Annotated[ResetPasswordUseCase, Depends(get_reset_password_use_case)],
):
    await use_case.execute(token, new_password)
    return {"message": "Password reset successfully"}
