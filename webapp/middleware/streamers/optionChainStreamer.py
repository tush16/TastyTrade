import asyncio
from datetime import datetime
import time
from typing import Set, Dict, Tuple
from fastapi import WebSocket, WebSocketDisconnect
from tastytrade import Session, DXLinkStreamer
from tastytrade.instruments import get_option_chain
from tastytrade.dxfeed import Greeks, Quote
from utils.common import safe_float, parse_option_symbol
from config.logging import logger


class StreamManager:
    def __init__(self, session: Session):
        self.session = session
        self.clients: Dict[Tuple[str, str], Set[WebSocket]] = {}
        self.tasks: Dict[Tuple[str, str], asyncio.Task] = {}
        self.last_reset = datetime.now()
        self.last_send = 0.0
        self.message_count = 0

        # State for grouping
        self.last_quotes: Dict[str, dict] = {}
        self.last_greeks: Dict[str, dict] = {}

    async def try_send_grouped(self, symbol: str, expiry: str, event_symbol: str):
        """Attempt to send grouped data when both quote and greeks are available"""
        if event_symbol in self.last_quotes and event_symbol in self.last_greeks:
            quote = self.last_quotes[event_symbol]
            greek = self.last_greeks[event_symbol]

            # Verify timestamps are reasonably close (e.g., within 2 seconds)
            quote_time = datetime.fromisoformat(quote["quote_data"]["timestamp"])
            greek_time = datetime.fromisoformat(greek["greeks_data"]["timestamp"])

            if abs((quote_time - greek_time).total_seconds()) < 2:
                await self.broadcast(
                    symbol,
                    expiry,
                    {
                        "tt_type": "grouped_option_data",
                        "symbol": event_symbol,
                        "timestamp": datetime.utcnow().isoformat(),
                        "quote": quote["quote_data"],
                        "greeks": greek["greeks_data"],
                        **quote["parsed"],
                    },
                )
                # Clear the cached values
                self.last_quotes.pop(event_symbol, None)
                self.last_greeks.pop(event_symbol, None)

    async def start_stream(self, symbol: str, expiry: str):
        """Main streaming method for a specific symbol/expiry combination"""
        key = (symbol, expiry)
        logger.info(f"Initializing stream for {key}...")

        # Get option chain data
        chain = get_option_chain(self.session, symbol)
        if not chain:
            logger.error(f"No option chain found for {symbol}")
            return

        try:
            expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
        except ValueError:
            logger.error(f"Invalid expiry format: {expiry}")
            return

        if expiry_date not in chain:
            logger.error(f"No options found for {symbol} with expiry {expiry_date}.")
            return

        options = chain[expiry_date]
        if not options:
            logger.error("No options available for this expiry.")
            return

        # Prepare symbols for subscription
        streamer_symbols = [o.streamer_symbol for o in options]
        underlying_symbol = options[0].underlying_symbol

        async with DXLinkStreamer(self.session) as streamer:
            # Subscribe to both data types
            logger.info(f"Subscribing to {len(streamer_symbols)} options...")
            await streamer.subscribe(Quote, streamer_symbols + [underlying_symbol])
            await streamer.subscribe(Greeks, streamer_symbols)
            logger.info("Subscriptions complete")

            async def listen_quotes():
                """Handle all incoming quote messages"""
                async for event in streamer.listen(Quote):
                    try:
                        if event.event_symbol == underlying_symbol:
                            # Handle underlying quote separately
                            await self.broadcast(
                                symbol,
                                expiry,
                                {
                                    "tt_type": "underlying_quote",
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "symbol": event.event_symbol,
                                    "bid_exchange_code": event.bid_exchange_code,
                                    "bid_price": safe_float(event.bid_price),
                                    "bid_size": safe_float(event.bid_size),
                                    "ask_exchange_code": event.ask_exchange_code,
                                    "ask_price": safe_float(event.ask_price),
                                    "ask_size": safe_float(event.ask_size),
                                },
                            )
                        else:
                            parsed = parse_option_symbol(event.event_symbol)
                            if parsed:
                                # Store the quote
                                self.last_quotes[event.event_symbol] = {
                                    "quote_data": {
                                        "bid_price": safe_float(event.bid_price),
                                        "ask_price": safe_float(event.ask_price),
                                        "bid_size": safe_float(event.bid_size),
                                        "ask_size": safe_float(event.ask_size),
                                        "timestamp": datetime.utcnow().isoformat(),
                                    },
                                    "parsed": parsed,
                                }
                                await self.try_send_grouped(
                                    symbol, expiry, event.event_symbol
                                )
                    except Exception as e:
                        logger.error(f"Quote processing error: {e}")

            async def listen_greeks():
                """Handle all incoming Greeks messages"""
                async for event in streamer.listen(Greeks):
                    try:
                        parsed = parse_option_symbol(event.event_symbol)
                        if parsed:
                            # Store the greeks
                            self.last_greeks[event.event_symbol] = {
                                "greeks_data": {
                                    "price": safe_float(event.price),
                                    "IV": safe_float(event.volatility),
                                    "delta": safe_float(event.delta),
                                    "gamma": safe_float(event.gamma),
                                    "theta": safe_float(event.theta),
                                    "rho": safe_float(event.rho),
                                    "vega": safe_float(event.vega),
                                    "timestamp": datetime.utcnow().isoformat(),
                                },
                                "parsed": parsed,
                            }
                            await self.try_send_grouped(
                                symbol, expiry, event.event_symbol
                            )
                    except Exception as e:
                        logger.error(f"Greeks processing error: {e}")

            # Start listeners
            processors = [
                asyncio.create_task(listen_quotes()),
                asyncio.create_task(listen_greeks()),
                asyncio.create_task(self.monitor_rates()),
            ]

            try:
                await asyncio.gather(*processors)
            except Exception as e:
                logger.error(f"Stream error: {e}")
                for task in processors:
                    task.cancel()
                raise

    async def monitor_rates(self):
        """Log message rates every minute"""
        while True:
            await asyncio.sleep(60)
            logger.info(f"Message rate: {self.message_count}/min")
            self.message_count = 0
            self.last_reset = datetime.now()

    async def connect(self, websocket: WebSocket, symbol: str, expiry: str):
        """Handle new WebSocket connection"""
        key = (symbol, expiry)
        await websocket.accept()
        if key not in self.clients:
            self.clients[key] = set()
        self.clients[key].add(websocket)
        logger.info(f"Client connected: {websocket.client} for {symbol} - {expiry}")

        if key not in self.tasks:
            self.tasks[key] = asyncio.create_task(self.start_stream(symbol, expiry))

    def disconnect(self, websocket: WebSocket):
        """Handle client disconnection"""
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
        """Send data to all connected clients with rate limiting"""
        now = time.time()
        if now - self.last_send < 0.1:  # 100ms minimum between sends
            await asyncio.sleep(0.1 - (now - self.last_send))
        self.last_send = time.time()
        self.message_count += 1

        key = (symbol, expiry)
        to_remove = []
        for client in self.clients.get(key, []):
            try:
                await client.send_json(data)
            except WebSocketDisconnect:
                to_remove.append(client)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                to_remove.append(client)

        for client in to_remove:
            self.disconnect(client)
