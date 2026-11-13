"""Pure decision logic: normalise pair data, apply rulebook filters. No I/O here."""
from statistics import median

WSOL = "So11111111111111111111111111111111111111112"


def num(x):
    try:
        if x is None:
            return None
        v = float(x)
        return v if v == v and v not in (float("inf"), float("-inf")) else None
    except (TypeError, ValueError):
        return None


def _period(d, key):
    return num(d.get(key)) if isinstance(d, dict) else None


def pair_view(pair: dict, now_ms: int) -> dict:
    """Flatten one DexScreener pair object into the fields the rules use."""
    base = pair.get("baseToken") or {}
    quote = pair.get("quoteToken") or {}
    liq = pair.get("liquidity") or {}
    txns = pair.get("txns") or {}
    vol = pair.get("volume") or {}
    chg = pair.get("priceChange") or {}
    created = num(pair.get("pairCreatedAt"))
    age_days = (now_ms - created) / 86_400_000 if created else None

    def tx(period, side):
        p = txns.get(period)
        return int(num(p.get(side)) or 0) if isinstance(p, dict) else 0

    return {
        "token": base.get("address"),
        "symbol": base.get("symbol") or "?",
        "name": base.get("name") or "",
        "pair": pair.get("pairAddress"),
        "dex": pair.get("dexId"),
        "chain": pair.get("chainId"),
        "quote_symbol": (quote.get("symbol") or "").upper(),
        "quote_addr": quote.get("address"),
        "price_usd": num(pair.get("priceUsd")),
        "price_native": num(pair.get("priceNative")),
        "liq_usd": num(liq.get("usd")) if isinstance(liq, dict) else None,
        "mcap": num(pair.get("marketCap")) or num(pair.get("fdv")),
        "vol_m5": _period(vol, "m5") or 0.0,
        "vol_h1": _period(vol, "h1") or 0.0,
        "vol_h6": _period(vol, "h6") or 0.0,
        "vol_h24": _period(vol, "h24") or 0.0,
        "buys_m5": tx("m5", "buys"), "sells_m5": tx("m5", "sells"),
        "buys_h1": tx("h1", "buys"), "sells_h1": tx("h1", "sells"),
        "buys_h24": tx("h24", "buys"), "sells_h24": tx("h24", "sells"),
        # A missing priceChange period means no trades in that window: treat as flat.
        "chg_m5": _period(chg, "m5") or 0.0,
        "chg_h1": _period(chg, "h1") or 0.0,
        "chg_h6": _period(chg, "h6") or 0.0,
        "chg_h24": _period(chg, "h24") or 0.0,
        "age_days": age_days,
        "boosts": int(num((pair.get("boosts") or {}).get("active")) or 0),
    }


def best_pairs(pairs: list, now_ms: int, chain: str = "solana") -> dict:
    """token address -> view of its deepest-liquidity pair on `chain`."""
    best = {}
    for p in pairs:
        if p.get("chainId") != chain:
            continue
        v = pair_view(p, now_ms)
        if not v["token"] or v["price_usd"] is None or v["price_usd"] <= 0:
            continue
        cur = best.get(v["token"])
        if cur is None or (v["liq_usd"] or 0) > (cur["liq_usd"] or 0):
            best[v["token"]] = v
    return best


def pool_briefs(pairs: list, token: str, now_ms: int, chain: str = "solana", limit: int = 12) -> list:
    """Diagnostics only: the pools where `token` is the base token, deepest first."""
    out = []
    for p in pairs:
        if p.get("chainId") != chain:
            continue
        v = pair_view(p, now_ms)
        if v["token"] != token:
            continue
        out.append({
            "pair": v["pair"], "dex": v["dex"], "quote": v["quote_symbol"],
            "liq_usd": round(v["liq_usd"] or 0), "vol_h24": round(v["vol_h24"]),
            "txns_h24": v["buys_h24"] + v["sells_h24"], "price_usd": v["price_usd"],
            "age_days": round(v["age_days"], 2) if v["age_days"] is not None else None,
        })
    out.sort(key=lambda b: b["liq_usd"], reverse=True)
    return out[:limit]


