"""Minimal HTTP JSON client (stdlib only) with pacing and retries."""
import json
import time
import urllib.error
import urllib.request


class ApiError(Exception):
    pass


class RateLimiter:
    """Keeps at least `min_interval` seconds between calls."""

    def __init__(self, min_interval: float):
        self.min_interval = min_interval
        self._last = 0.0

    def wait(self) -> None:
        gap = time.monotonic() - self._last
        if gap < self.min_interval:
            time.sleep(self.min_interval - gap)
        self._last = time.monotonic()


def get_json(url: str, limiter: RateLimiter = None, timeout: float = 12, retries: int = 2):
    last = None
    for attempt in range(retries + 1):
        if limiter:
            limiter.wait()
        try:
            req = urllib.request.Request(
                url,
                headers={"Accept": "application/json", "User-Agent": "solana-paper-trader/1.0"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code == 429 or e.code >= 500:
                time.sleep(2.0 * (attempt + 1))
                continue
            break
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as e:
            last = type(e).__name__
            time.sleep(1.0 * (attempt + 1))
    raise ApiError(f"{last} for {url[:120]}")
