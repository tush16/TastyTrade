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
async def ws_chain(
    websocket: WebSocket, symbol: str = Query(...), expiry: str = Query(...)
):
    await stream_mgr.connect(websocket, symbol, expiry)
    try:
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                await websocket.send_json(
                    {"type": "ping", "timestamp": datetime.utcnow().isoformat()}
                )
    except WebSocketDisconnect:
        stream_mgr.disconnect(websocket)
