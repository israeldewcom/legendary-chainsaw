from fastapi import APIRouter, Depends, Query
from typing import List, Annotated
from app.application.dtos import SearchQueryDTO, SearchResultDTO
from app.application.use_cases.search.search import SearchUseCase
from app.interfaces.api.dependencies import get_search_use_case, get_current_user
from app.domain.entities.user import User

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/", response_model=List[SearchResultDTO])
async def search(
    q: str = Query(..., min_length=1),
    type: str = Query(None),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[SearchUseCase, Depends(get_search_use_case)],
):
    query = SearchQueryDTO(q=q, type=type, limit=limit, offset=offset)
    return await use_case.execute(current_user.id, query)
