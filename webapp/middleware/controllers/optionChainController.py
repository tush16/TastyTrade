import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from streamers.optionChainStreamer import StreamManager
from datetime import datetime
from tastytrade.session import Session
from config.settings import settings

router = APIRouter()

LOGIN = settings.LOGIN
PASSWORD = settings.PASSWORD

session = Session(LOGIN, PASSWORD, is_test=True)
stream_mgr = StreamManager(session)

@router.websocket("/ws/chain")
async def websocket_stream(
    websocket: WebSocket,
    symbol: str,
    expiry: str,
    option_symbols: str = Query(..., description="Comma separated list of option symbols"),
):
    option_symbols_list = option_symbols.split(",")

    if not option_symbols_list or option_symbols_list == [""]:
        await websocket.close(code=1003)  
        return

    await stream_mgr.connect(websocket, symbol, expiry, option_symbols_list)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        stream_mgr.disconnect(websocket)

