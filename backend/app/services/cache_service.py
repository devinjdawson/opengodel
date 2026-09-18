"""Centralized caching + request-coalescing layer for OpenBB SDK calls.

Why this exists:
  Every widget endpoint currently calls the (synchronous) OpenBB SDK directly on
  each request. Several providers have hard daily/per-minute limits:
    - Marketaux: hard daily request cap (email-on-exhaustion)
    - FMP:       250 requests/day on the free tier
    - YFinance:  aggressive throttling on bulk (S&P 500) requests
  Without a shared cache, multiple widgets / multiple users / repeated renders all
  hit the provider independently and burn the quota.

This module provides:
  1. A process-wide TTL cache (Redis if configured, else in-memory). All widget
     requests go through one backend process, so in-memory is sufficient to cut
     redundant provider calls dramatically.
  2. Per-category + per-provider TTLs so expensive/limited providers are cached
     longer (Marketaux sentiment cached for hours, not minutes).
  3. Request coalescing: concurrent identical in-flight calls collapse into a
     single provider request.
  4. Optional force-refresh used by the prefetch scheduler to keep hot data warm.
"""

from __future__ import annotations

import asyncio
import functools
import hashlib
import json
import logging
import os
import tempfile
import threading
import time
from typing import Any, Callable, Optional

from openbb import obb

from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# TTL configuration (seconds)
# ---------------------------------------------------------------------------
TTL_CONFIG: dict[str, int] = {
    "quote": 30,           # real-time equity/etf/index prices
    "intraday": 60,        # intraday price series
    "historical": 86_400,  # EOD candles -> daily
    "news": 900,           # 15 min
    "sentiment": 1_800,    # 30 min base for Marketaux sentiment
    "fundamentals": 86_400,  # financials / estimates / key metrics -> daily
    "options": 60,
    "macro": 86_400,       # FRED / Fed data -> daily
    "search": 86_400,
    "dividend": 86_400,
    "default": 300,
}

# Providers with stricter quotas get a longer cache multiplier.
PROVIDER_MULTIPLIER: dict[str, float] = {
    "marketaux": 4.0,   # very limited daily requests
    "fmp": 3.0,         # 250/day free tier
    "yfinance": 1.0,
    "cboe": 1.0,
    "fred": 1.0,
    "federal_reserve": 1.0,
    "nasdaq": 1.0,
    "intrinio": 1.5,
    "polygon": 1.0,
    "alpha_vantage": 1.0,
}

# Hard daily upstream-call budgets. Once a provider hits its cap we stop making
# upstream calls entirely and degrade gracefully (serve stale cache, else raise).
PROVIDER_DAILY_LIMIT: dict[str, int] = {
    "fmp": 240,        # 250/day documented; leave headroom for manual testing
    "marketaux": 95,   # ~100/day documented; leave headroom
}

# After a throttling-style failure (429/402/quota), block the provider for this
# long before trying again — protects against hourly/burst limits that daily
# budgets cannot express.
PROVIDER_COOLDOWN_SECONDS = 600
_THROTTLE_MARKERS = (
    "429",
    "too many requests",
    "rate limit",
    "ratelimit",
    "quota",
    "402",
    "payment required",
)


class ProviderBlocked(RuntimeError):
    """Upstream call refused locally: provider is budget-capped or cooling down."""


class ProviderBudgetExhausted(ProviderBlocked):
    """Daily upstream-call budget spent and no cached (even stale) data exists."""


# ---------------------------------------------------------------------------
# In-memory store (single backend process => sufficient; Redis optional later)
# ---------------------------------------------------------------------------
_memory_store: dict[str, tuple[float, Any]] = {}
_key_locks: dict[str, asyncio.Lock] = {}
_global_lock = asyncio.Lock()
_store_lock = threading.Lock()  # guards _memory_store across worker threads
_MAX_ENTRIES = 4_000

# Per-provider daily usage counters: {"upstream": N, "hits": M, "errors": E,
# "budget_blocked": B, "cooldown_blocked": C}. Lets /cache/stats show real quota
# consumption instead of guessing from docs.
_usage: dict[str, dict[str, int]] = {}
_usage_date: str = ""

# Counters survive backend restarts via a JSON file in the system temp dir,
# so a mid-day restart cannot silently double-burn a provider's daily quota.
_USAGE_FILE = os.path.join(tempfile.gettempdir(), "opengodel_provider_usage.json")

# Provider -> epoch until which upstream calls are blocked (throttle circuit breaker).
_cooldowns: dict[str, float] = {}


def _persist_usage_locked() -> None:
    """Write counters to disk. Caller must hold _store_lock."""
    payload = {
        "date": _usage_date,
        "usage": {p: dict(c) for p, c in _usage.items()},
    }
    try:
        tmp = f"{_USAGE_FILE}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f)
        os.replace(tmp, _USAGE_FILE)
    except OSError:
        pass  # best-effort only; caching must never crash the app


