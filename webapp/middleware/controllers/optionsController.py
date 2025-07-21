from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.optionsService import OptionsService

router = APIRouter(tags=["Equity Options API"])
security = HTTPBearer()


@router.get(
    "/equity-options",
    summary="Fetch option metadata using OCC symbols from user-provided stock tickers",
)
async def get_equity_options(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    stock_symbols: List[str] = Query(
        ...,
        alias="stock[]",
        description="Required list of stock tickers (e.g., AAPL, TSLA)",
    ),
    active: bool = Query(True, description="Only active (tradable) options"),
    with_expired: bool = Query(False, description="Include expired options"),
):
    token = credentials.credentials
    service = OptionsService(token)

    if not stock_symbols:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least one stock symbol in 'stock[]'.",
        )

    try:
        occ_symbols = []
        for ticker in stock_symbols:
            chain = await service.get_option_chain(ticker)
            chain_items = chain.get("items", [])

            # Limit to top 5 calls + 5 puts (adjust as needed)
            calls = [
                item["symbol"] for item in chain_items if item.get("option-type") == "C"
            ][:5]
            puts = [
                item["symbol"] for item in chain_items if item.get("option-type") == "P"
            ][:5]
            occ_symbols.extend(calls + puts)

        if not occ_symbols:
            raise HTTPException(
                status_code=404,
                detail="No OCC option symbols found for selected stocks.",
            )

        metadata = await service.get_equity_options(
            symbols=occ_symbols,
            active=active,
            with_expired=with_expired,
        )

        if isinstance(metadata, dict) and "error" in metadata:
            raise HTTPException(status_code=502, detail=metadata["error"])

        return metadata

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
