from datetime import datetime, timezone
import math
from config.logging import logger
from scipy.stats import norm

CONTRACT_MULTIPLIER = 100.0


def calculate_pmp_pop_ce_sell(
    current_price: float,
    strike: float,
    premium_ce: float,
    expiry_utc: datetime,
    iv_instrument: float,
    iv_ce: float,
):
    sqrt_252 = math.sqrt(252.0)
    sqrt_365 = math.sqrt(365.0)
    constant = sqrt_252 / sqrt_365

    now = datetime.now(timezone.utc)
    tte_days = (expiry_utc - now).total_seconds() / 86400.0
    if tte_days <= 0:
        logger.warning(f"Option expired: TTE {tte_days} days")
        return 0.0, 0.0, 0.0, math.inf, None  # pmp, pop, max_profit, max_loss, ev

    sqrt_tte = math.sqrt(tte_days)
    expected_move = sqrt_tte / sqrt_365

    # Per your sheet (kept for parity; not used later):
    _vol_instr = iv_instrument * constant
    _intraday_vol = _vol_instr / sqrt_252
    _expiry_vol = _intraday_vol * sqrt_tte

    stddev = max(current_price * expected_move * iv_ce, 1e-12)

    breakeven = strike + premium_ce
    z_pmp = (strike - current_price) / stddev
    pmp = norm.cdf(z_pmp) * 100.0

    z_pop = (breakeven - current_price) / stddev
    pop = norm.cdf(z_pop) * 100.0

    # P&L (per contract)
    max_profit = premium_ce * CONTRACT_MULTIPLIER
    max_loss = math.inf
    ev = None  # unbounded loss → undefined simple EV

    return pmp, pop, max_profit, max_loss, ev


def calculate_pmp_pop_pe_sell(
    current_price: float,
    strike: float,
    premium_pe: float,
    expiry_utc: datetime,
    iv_instrument: float,
    iv_pe: float,
):
    sqrt_252 = math.sqrt(252.0)
    sqrt_365 = math.sqrt(365.0)
    constant = sqrt_252 / sqrt_365

    now = datetime.now(timezone.utc)
    tte_days = (expiry_utc - now).total_seconds() / 86400.0
    if tte_days <= 0:
        logger.warning(f"Option expired: TTE {tte_days} days")
        return 0.0, 0.0, 0.0, 0.0, 0.0

    sqrt_tte = math.sqrt(tte_days)
    expected_move = sqrt_tte / sqrt_365

    _vol_instr = iv_instrument * constant
    _intraday_vol = _vol_instr / sqrt_252
    _expiry_vol = _intraday_vol * sqrt_tte

    stddev = max(current_price * expected_move * iv_pe, 1e-12)

    breakeven = strike - premium_pe
    z_pmp = (strike - current_price) / stddev
    pmp = (1.0 - norm.cdf(z_pmp)) * 100.0

    z_pop = (breakeven - current_price) / stddev
    pop = (1.0 - norm.cdf(z_pop)) * 100.0

    # P&L (per contract)
    max_profit = premium_pe * CONTRACT_MULTIPLIER
    # Worst case underlying → 0: loss ≈ (strike - premium) * 100, floor at 0
    max_loss = max((strike - premium_pe) * CONTRACT_MULTIPLIER, 0.0)
    # Simple EV using POP as prob(keep credit)
    ev = (pop / 100.0) * max_profit - (1.0 - pop / 100.0) * max_loss

    return pmp, pop, max_profit, max_loss, ev