def _load_usage() -> None:
    """Restore today's counters from disk (called once at import)."""
    global _usage, _usage_date
    try:
        with open(_USAGE_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("date") == time.strftime("%Y-%m-%d"):
            restored = {
                p: {k: int(v) for k, v in c.items()}
                for p, c in data.get("usage", {}).items()
            }
            with _store_lock:
                _usage_date = data["date"]
                _usage = restored
    except (OSError, ValueError):
        pass


def _record_usage(provider: Optional[str], kind: str) -> None:
    global _usage_date
    today = time.strftime("%Y-%m-%d")
    key = (provider or "unknown").lower()
    with _store_lock:
        if today != _usage_date:
            _usage.clear()
            _cooldowns.clear()
            _usage_date = today
        entry = _usage.setdefault(
            key, {"upstream": 0, "hits": 0, "errors": 0, "budget_blocked": 0, "cooldown_blocked": 0}
        )
        entry[kind] = entry.get(kind, 0) + 1
        _persist_usage_locked()


_load_usage()


def _is_throttle_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(marker in msg for marker in _THROTTLE_MARKERS)


def _note_provider_error(provider: Optional[str], exc: Exception) -> None:
    """Trip the throttle circuit breaker when an error looks rate-limit related."""
    if not _is_throttle_error(exc):
        return
    key = (provider or "unknown").lower()
    until = time.time() + PROVIDER_COOLDOWN_SECONDS
    with _store_lock:
        if until > _cooldowns.get(key, 0):
            _cooldowns[key] = until
    logger.warning(
        "Provider '%s' looks rate-limited (%s); cooling down for %ss",
        provider, str(exc)[:120], PROVIDER_COOLDOWN_SECONDS,
    )


def _in_cooldown(provider: Optional[str]) -> bool:
    key = (provider or "unknown").lower()
    with _store_lock:
        return _cooldowns.get(key, 0) > time.time()


def _resolve_ttl(category: str, provider: Optional[str]) -> int:
    base = TTL_CONFIG.get(category, TTL_CONFIG["default"])
    mult = PROVIDER_MULTIPLIER.get((provider or "").lower(), 1.0)
    return int(base * mult)


def _make_cache_key(name: str, args: tuple, kwargs: dict) -> str:
    payload = {
        "n": name,
        "a": [str(a) for a in args],
        "k": {k: str(v) for k, v in sorted(kwargs.items())},
    }
    raw = repr(payload).encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()[:24]
    return f"obb:{name}:{digest}"


def _memory_get(key: str, allow_stale: bool = False) -> Any | None:
    """Read an entry. Expired entries are NOT popped here: they remain as
    graceful-degradation fallbacks for when a provider budget is exhausted
    (eviction under _MAX_ENTRIES pressure reclaims them)."""
    with _store_lock:
        item = _memory_store.get(key)
        if item is None:
            return None
        expires_at, value = item
        if expires_at < time.time() and not allow_stale:
            return None
        return value


def _budget_remaining(provider: Optional[str]) -> Optional[int]:
    """Calls left today for this provider, or None if unlimited."""
    key = (provider or "unknown").lower()
    limit = PROVIDER_DAILY_LIMIT.get(key)
    if limit is None:
        return None
    with _store_lock:
        used = (_usage.get(key, {}) or {}).get("upstream", 0)
    return max(0, limit - used)


def _upstream_gate(provider: Optional[str], cache_key: str) -> Optional[str]:
    """Decide whether an upstream call may proceed.

    Returns None when the call may proceed, otherwise a short reason string
    ("daily budget exhausted" / "throttle cooldown"). Blocked calls are counted
    and logged; the caller should degrade (stale cache or raise).
    """
    remaining = _budget_remaining(provider)
    if remaining is not None and remaining <= 0:
        reason = "daily budget exhausted"
        kind = "budget_blocked"
    elif _in_cooldown(provider):
        reason = "throttle cooldown"
        kind = "cooldown_blocked"
    else:
        return None
    _record_usage(provider, kind)
    logger.warning(
        "Provider '%s' blocked upstream call for %s: %s", provider, cache_key, reason,
    )
    return reason


def _memory_set(key: str, value: Any, ttl: int) -> None:
    with _store_lock:
        _memory_store[key] = (time.time() + ttl, value)
        if len(_memory_store) > _MAX_ENTRIES:
            # Evict roughly half the expired/excess entries.
            now = time.time()
            expired = [k for k, (exp, _) in _memory_store.items() if exp < now]
            for k in expired[: len(expired) // 2]:
                _memory_store.pop(k, None)


async def _acquire_key_lock(key: str) -> asyncio.Lock:
    async with _global_lock:
        lock = _key_locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            _key_locks[key] = lock
        return lock


async def _execute(func: Callable, args: tuple, kwargs: dict) -> Any:
    loop = asyncio.get_event_loop()
    if kwargs:
        return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
    return await loop.run_in_executor(None, func, *args)


async def run_obb(
    func: Callable,
    *args,
    name: str,
    category: str = "default",
    ttl: Optional[int] = None,
    provider: Optional[str] = None,
    force: bool = False,
    **kwargs,
) -> Any:
    """Run a synchronous OpenBB SDK call through the thread pool with caching.

    Args:
        func:      The OpenBB callable, e.g. ``obb.equity.price.quote``.
        name:      Stable dotted path identifier, e.g. ``"equity.price.quote"``.
                   Required to build a deterministic cache key.
        category:  Data category driving the base TTL (see TTL_CONFIG).
        ttl:       Explicit TTL override in seconds (bypasses category logic).
        provider:  Provider name; used for both the call and the TTL multiplier.
        force:     When True, skip the cache read and refresh (used by prefetch).
        **kwargs:  Forwarded to ``func`` (the OpenBB request parameters).
    """
    if provider is not None:
        kwargs.setdefault("provider", provider)

    cache_key = _make_cache_key(name, args, kwargs)
    effective_ttl = ttl if ttl is not None else _resolve_ttl(category, provider)

    if not force:
        cached = _memory_get(cache_key)
        if cached is not None:
            _record_usage(provider, "hits")
            return cached

    lock = await _acquire_key_lock(cache_key)
    async with lock:
        # Double-check after acquiring the per-key lock (another coroutine may
        # have populated the cache while we waited).
        if not force:
            cached = _memory_get(cache_key)
            if cached is not None:
                _record_usage(provider, "hits")
                return cached

        block_reason = _upstream_gate(provider, cache_key)
        if block_reason:
            stale = _memory_get(cache_key, allow_stale=True)
            if stale is not None:
                _record_usage(provider, "hits")
                return stale
            raise ProviderBlocked(
                f"Provider '{provider}' temporarily refusing upstream calls ({block_reason}); "
                f"no cached data available for this request."
            )
        try:
            result = await _execute(func, args, kwargs)
        except Exception as exc:
            _record_usage(provider, "errors")
            _note_provider_error(provider, exc)
            raise
        _memory_set(cache_key, result, effective_ttl)
        _record_usage(provider, "upstream")
        return result


def run_obb_sync(
    func: Callable,
    *args,
    name: str,
    category: str = "default",
    ttl: Optional[int] = None,
    provider: Optional[str] = None,
    force: bool = False,
    **kwargs,
) -> Any:
    """Synchronous variant of :func:`run_obb`.

    Used by code that runs outside the asyncio event loop (the scheduler, the
    synchronous ``OpenBBService`` wrapper). Performs the same TTL caching but
    without request coalescing.
    """
    if provider is not None:
        kwargs.setdefault("provider", provider)

    cache_key = _make_cache_key(name, args, kwargs)
    effective_ttl = ttl if ttl is not None else _resolve_ttl(category, provider)

    if not force:
        cached = _memory_get(cache_key)
        if cached is not None:
            _record_usage(provider, "hits")
            return cached

    block_reason = _upstream_gate(provider, cache_key)
    if block_reason:
        stale = _memory_get(cache_key, allow_stale=True)
        if stale is not None:
            _record_usage(provider, "hits")
            return stale
        raise ProviderBlocked(
            f"Provider '{provider}' temporarily refusing upstream calls ({block_reason}); "
            f"no cached data available for this request."
        )
    try:
        result = func(*args, **kwargs)
    except Exception as exc:
        _record_usage(provider, "errors")
        _note_provider_error(provider, exc)
        raise
    _memory_set(cache_key, result, effective_ttl)
    _record_usage(provider, "upstream")
    return result


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------
def cache_stats() -> dict[str, Any]:
    with _store_lock:
        now = time.time()
        live = sum(1 for exp, _ in _memory_store.values() if exp >= now)
        expired = len(_memory_store) - live
        usage_copy = {p: dict(c) for p, c in sorted(_usage.items())}
        upstream_used = {p: c.get("upstream", 0) for p, c in _usage.items()}
        cooldowns = {
            p: int(max(0, until - now)) for p, until in _cooldowns.items() if until > now
        }
    # Budgets computed AFTER releasing _store_lock (_budget_remaining would
    # otherwise deadlock on the same non-reentrant lock).
    budgets = {
        p: {"limit": limit, "remaining": max(0, limit - upstream_used.get(p, 0))}
        for p, limit in sorted(PROVIDER_DAILY_LIMIT.items())
    }
    return {
        "entries": len(_memory_store),
        "live": live,
        "expired": expired,
        "keys_sample": sorted(_memory_store.keys())[:20],
        "usage_date": _usage_date,
        "usage": usage_copy,
        "budgets": budgets,
        "cooldowns_seconds": cooldowns,
    }


def clear_cache() -> int:
    with _store_lock:
        count = len(_memory_store)
        _memory_store.clear()
    return count
