"""CoinGecko REST API service (Demo plan).

Plan is fixed to **Demo**: base URL ``https://api.coingecko.com/api/v3`` and
auth header ``x-cg-demo-api-key`` (per CoinGecko docs — a demo key must never
hit ``pro-api.coingecko.com``, and header/query-param auth must not be mixed).

All calls flow through :func:`app.services.cache_service.run_cached_async`, so
they share the provider budget gate (PROVIDER_DAILY_LIMIT["coingecko"]),
throttle cooldown on 429, request coalescing, and TTL-based caching that keeps
the 30-calls/min demo quota from being burned by repeated dashboard renders.

Endpoint note (per docs): date params vary by endpoint — ``market_chart/range``
uses ISO ``YYYY-MM-DD``, ``/coins/{id}/history`` uses ``DD-MM-YYYY``.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from app.core.config import settings
from app.services.cache_service import run_cached_async

logger = logging.getLogger(__name__)

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
AUTH_HEADER_NAME = "x-cg-demo-api-key"
PROVIDER = "coingecko"

_client: Optional[httpx.AsyncClient] = None


class CoinGeckoError(RuntimeError):
    """Upstream CoinGecko API failure (message includes status/code for the
    cache layer's throttle detection, e.g. a 429 triggers the cooldown)."""


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        headers = {}
        if settings.cg_api_key:
            headers[AUTH_HEADER_NAME] = settings.cg_api_key
        _client = httpx.AsyncClient(
            base_url=COINGECKO_BASE_URL,
            headers=headers,
            timeout=20.0,
        )
    return _client


async def _request(path: str, params: dict[str, Any]) -> Any:
    client = _get_client()
    resp = await client.get(path, params=params)
    if resp.status_code != 200:
        try:
            body = resp.json()
            detail = body.get("error") or body.get("status", {}).get("error_message") or resp.text[:200]
        except ValueError:
            detail = resp.text[:200]
        raise CoinGeckoError(
            f"CoinGecko API error {resp.status_code} on {path}: {detail}"
        )
    return resp.json()


async def _cached_fetch(name: str, path: str, params: dict[str, Any], category: str, ttl: Optional[int] = None) -> Any:
    return await run_cached_async(
        lambda: _request(path, params),
        name=name,
        category=category,
        ttl=ttl,
        provider=PROVIDER,
    )


async def get_markets(
    vs_currency: str = "usd",
    per_page: int = 100,
    page: int = 1,
    order: str = "market_cap_desc",
    sparkline: bool = False,
    price_change_percentage: str = "24h",
) -> list[dict]:
    """Top coins ranked by market cap (price, 24h change, volume, mcap)."""
    params = {
        "vs_currency": vs_currency,
        "per_page": per_page,
        "page": page,
        "order": order,
        "sparkline": str(sparkline).lower(),
        "price_change_percentage": price_change_percentage,
    }
    name = f"coingecko.coins.markets:{vs_currency}:{per_page}:{page}:{order}:{sparkline}"
    return await _cached_fetch(name, "/coins/markets", params, category="quote", ttl=60)


async def get_market_chart(coin_id: str, vs_currency: str = "usd", days: int = 30) -> dict:
    """Historical price/market-cap/volume series. Granularity is automatic:
    1d -> 5-min, 2-90d -> hourly, >90d -> daily."""
    params = {"vs_currency": vs_currency, "days": days}
    name = f"coingecko.market_chart:{coin_id}:{vs_currency}:{days}"
    return await _cached_fetch(name, f"/coins/{coin_id}/market_chart", params, category="historical", ttl=900)


async def get_ohlc(coin_id: str, vs_currency: str = "usd", days: int = 30) -> list:
    """OHLC candlesticks ([timestamp, open, high, low, close], ms)."""
    params = {"vs_currency": vs_currency, "days": days}
    name = f"coingecko.ohlc:{coin_id}:{vs_currency}:{days}"
    return await _cached_fetch(name, f"/coins/{coin_id}/ohlc", params, category="historical", ttl=900)


async def get_trending() -> dict:
    """Top trending coins/NFTs/categories over the last 24h."""
    name = "coingecko.search.trending"
    return await _cached_fetch(name, "/search/trending", {}, category="news", ttl=900)


async def get_top_gainers_losers(vs_currency: str = "usd", duration: str = "24h") -> dict:
    """Top gainers and losers by market-cap band for the given duration."""
    params = {"vs_currency": vs_currency, "duration": duration}
    name = f"coingecko.top_gainers_losers:{vs_currency}:{duration}"
    return await _cached_fetch(name, "/coins/top_gainers_losers", params, category="quote", ttl=300)


async def search_coins(query: str) -> dict:
    """Resolve CoinGecko coin IDs by name/symbol (cached long — IDs are stable)."""
    name = f"coingecko.search:{query.lower()}"
    return await _cached_fetch(name, "/search", {"query": query}, category="search")


async def get_global() -> dict:
    """Global crypto aggregate stats (total market cap, dominance, volume)."""
    name = "coingecko.global"
    return await _cached_fetch(name, "/global", {}, category="quote", ttl=120)
