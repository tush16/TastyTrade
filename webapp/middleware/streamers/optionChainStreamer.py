import asyncio
from datetime import datetime
from typing import Set, Dict, Tuple
from fastapi import WebSocket, WebSocketDisconnect

from tastytrade import Session, DXLinkStreamer
from tastytrade.instruments import get_option_chain
from tastytrade.dxfeed import Greeks, Quote
from utils.common import safe_float
from config.logging import logger


class StreamManager:
    def __init__(self, session: Session):
        self.session = session
        self.clients: Dict[Tuple[str, str], Set[WebSocket]] = {}
        self.tasks: Dict[Tuple[str, str], asyncio.Task] = {}

    async def start_stream(self, symbol: str, expiry: str):
        key = (symbol, expiry)
        logger.info(f"Fetching option chain for {key}...")

        chain = get_option_chain(self.session, symbol)
        if not chain:
            logger.info(f"No option chain found for {symbol}")
            return

        try:
            expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
        except ValueError:
            logger.info(f"Invalid expiry format: {expiry}")
            return

        if expiry_date not in chain:
            logger.info(f"No options found for {symbol} with expiry {expiry_date}.")
            return

        options = chain[expiry_date]
        if not options:
            logger.info("No options available for this expiry.")
            return

        streamer_symbols = [o.streamer_symbol for o in options]
        underlying_symbols = list(set(o.underlying_symbol for o in options))

        async with DXLinkStreamer(self.session) as streamer:
            logger.info("Subscribing to DXLink...")
            await streamer.subscribe(Quote, underlying_symbols)
            await streamer.subscribe(Greeks, streamer_symbols)

            async def listen_quotes():
                async for event in streamer.listen(Quote):
                    await self.broadcast(
                        symbol,
                        expiry,
                        {
                            "type": "quote",
                            "timestamp": datetime.utcnow().isoformat(),
                            "symbol": event.event_symbol,
                            "bid": safe_float(event.bid_price),
                            "ask": safe_float(event.ask_price),
                        },
                    )

            async def listen_greeks():
                async for event in streamer.listen(Greeks):
                    await self.broadcast(
                        symbol,
                        expiry,
                        {
                            "type": "greeks",
                            "timestamp": datetime.utcnow().isoformat(),
                            "symbol": event.event_symbol,
                            "delta": safe_float(event.delta),
                            "gamma": safe_float(event.gamma),
                            "theta": safe_float(event.theta),
                            "vega": safe_float(event.vega),
                            "price": safe_float(event.price),
                        },
                    )

            await asyncio.gather(listen_quotes(), listen_greeks())

    async def connect(self, websocket: WebSocket, symbol: str, expiry: str):
        key = (symbol, expiry)
        await websocket.accept()
        if key not in self.clients:
            self.clients[key] = set()
        self.clients[key].add(websocket)
        logger.info(f"Client connected: {websocket.client} for {symbol} - {expiry}")

        if key not in self.tasks:
            self.tasks[key] = asyncio.create_task(self.start_stream(symbol, expiry))

    def disconnect(self, websocket: WebSocket):
        for key, clients in self.clients.items():
            if websocket in clients:
                clients.remove(websocket)
                logger.info(f"Client disconnected: {websocket.client}")
                if not clients:
                    task = self.tasks.pop(key, None)
                    if task:
                        task.cancel()
                    self.clients.pop(key)
                break

    async def broadcast(self, symbol: str, expiry: str, data: dict):
        key = (symbol, expiry)
        to_remove = []
        for client in self.clients.get(key, []):
            try:
                await client.send_json(data)
            except WebSocketDisconnect:
                to_remove.append(client)
            except Exception as e:
                logger.info(f"Broadcast error: {e}")
                to_remove.append(client)

        for client in to_remove:
            self.disconnect(client)
