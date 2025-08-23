from fastapi import APIRouter, HTTPException, Depends, Request
from tastytrade.instruments import get_option_chain
from tastytrade.session import Session
from datetime import date, datetime
from collections import defaultdict
from config.logging import logger

router = APIRouter(tags=["Options API"])


def get_session(request: Request) -> Session:
    session = request.app.state.session
    if not session:
        raise HTTPException(status_code=500, detail="Session not initialized")
    return session


@router.get("/option-chains")
async def get_expiries_with_symbols(
    symbol: str, session: Session = Depends(get_session)
):
    try:
        symbol_enc = symbol.replace("/", "%2F")
        data = await session._a_get(f"/option-chains/{symbol_enc}")

        expiry_map = defaultdict(list)
        for item in data.get("items", []):
            raw_exp = item.get("expiration-date")
            option_symbol = item.get("streamer-symbol")

            if not raw_exp or not option_symbol:
                continue

            try:
                if len(raw_exp) == 10:
                    exp_date = date.fromisoformat(raw_exp).isoformat()
                else:
                    exp_date = datetime.fromisoformat(raw_exp).date().isoformat()
            except ValueError:
                continue

            expiry_map[exp_date].append(option_symbol)

        if not expiry_map:
            raise HTTPException(status_code=404, detail="No expiries found")

        return expiry_map

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
