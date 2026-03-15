"""Market data integration.

We primarily use Polymarket's public Gamma API because it does not require
credentials and exposes outcomes + prices.

If in the future we want orderbook-level pricing, we can extend this file
with the CLOB API (which typically requires an API key / auth).

Env vars:
- GAMMA_API_BASE (default: https://gamma-api.polymarket.com)
- MARKET_QUERY (optional): substring filter on question/slug
- MARKET_LIMIT (default: 50)
- MARKET_SOURCE (default: gamma)
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

import requests

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GammaMarket:
    external_id: str
    slug: str | None
    question: str
    condition_id: str | None
    active: bool
    closed: bool
    end_date: datetime | None
    updated_at_external: datetime | None
    outcomes: list[str]
    outcome_prices: list[float]
    clob_token_ids: list[str] | None


def _parse_dt(v: Any) -> datetime | None:
    if not v:
        return None
    if isinstance(v, datetime):
        return v
    if isinstance(v, str):
        # Gamma usually returns ISO with Z
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _parse_json_list_str(v: Any) -> list[Any]:
    """Gamma returns some fields as JSON-encoded strings."""
    if v is None:
        return []
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        try:
            parsed = json.loads(v)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []
    return []


def _to_float(x: Any) -> float | None:
    try:
        if x is None:
            return None
        return float(x)
    except (TypeError, ValueError):
        return None


class GammaClient:
    def __init__(self, base_url: str | None = None, timeout_s: int = 20):
        self.base_url = (base_url or os.getenv("GAMMA_API_BASE") or "https://gamma-api.polymarket.com").rstrip("/")
        self.timeout_s = timeout_s

    def list_markets(self, *, active: bool = True, closed: bool = False, limit: int = 50) -> list[dict[str, Any]]:
        url = f"{self.base_url}/markets"
        params = {
            "active": str(active).lower(),
            "closed": str(closed).lower(),
            "limit": str(limit),
        }
        r = requests.get(url, params=params, timeout=self.timeout_s)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, list):
            raise ValueError("Gamma /markets returned non-list")
        return data

    def get_market(self, market_id: str) -> dict[str, Any]:
        url = f"{self.base_url}/markets/{market_id}"
        r = requests.get(url, timeout=self.timeout_s)
        r.raise_for_status()
        data = r.json()
        if not isinstance(data, dict):
            raise ValueError("Gamma /markets/{id} returned non-dict")
        return data


def fetch_gamma_markets() -> list[GammaMarket]:
    """Fetch and parse a batch of markets from Gamma.

    We do a cheap list call and then hydrate each market (to get outcomes/prices).
    This is still fast enough for small limits (<= 100) and avoids relying on
    list payload shape.
    """

    query = (os.getenv("MARKET_QUERY") or "").strip().lower()
    limit = int(os.getenv("MARKET_LIMIT") or "50")

    client = GammaClient()
    listed = client.list_markets(active=True, closed=False, limit=limit)

    markets: list[GammaMarket] = []
    for item in listed:
        market_id = str(item.get("id") or "").strip()
        if not market_id:
            continue

        # Optional query filter using cheap list fields first
        if query:
            q = str(item.get("question") or "").lower()
            slug = str(item.get("slug") or "").lower()
            if query not in q and query not in slug:
                continue

        try:
            full = client.get_market(market_id)
            outcomes = [str(x) for x in _parse_json_list_str(full.get("outcomes"))]
            prices_raw = _parse_json_list_str(full.get("outcomePrices"))
            outcome_prices: list[float] = []
            for x in prices_raw:
                fx = _to_float(x)
                if fx is None:
                    fx = 0.0
                outcome_prices.append(fx)

            clob_token_ids_raw = _parse_json_list_str(full.get("clobTokenIds"))
            clob_token_ids = [str(x) for x in clob_token_ids_raw] if clob_token_ids_raw else None

            markets.append(
                GammaMarket(
                    external_id=market_id,
                    slug=full.get("slug"),
                    question=str(full.get("question") or "").strip() or market_id,
                    condition_id=full.get("conditionId"),
                    active=bool(full.get("active")),
                    closed=bool(full.get("closed")),
                    end_date=_parse_dt(full.get("endDate")),
                    updated_at_external=_parse_dt(full.get("updatedAt") or full.get("updatedAtIso")),
                    outcomes=outcomes,
                    outcome_prices=outcome_prices,
                    clob_token_ids=clob_token_ids,
                )
            )
        except Exception:
            # Fail-soft: keep going; we'll log once with context
            logger.exception("[gamma] failed to hydrate market | market_id=%s", market_id)
            continue

    return markets


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def pair_outcomes_with_prices(outcomes: Iterable[str], prices: Iterable[float]) -> list[tuple[int, str, float | None]]:
    out = list(outcomes)
    pr = list(prices)
    n = max(len(out), len(pr))
    pairs: list[tuple[int, str, float | None]] = []
    for i in range(n):
        name = out[i] if i < len(out) else f"outcome_{i}"
        price = pr[i] if i < len(pr) else None
        pairs.append((i, name, price))
    return pairs
