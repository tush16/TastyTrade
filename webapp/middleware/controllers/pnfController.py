from fastapi import APIRouter, HTTPException, Query
from services.pnfService import PNFService

router = APIRouter(prefix="/pnf", tags=["Point & Figure"])

@router.get("/{symbol}")
async def get_pnf_chart(
    symbol: str,
    start: str = Query("2023-01-01"),
    end: str = Query("2025-01-01"),
    boxsize: int = Query(2, ge=1),
    reversal: int = Query(3, ge=1)
):
    try:
        ts = PNFService.fetch_timeseries(symbol, start, end)
        chart_base64 = PNFService.generate_pnf_chart(ts, symbol, boxsize, reversal)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
