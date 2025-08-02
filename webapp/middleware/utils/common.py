from decimal import Decimal


def safe_float(val):
    if isinstance(val, Decimal):
        return float(val)
    return val
