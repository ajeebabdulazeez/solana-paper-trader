"""DexScreener public API client.

Limits per the official reference: 60 requests/minute on profile, boost, takeover
and meta endpoints; 300/minute on pair and token endpoints. No API key.

Response shapes differ by endpoint (bare list vs {"pairs": [...]}) so every
method normalises to a list and never assumes one shape.
"""
from urllib.parse import quote

from .net import RateLimiter, get_json

BASE = "https://api.dexscreener.com"


def _as_list(data, key=None) -> list:
    if data is None:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        if key and isinstance(data.get(key), list):
            return [x for x in data[key] if isinstance(x, dict)]
        if "pairs" in data and isinstance(data["pairs"], list):
            return [x for x in data["pairs"] if isinstance(x, dict)]
        if key is None and ("tokenAddress" in data or "pairAddress" in data):
            return [data]
    return []


class DexScreener:
    def __init__(self):
        self.slow = RateLimiter(1.1)   # 60/min group
        self.fast = RateLimiter(0.25)  # 300/min group
        self.calls = 0

    def _get(self, path, limiter):
        self.calls += 1
        return get_json(BASE + path, limiter)

    # --- discovery feeds (60/min) ---
    def boosts_latest(self) -> list:
        return _as_list(self._get("/token-boosts/latest/v1", self.slow))

    def boosts_top(self) -> list:
        return _as_list(self._get("/token-boosts/top/v1", self.slow))

    def profiles_latest(self) -> list:
        return _as_list(self._get("/token-profiles/latest/v1", self.slow))

    def takeovers_latest(self) -> list:
        return _as_list(self._get("/community-takeovers/latest/v1", self.slow))

    def metas_trending(self) -> list:
        data = self._get("/metas/trending/v1", self.slow)
        return [m for m in data if isinstance(m, dict)] if isinstance(data, list) else []

    def meta_pairs(self, slug: str) -> list:
        return _as_list(self._get(f"/metas/meta/v1/{quote(slug, safe='')}", self.slow), "pairs")

    # --- pair data (300/min) ---
    def pairs_for_tokens(self, chain: str, addresses: list) -> list:
        csv = ",".join(addresses)
        return _as_list(self._get(f"/tokens/v1/{chain}/{csv}", self.fast))

    def pairs_for_token(self, chain: str, address: str) -> list:
        return _as_list(self._get(f"/token-pairs/v1/{chain}/{address}", self.fast))

    def search(self, q: str) -> list:
        return _as_list(self._get(f"/latest/dex/search?q={quote(q)}", self.fast))
