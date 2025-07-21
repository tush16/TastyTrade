from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.optionChainsService import OptionChainsService

router = APIRouter(tags=["Option-Chain API"])
security = HTTPBearer()


@router.get("/option-chains/{symbol}/nested")
async def get_option_chain(
    symbol: str, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    return await OptionChainsService(token).get_option_chain(symbol)
