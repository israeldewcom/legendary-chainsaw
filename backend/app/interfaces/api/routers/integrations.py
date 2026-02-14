from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Annotated
from httpx_oauth.clients.quickbooks import QuickBooksOAuth2
from app.application.dtos import QuickBooksAuthUrlDTO, QuickBooksTokenResponseDTO
from app.application.use_cases.integrations.quickbooks.connect import ConnectQuickBooksUseCase
from app.application.use_cases.integrations.quickbooks.disconnect import DisconnectQuickBooksUseCase
from app.application.use_cases.integrations.quickbooks.status import GetQuickBooksStatusUseCase
from app.application.use_cases.integrations.quickbooks.sync import SyncQuickBooksUseCase
from app.interfaces.api.dependencies import get_current_user, get_quickbooks_connect_use_case, etc.
from app.domain.entities.user import User
from app.config import settings

router = APIRouter(prefix="/integrations", tags=["integrations"])

# QuickBooks OAuth client
qb_oauth = QuickBooksOAuth2(
    settings.QUICKBOOKS_CLIENT_ID,
    settings.QUICKBOOKS_CLIENT_SECRET.get_secret_value() if settings.QUICKBOOKS_CLIENT_SECRET else None,
    settings.QUICKBOOKS_REDIRECT_URI,
    environment=settings.QUICKBOOKS_ENVIRONMENT,
)


@router.get("/quickbooks/auth-url", response_model=QuickBooksAuthUrlDTO)
async def get_quickbooks_auth_url(
    current_user: Annotated[User, Depends(get_current_user)],
):
    state = f"user_id:{current_user.id}"
    url = await qb_oauth.get_authorization_url(
        redirect_uri=settings.QUICKBOOKS_REDIRECT_URI,
        state=state,
        scope=["com.intuit.quickbooks.accounting"],
    )
    return QuickBooksAuthUrlDTO(url=url)


@router.get("/quickbooks/callback")
async def quickbooks_callback(
    request: Request,
    code: str,
    state: str,
    realm_id: str,
    use_case: Annotated[ConnectQuickBooksUseCase, Depends(get_quickbooks_connect_use_case)],
):
    # Verify state
    if not state.startswith("user_id:"):
        raise HTTPException(status_code=400, detail="Invalid state")
    user_id = int(state.split(":")[1])

    # Exchange code for token
    token = await qb_oauth.get_access_token(code, settings.QUICKBOOKS_REDIRECT_URI)
    access_token = token["access_token"]
    refresh_token = token["refresh_token"]
    expires_in = token["expires_in"]

    await use_case.execute(
        user_id=user_id,
        realm_id=realm_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
    )
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/integrations/quickbooks/success")


@router.get("/quickbooks/status", response_model=QuickBooksTokenResponseDTO)
async def quickbooks_status(
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[GetQuickBooksStatusUseCase, Depends(get_quickbooks_status_use_case)],
):
    return await use_case.execute(current_user.id)


@router.post("/quickbooks/disconnect")
async def quickbooks_disconnect(
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[DisconnectQuickBooksUseCase, Depends(get_quickbooks_disconnect_use_case)],
):
    await use_case.execute(current_user.id)
    return {"message": "Disconnected"}


@router.post("/quickbooks/sync")
async def quickbooks_sync(
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[SyncQuickBooksUseCase, Depends(get_quickbooks_sync_use_case)],
):
    await use_case.execute(current_user.id)
    return {"message": "Sync started"}
