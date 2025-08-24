import asyncpg
from typing import Dict, Any


class OptionChainRepository:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def insert_option_data(self, data: Dict[str, Any]) -> None:
        query = """
        INSERT INTO option_chain_data (
            symbol, underlying_symbol, expiry_date, strike_price, option_type,
            iv_strike, mid_price, bid_price, ask_price, vega, theta,
            pmp, pop, max_profit, max_loss, ev, underlying_price
        )
        VALUES (
            $1, $2, $3, $4, $5,
            $6, $7, $8, $9, $10, $11,
            $12, $13, $14, $15, $16, $17
        )
        ON CONFLICT ( symbol, underlying_symbol, expiry_date, strike_price, option_type, iv_strike, mid_price, bid_price, ask_price, vega, theta)
        DO NOTHING
        """
        async with self.conn.transaction():
            await self.conn.execute(
                query,
                data["symbol"],
                data["underlying_symbol"],
                data["expiry_date"],
                data["strike_price"],
                data["option_type"],
                data["iv_strike"],
                data["mid_price"],
                data["bid_price"],
                data["ask_price"],
                data["vega"],
                data["theta"],
                data["pmp"],
                data["pop"],
                data["max_profit"],
                data["max_loss"],
                data["ev"],
                data["underlying_price"],
            )
