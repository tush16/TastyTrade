from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.futuresService import FuturesService

router = APIRouter(tags=["Futures API"])
security = HTTPBearer()


@router.get("/futures")
async def list_futures(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return await FuturesService(token).list_futures()


@router.get("/futures/{symbol}")
async def get_future(
    symbol: str, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    return await FuturesService(token).get_future(symbol)
