from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.stockService import StockService

router = APIRouter(tags=["Equities API"])
security = HTTPBearer()


@router.get("/equities/list")
async def list_equities(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return await StockService(token).list_equities()


@router.get("/equities/search")
async def search_equities(
    query: str, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    return await StockService(token).search_equities(query)
