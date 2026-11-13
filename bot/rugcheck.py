"""RugCheck summary lookup and pass/fail assessment.

GET https://api.rugcheck.xyz/v1/tokens/{mint}/report/summary (no key).
score_normalised runs 0-100, higher = riskier. Each risk has a name and a level.
"""
from .net import RateLimiter, get_json

BASE = "https://api.rugcheck.xyz"


class RugCheck:
    def __init__(self):
        self.limiter = RateLimiter(2.5)
        self.calls = 0

    def summary(self, mint: str) -> dict:
        self.calls += 1
        data = get_json(f"{BASE}/v1/tokens/{mint}/report/summary", self.limiter, timeout=15, retries=1)
        if not isinstance(data, dict):
            raise ValueError("unexpected rugcheck response")
        return data


def compact(summary: dict) -> dict:
    """Keep only what the rules and the trade journal need."""
    risks = []
    for r in summary.get("risks") or []:
        if isinstance(r, dict):
            risks.append([str(r.get("name", "")), str(r.get("level", "")).lower()])
    return {
        "score_normalised": summary.get("score_normalised"),
        "score": summary.get("score"),
        "lp_locked_pct": summary.get("lpLockedPct"),
        "risks": risks,
    }


def assess(c: dict, rules: dict):
    """Return (ok, reason). `c` is a compact() summary."""
    score = c.get("score_normalised")
    if not isinstance(score, (int, float)):
        return False, "rugcheck_no_score"
    if score > rules["max_score_normalised"]:
        return False, "rugcheck_score"
    blocked = {lvl.lower() for lvl in rules.get("block_risk_levels", [])}
    for name, level in c.get("risks", []):
        if level in blocked:
            return False, "rugcheck_risk:" + name[:40]
    return True, None
