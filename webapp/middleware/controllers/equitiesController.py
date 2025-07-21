from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.equitiesService import EquitiesService

router = APIRouter(tags=["Equities API"])
security = HTTPBearer()


@router.get("/equities/top")
async def list_equities(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return await EquitiesService(token).list_equities()


@router.get("/equities/active")
async def get_active_equities(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    page_offset: int = Query(0, ge=0, description="Page offset, default is 0"),
    per_page: int = Query(
        500, ge=1, le=1000, description="Results per page, default is 500"
    ),
    lendability: str = Query(
        "Easy To Borrow",
        description="Lendability filter: Easy To Borrow, Locate Required, or Preborrow",
    ),
):
    token = credentials.credentials
    service = EquitiesService(token)
    try:
        return await service.get_active_equities(page_offset, per_page, lendability)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/equities/search")
async def search_equities(
    query: str, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    return await EquitiesService(token).search_equities(query)
