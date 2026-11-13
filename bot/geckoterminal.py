"""GeckoTerminal public API: used only to DISCOVER tokens (trending and most-traded Solana pools).

Base https://api.geckoterminal.com/api/v2, no key. Documented limit is 30 calls/minute but the
live API returned HTTP 429 on the 10th call in about 22 seconds, so calls are spaced 6.5s apart.
Prices and trade decisions still come from DexScreener; this just widens the net,
because DexScreener's own feeds skew to brand-new or paid-for tokens.
"""
from datetime import datetime, timezone

from .net import RateLimiter, get_json
from .strategy import WSOL, num

BASE = "https://api.geckoterminal.com/api/v2"
NOT_TARGETS = {
    WSOL,
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",  # USDT
}


class GeckoTerminal:
    def __init__(self):
        self.limiter = RateLimiter(6.5)
        self.calls = 0

    def _pools(self, path) -> list:
        self.calls += 1
        data = get_json(BASE + path, self.limiter, retries=1)
        rows = data.get("data") if isinstance(data, dict) else None
        return [r for r in rows if isinstance(r, dict)] if isinstance(rows, list) else []

    def trending(self, page: int) -> list:
        return self._pools(f"/networks/solana/trending_pools?page={page}")

    def top(self, sort: str, page: int) -> list:
        return self._pools(f"/networks/solana/pools?sort={sort}&page={page}")


def _token_id(pool, side):
    ident = (((pool.get("relationships") or {}).get(side) or {}).get("data") or {}).get("id") or ""
    return ident.split("_", 1)[1] if ident.startswith("solana_") else None


def pick_tokens(pools: list, now, min_reserve_usd: float, max_age_days: float) -> list:
    """Token addresses from pools that are liquid enough and not too old. Unknown age is kept."""
    out = []
    for p in pools:
        a = p.get("attributes") or {}
        reserve = num(a.get("reserve_in_usd"))
        if reserve is None or reserve < min_reserve_usd:
            continue
        created = a.get("pool_created_at")
        if created:
            try:
                dt = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                if (now - dt).total_seconds() / 86400 > max_age_days:
                    continue
            except ValueError:
                pass
        token = _token_id(p, "base_token")
        if token in NOT_TARGETS:
            token = _token_id(p, "quote_token")
        if token and token not in NOT_TARGETS and token not in out:
            out.append(token)
    return out
