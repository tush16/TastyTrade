import re
from datetime import datetime, timezone
from typing import Optional
from config.logging import logger
import pytz


def safe_float(value) -> float:
    try:
        return float(value) if value is not None else 0.0
    except (ValueError, TypeError):
        return 0.0
    
def sanitize_inf(data):
    """Recursively replace Infinity/-Infinity/NaN with None (JSON-safe)."""
    if isinstance(data, dict):
        return {k: sanitize_inf(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_inf(v) for v in data]
    elif isinstance(data, float):
        if data == float("inf") or data == float("-inf") or data != data:  # NaN check
            return None
        return data
    return data

def parse_option_symbol(symbol: str) -> Optional[dict]:
    """
    Parse Tastytrade option symbol like '.META250822C620'
    Returns both raw + human-readable fields.
    """
    pattern = r'^\.(\w+?)(\d{6})([CP])(\d+\.?\d*)$'
    m = re.match(pattern, symbol.strip())
    if not m:
        logger.error(f"Invalid option symbol format: {symbol}")
        return None
    
    underlying, expiry, call_put, strike = m.groups()
    return {
        "underlying": underlying,
        "expiry": expiry,  # 'YYMMDD'
        "expiry_date": datetime.strptime(expiry, "%y%m%d").strftime("%Y-%m-%d"),
        "call_put": call_put,  # 'C' or 'P'
        "type": "call" if call_put == "C" else "put",
        "strike": safe_float(strike)
    }


def expiry_yymmdd_to_utc_16et(yymmdd: str) -> datetime:
    """
    Convert 'YYMMDD' to a datetime at 16:00 America/New_York in UTC.
    Example: '250822' -> 2025-08-22 20:00:00+00:00 (EDT is UTC-4).
    """
    try:
        year = 2000 + int(yymmdd[0:2])
        month = int(yymmdd[2:4])
        day = int(yymmdd[4:6])
        ny_tz = pytz.timezone("America/New_York")
        expiry_et = ny_tz.localize(datetime(year, month, day, 16, 0, 0))
        return expiry_et.astimezone(timezone.utc)
    except Exception as e:
        logger.error(f"Error converting expiry {yymmdd} to 16:00 ET: {e}")
        return datetime.now(timezone.utc)
