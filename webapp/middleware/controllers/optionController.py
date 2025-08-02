from fastapi import APIRouter, HTTPException, Depends, Request
from tastytrade.instruments import get_option_chain
from tastytrade.session import Session

router = APIRouter(tags=["Options API"])


def get_session(request: Request) -> Session:
    session = request.app.state.session
    if not session:
        raise HTTPException(status_code=500, detail="Session not initialized")
    return session


@router.get("/options/expiries")
def get_expiries(symbol: str, session: Session = Depends(get_session)):
    try:
        chain = get_option_chain(session, symbol)
        if not chain:
            raise HTTPException(status_code=404, detail="Option chain not found")
        expiries = sorted(chain.keys())
        return expiries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
