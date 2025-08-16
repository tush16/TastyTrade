import time
from datetime import datetime, timezone
import asyncio
from typing import Set, Dict, Tuple, List
from fastapi import WebSocket, WebSocketDisconnect
from tastytrade import Session, DXLinkStreamer
from tastytrade.dxfeed import Greeks, Quote
from config.logging import logger
from utils.common import safe_float, parse_option_symbol, expiry_yymmdd_to_utc_16et
from utils.optionChainMetrics import (calculate_pmp_pop_ce_sell, calculate_pmp_pop_pe_sell)

class StreamManager:
    def __init__(self, session: Session):
        self.session = session
        self.clients: Dict[Tuple[str, str], Set[WebSocket]] = {}
        self.tasks: Dict[Tuple[str, str], asyncio.Task] = {}
        self.last_reset = datetime.now(timezone.utc)
        self.last_send = 0.0
        self.message_count = 0

        # last_* caches keyed by event_symbol (for options) and by underlying symbol (for the underlying)
        self.last_quotes: Dict[str, dict] = {}
        self.last_greeks: Dict[str, dict] = {}


    async def try_send_grouped(self, symbol: str, expiry: str, event_symbol: str):
        """Process and broadcast option data with calculations when quote and Greeks are available."""
        if event_symbol not in self.last_quotes or event_symbol not in self.last_greeks:
            return

        quote = self.last_quotes[event_symbol]
        greek = self.last_greeks[event_symbol]
        try:
            quote_time = datetime.fromisoformat(quote["quote_data"]["timestamp"])
            greek_time = datetime.fromisoformat(greek["greeks_data"]["timestamp"])
        except Exception:
            # If timestamps malformed, proceed anyway
            quote_time = greek_time = datetime.now(timezone.utc)

        if abs((quote_time - greek_time).total_seconds()) < 2:
            parsed = quote["parsed"]
            if not parsed:
                logger.error(f"Skipping processing for {event_symbol}: parse failed")
                return

            # Option type and mid
            option_type = 'CALL' if parsed.get('call_put') == 'C' else 'PUT'
            bid = safe_float(quote["quote_data"].get("bid_price"))
            ask = safe_float(quote["quote_data"].get("ask_price"))
            mid_price = (bid + ask) / 2.0 if (bid > 0 and ask > 0) else (bid or ask)

            # Underlying price snapshot (we store it under underlying symbol)
            underlying_quote = self.last_quotes.get(symbol, {}).get("quote_data", {})
            current_price = (
                safe_float(underlying_quote.get("last_price"))
                or ((safe_float(underlying_quote.get("bid_price")) + safe_float(underlying_quote.get("ask_price"))) / 2.0)
                or safe_float(underlying_quote.get("bid_price"))
                or safe_float(underlying_quote.get("ask_price"))
            )
            if current_price <= 0 or mid_price is None or mid_price <= 0:
                logger.warning(f"Missing prices for {event_symbol}: underlying={current_price}, mid={mid_price}")
                return

            # Use strike IV as both strike IV and underlying IV proxy (decimal)
            iv_strike = safe_float(greek["greeks_data"].get("IV")) 
            iv_instrument = iv_strike

            # Expiry UTC from YYMMDD @ 16:00 ET
            try:
                expiry_utc = expiry_yymmdd_to_utc_16et(parsed["expiry"])
            except Exception as e:
                logger.error(f"Error parsing expiry for {event_symbol}: {e}")
                return

            try:
                if option_type == 'CALL':
                    pmp, pop, max_profit, max_loss, ev = calculate_pmp_pop_ce_sell(
                        current_price=current_price,
                        strike=parsed["strike"],
                        premium_ce=mid_price,
                        expiry_utc=expiry_utc,
                        iv_instrument=iv_instrument,
                        iv_ce=iv_strike,
                    )
                else:
                    pmp, pop, max_profit, max_loss, ev = calculate_pmp_pop_pe_sell(
                        current_price=current_price,
                        strike=parsed["strike"],
                        premium_pe=mid_price,
                        expiry_utc=expiry_utc,
                        iv_instrument=iv_instrument,
                        iv_pe=iv_strike,
                    )
            except Exception as e:
                logger.error(f"Calculation error for {event_symbol}: {e}")
                return

            option_data = {
                "symbol": event_symbol,
                "underlying_symbol": symbol,
                "expiry_date": expiry_utc.isoformat(),
                "strike_price": parsed["strike"],
                "option_type": option_type,
                "iv_strike": iv_strike * 100.0,  
                "mid_price": mid_price,
                "bid_price": bid,
                "ask_price": ask,
                "vega": safe_float(greek["greeks_data"].get("vega")),
                "theta": safe_float(greek["greeks_data"].get("theta")),
                "pmp": round(pmp, 4),
                "pop": round(pop, 4),
                "max_profit": max_profit,
                "max_loss": max_loss,
                "ev": None if ev is None else round(ev, 4),
                "underlying_price": current_price,
            }

            # Broadcast to clients
            await self.broadcast(
                symbol,
                expiry,
                {
                    "tt_type": "grouped_option_data",
                    "symbol": event_symbol,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "quote": quote["quote_data"],
                    "greeks": greek["greeks_data"],
                    "calculations": option_data,
                    **parsed,
                },
            )

            # clear paired data
            self.last_quotes.pop(event_symbol, None)
            self.last_greeks.pop(event_symbol, None)

    async def start_stream(self, symbol: str, expiry: str, option_symbols: List[str]):
        key = (symbol, expiry)
        logger.info(f"Initializing stream for {key}...")

        if not option_symbols:
            logger.error(f"No option symbols provided for {symbol} - {expiry}")
            return

        underlying_symbol = symbol
        logger.info(f"Subscribing to {len(option_symbols)} options for {symbol} - {expiry}")
        logger.info(f"Underlying symbol: {underlying_symbol}")

        async with DXLinkStreamer(self.session) as streamer:
            await streamer.subscribe(Quote, option_symbols + [underlying_symbol])
            await streamer.subscribe(Greeks, option_symbols)
            logger.info("Subscriptions complete")

            async def listen_quotes():
                async for event in streamer.listen(Quote):
                    try:
                        if event.event_symbol == underlying_symbol:
                            quote_data = {
                                "bid_price": safe_float(event.bid_price),
                                "ask_price": safe_float(event.ask_price),
                                "bid_size": safe_float(event.bid_size),
                                "ask_size": safe_float(event.ask_size),
                                "last_price": safe_float(getattr(event, "last_price", None)),
                                "timestamp": datetime.now(timezone.utc).isoformat(),
                            }
                            self.last_quotes[underlying_symbol] = {
                                "quote_data": quote_data,
                                "parsed": {"underlying": underlying_symbol}, 
                            }
                            await self.broadcast(
                                symbol,
                                expiry,
                                {
                                    "tt_type": "underlying_quote",
                                    "timestamp": quote_data["timestamp"],
                                    "symbol": event.event_symbol,
                                    "bid_exchange_code": event.bid_exchange_code,
                                    "bid_price": quote_data["bid_price"],
                                    "bid_size": quote_data["bid_size"],
                                    "ask_exchange_code": event.ask_exchange_code,
                                    "ask_price": quote_data["ask_price"],
                                    "ask_size": quote_data["ask_size"],
                                    "last_price": quote_data["last_price"],
                                },
                            )
                        else:
                            parsed = parse_option_symbol(event.event_symbol)
                            if parsed:
                                self.last_quotes[event.event_symbol] = {
                                    "quote_data": {
                                        "bid_price": safe_float(event.bid_price),
                                        "ask_price": safe_float(event.ask_price),
                                        "bid_size": safe_float(event.bid_size),
                                        "ask_size": safe_float(event.ask_size),
                                        "timestamp": datetime.now(timezone.utc).isoformat(),
                                    },
                                    "parsed": parsed,
                                }
                                await self.try_send_grouped(symbol, expiry, event.event_symbol)
                            else:
                                logger.error(f"Failed to parse quote symbol: {event.event_symbol}")
                    except Exception as e:
                        logger.error(f"Quote processing error for {event.event_symbol}: {e}")

            async def listen_greeks():
                async for event in streamer.listen(Greeks):
                    try:
                        parsed = parse_option_symbol(event.event_symbol)
                        if parsed:
                            self.last_greeks[event.event_symbol] = {
                                "greeks_data": {
                                    "price": safe_float(event.price),
                                    "IV": safe_float(event.volatility),  
                                    "delta": safe_float(event.delta),
                                    "gamma": safe_float(event.gamma),
                                    "theta": safe_float(event.theta),
                                    "rho": safe_float(event.rho),
                                    "vega": safe_float(event.vega),
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                },
                                "parsed": parsed,
                            }
                            await self.try_send_grouped(symbol, expiry, event.event_symbol)
                        else:
                            logger.error(f"Failed to parse Greeks symbol: {event.event_symbol}")
                    except Exception as e:
                        logger.error(f"Greeks processing error for {event.event_symbol}: {e}")

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
        while True:
            await asyncio.sleep(60)
            logger.info(f"Message rate: {self.message_count}/min")
            self.message_count = 0
            self.last_reset = datetime.now(timezone.utc)

    async def connect(self, websocket: WebSocket, symbol: str, expiry: str, option_symbols: List[str]):
        key = (symbol, expiry)
        await websocket.accept()
        if key not in self.clients:
            self.clients[key] = set()
        self.clients[key].add(websocket)
        logger.info(f"Client connected: {websocket.client} for {symbol} - {expiry}")

        if key not in self.tasks:
            self.tasks[key] = asyncio.create_task(self.start_stream(symbol, expiry, option_symbols))

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
        now = time.time()
        if now - self.last_send < 0.1:
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
