from decimal import Decimal
import re
from datetime import datetime
from typing import Optional, Dict


def safe_float(val):
    if isinstance(val, Decimal):
        return float(val)
    return val


def parse_option_symbol(symbol: str) -> Optional[Dict]:
    """
    Parses option symbols like .SPY230830C387.5
    Returns metadata or None if format is invalid.
    """
    pattern = r"\.(?P<underlying>[A-Z]+)(?P<date>\d{6})(?P<type>[CP])(?P<strike>\d+(?:\.\d+)?)"
    match = re.match(pattern, symbol)

    if not match:
        return None

    groups = match.groupdict()
    try:
        return {
            "underlying": groups["underlying"],
            "expiry": datetime.strptime(groups["date"], "%y%m%d").strftime("%Y-%m-%d"),
            "type": "call" if groups["type"] == "C" else "put",
            "strike": float(groups["strike"]),
        }
    except Exception:
        return None