def sol_usd_from(pairs: list):
    """SOL price implied by SOL-quoted pairs: priceUsd / priceNative (median)."""
    vals = []
    for p in pairs:
        q = p.get("quoteToken") or {}
        if q.get("address") != WSOL:
            continue
        usd, nat = num(p.get("priceUsd")), num(p.get("priceNative"))
        if usd and nat and usd > 0 and nat > 0:
            vals.append(usd / nat)
    return median(vals) if vals else None


def buy_sell_ratio(v: dict) -> float:
    return v["buys_h1"] / max(1, v["sells_h1"])


def volume_accel(v: dict) -> float:
    """Last hour's volume vs the average hour of the last six."""
    avg = v["vol_h6"] / 6.0
    return v["vol_h1"] / avg if avg > 0 else 0.0


def watch_reject(v: dict, r: dict):
    if v["liq_usd"] is None or v["liq_usd"] < r["min_liquidity_usd"]:
        return "watch_liquidity"
    if v["age_days"] is not None and v["age_days"] > r["max_age_days"]:
        return "watch_too_old"
    return None


def universe_reject(v: dict, r: dict):
    """Is this token the kind we trade at all? Returns a reason, or None if eligible."""
    if v["age_days"] is None:
        return "age_unknown"
    if v["age_days"] < r["min_age_days"]:
        return "too_young"
    if v["age_days"] > r["max_age_days"]:
        return "too_old"
    if v["quote_symbol"] not in r["allowed_quote_symbols"]:
        return "quote_token"
    if v["liq_usd"] is None or v["liq_usd"] < r["min_liquidity_usd"]:
        return "liquidity"
    if v["vol_h24"] < r["min_volume_h24_usd"]:
        return "volume_h24"
    if v["mcap"] is None:
        return "mcap_unknown"
    if v["mcap"] < r["min_market_cap_usd"]:
        return "mcap_small"
    if v["mcap"] > r["max_market_cap_usd"]:
        return "mcap_large"
    if v["buys_h24"] + v["sells_h24"] < r["min_txns_h24"]:
        return "txns_h24"
    if v["liq_usd"] / v["mcap"] < r["min_liq_to_mcap"]:
        return "liq_to_mcap"
    return None


def entry_reject(v: dict, r: dict, liq_drop_pct_1h):
    """Is now a moment to buy? Returns a reason, or None to enter."""
    if v["chg_h1"] < r["h1_change_min_pct"]:
        return "h1_weak"
    if v["chg_h1"] > r["h1_change_max_pct"]:
        return "h1_overheated"
    if v["chg_h6"] < r["h6_change_min_pct"]:
        return "h6_down"
    if v["chg_h24"] < r["h24_change_min_pct"]:
        return "h24_dumped"
    if v["chg_m5"] < r["m5_change_min_pct"]:
        return "m5_dropping"
    if v["buys_h1"] + v["sells_h1"] < r["min_txns_h1"]:
        return "txns_h1"
    if buy_sell_ratio(v) < r["min_buy_sell_ratio_h1"]:
        return "buy_pressure"
    if volume_accel(v) < r["min_volume_accel"]:
        return "volume_accel"
    if liq_drop_pct_1h is not None and liq_drop_pct_1h > r["max_liquidity_drop_pct_1h"]:
        return "liquidity_falling"
    return None


def entry_score(v: dict) -> float:
    return buy_sell_ratio(v) * volume_accel(v)


def features(v: dict) -> dict:
    """What we record at entry so reviews can ask 'which conditions paid?'."""
    return {
        "age_days": round(v["age_days"], 2) if v["age_days"] is not None else None,
        "liq_usd": round(v["liq_usd"] or 0),
        "mcap": round(v["mcap"] or 0),
        "vol_h24": round(v["vol_h24"]),
        "vol_h1": round(v["vol_h1"]),
        "chg_m5": v["chg_m5"], "chg_h1": v["chg_h1"],
        "chg_h6": v["chg_h6"], "chg_h24": v["chg_h24"],
        "buy_sell_ratio_h1": round(buy_sell_ratio(v), 2),
        "volume_accel": round(volume_accel(v), 2),
        "txns_h1": v["buys_h1"] + v["sells_h1"],
        "liq_to_mcap": round((v["liq_usd"] or 0) / v["mcap"], 4) if v["mcap"] else None,
        "boosts": v["boosts"],
        "dex": v["dex"],
        "quote": v["quote_symbol"],
        "score": round(entry_score(v), 2),
    }
