"""US equity market-hours awareness for cache prefetch scheduling."""

from __future__ import annotations

import datetime as dt
from typing import Optional

# US/Eastern trading session (regular hours, ignoring early closes/holidays).
_MARKET_OPEN = dt.time(9, 30)
_MARKET_CLOSE = dt.time(16, 0)


def _eastern_now() -> dt.datetime:
    try:
        from zoneinfo import ZoneInfo

        return dt.datetime.now(ZoneInfo("America/New_York"))
    except Exception:
        # Fallback: assume server local time is already US/Eastern.
        return dt.datetime.now()


def is_market_open(now: Optional[dt.datetime] = None) -> bool:
    """Return True if US regular-session trading is open at ``now`` (ET)."""
    now = now or _eastern_now()
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    return _MARKET_OPEN <= now.time() <= _MARKET_CLOSE


def next_market_open(now: Optional[dt.datetime] = None) -> dt.datetime:
    """Return the next upcoming regular-session open (ET)."""
    now = now or _eastern_now()
    candidate = now.replace(hour=9, minute=30, second=0, microsecond=0)
    if is_market_open(now) or now.time() > _MARKET_CLOSE:
        candidate = candidate + dt.timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate = candidate + dt.timedelta(days=1)
    return candidate
