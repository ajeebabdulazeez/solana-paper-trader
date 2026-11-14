"""Replay the rulebook on recorded snapshots. A review aid: it reads data/, writes nothing.

    python3 -m bot.replay                        # the current rulebook on the bot's own universe
    python3 -m bot.replay --wide                 # entry and exit rules on every recorded token
    python3 -m bot.replay --no-cooldown --set entry.min_txns_h1=50
    python3 -m bot.replay --wide --set universe.min_age_days=3 --set universe.max_age_days=30

It answers "what would these rules have done on the prices the bot recorded?", so a review can
look at more than the handful of trades the bot really took, and can keep measuring the entries
a rule now blocks. Treat the output as hints, never as proof:

- no RugCheck, no position cap, no daily cap, no cash limit; each token holds one position at a time
- only the snapshot rows exist (the 120 deepest watchlist tokens per cycle), and a held token is
  priced on whatever pool the row shows
- a token that leaves the snapshots while held cannot be priced. It is listed as "lost" and left
  out of the win rate. For a token a few hours old that usually means its pool was drained, so
  `--wide` flatters tokens under 3 days old: read it with an age filter
- rows from before 2026-11-13 18:40 UTC have no quote symbol and are skipped
- it is the same few days of one market, and every variant tried on it is fitted to it

With the rulebook that was live at the time, it reproduces the bot's real trades (v2: all six,
each within 0.1 points of the journal; the replay always buys the full position size).
"""
import argparse
import copy
from datetime import datetime, timezone
from statistics import median

from . import portfolio as P
from . import store
from . import strategy as S

FIELDS = ["token", "symbol", "price_usd", "liq_usd", "mcap", "vol_m5", "vol_h1", "vol_h6", "vol_h24",
          "buys_m5", "sells_m5", "buys_h1", "sells_h1", "buys_h24", "sells_h24",
          "chg_m5", "chg_h1", "chg_h6", "chg_h24", "age_days", "quote_symbol", "dex"]
FMT = "%Y-%m-%dT%H:%M:%SZ"
UNFINISHED = ("open", "lost")
LOST_AFTER_MIN = 30   # a held token with no snapshot row for this long has left the record


def parse(ts: str):
    return datetime.strptime(ts, FMT).replace(tzinfo=timezone.utc)


def view(row: list) -> dict:
    v = dict(zip(FIELDS, row))
    v.setdefault("quote_symbol", None)   # rows recorded before the field existed
    v.setdefault("dex", None)
    v["boosts"] = 0
    if not v.get("mcap"):
        v["mcap"] = None                 # a rounded-to-zero market cap is unknown, not zero
    return v


def load_snapshots(data_dir=None) -> list:
    snaps = []
    for f in sorted((data_dir or store.data_dir()).glob("snapshots/*/*.jsonl")):
        snaps += store.read_jsonl(f)
    snaps.sort(key=lambda d: d["ts"])
    return snaps


def wide_rules(rules: dict) -> dict:
    """The same entry and exit rules with the universe opened to every recorded token."""
    r = copy.deepcopy(rules)
    r["universe"].update(min_age_days=0, max_age_days=1e9, min_liquidity_usd=0, min_volume_h24_usd=0,
                         min_market_cap_usd=0, max_market_cap_usd=1e18, min_txns_h24=0,
                         min_liq_to_mcap=0, allowed_quote_symbols=None)
    return r


def replay(snaps: list, rules: dict, cooldown: bool = True) -> list:
    """Hypothetical trades, in the order they closed. Positions left at the end are marked at their
    last price: "open" if the token was still in the record, "lost" if it left it while held."""
    ex, costs, pf, uni = rules["exit"], rules["costs"], rules["portfolio"], rules["universe"]
    any_quote = uni.get("allowed_quote_symbols") is None
    pos, last_exit, hist, trades = {}, {}, {}, []

    def record(t, p, reason, now, held_h):
        trades.append({
            "token": t, "symbol": p["symbol"], "opened": p["opened"], "closed": now.strftime(FMT),
            "hold_minutes": round(held_h * 60, 1), "exit_reason": reason,
            "pnl_pct": round((p["out"] / p["sol_in"] - 1) * 100, 2),
            "max_gain_pct": round((p["peak"] / p["mid"] - 1) * 100, 2),
            "max_drawdown_pct": round((p["trough"] / p["mid"] - 1) * 100, 2), "features": p["features"]})

    for d in snaps:
        sol = d.get("sol_usd")
        if not sol:
            continue
        now = parse(d["ts"])
        now_ts = now.timestamp()
        views = {r[0]: view(r) for r in d["rows"]}
        for t, p in list(pos.items()):                      # exits first, as the bot does
            v = views.get(t)
            if v is None:
                continue
            price, liq = v["price_usd"], v["liq_usd"]
            p["seen"] = now
            p["suspect"] = S.hold_suspect(p["last"], p["last_liq"], p["suspect"], price, liq,
                                          S.traded_since(v, p["last_vol_h24"]),
                                          (now - p["last_ts"]).total_seconds())
            if p["suspect"]:
                continue
            p["last"], p["last_liq"], p["last_ts"], p["last_vol_h24"] = price, liq, now, v.get("vol_h24")
            p["peak"], p["trough"] = max(p["peak"], price), min(p["trough"], price)
            chg = (price / p["mid"] - 1) * 100
            held_h = (now - parse(p["opened"])).total_seconds() / 3600
            liq_drop = (1 - (liq or 0) / p["entry_liq"]) * 100 if p["entry_liq"] else 0
            reason = None
            if liq_drop >= ex["liquidity_drop_exit_pct"]:
                reason = "liquidity_drop"
            elif chg <= -ex["stop_loss_pct"]:
                reason = "stop_loss"
            elif p["tp1"] and price <= p["peak"] * (1 - ex["trailing_stop_pct"] / 100):
                reason = "trailing_stop"
            elif held_h >= ex["max_hold_hours"]:
                reason = "time_stop"
            elif not p["tp1"] and chg >= ex["take_profit_1_pct"]:
                qty = p["left"] * ex["take_profit_1_fraction"]
                p["out"] += P.sell_fill(qty, price, liq, sol, costs)[0]
                p["left"] -= qty
                p["tp1"] = True
            if reason:
                p["out"] += P.sell_fill(p["left"], price, liq, sol, costs)[0]
                record(t, p, reason, now, held_h)
                del pos[t]
                last_exit[t] = now
        for t, v in views.items():                          # then entries
            h = [x for x in hist.get(t, []) if x[0] >= now_ts - 7200] + [(now_ts, v["liq_usd"])]
            hist[t] = h
            if t in pos or v["price_usd"] is None or not v["liq_usd"]:
                continue
            if v["quote_symbol"] is None and not any_quote:
                continue
            u = dict(uni, allowed_quote_symbols=[v["quote_symbol"]]) if any_quote else uni
            if S.universe_reject(v, u):
                continue
            if cooldown and t in last_exit and \
                    (now - last_exit[t]).total_seconds() / 3600 < pf["token_cooldown_hours"]:
                continue
            peak = max(l for ts, l in h if ts >= now_ts - 3900)
            if S.entry_reject(v, rules["entry"], (1 - v["liq_usd"] / peak) * 100):
                continue
            size = pf["position_size_sol"]
            tokens, _, _ = P.buy_fill(size, v["price_usd"], v["liq_usd"], sol, costs)
            if tokens <= 0:
                continue
            pos[t] = {"symbol": v["symbol"], "opened": d["ts"], "mid": v["price_usd"],
                      "entry_liq": v["liq_usd"], "sol_in": size, "left": tokens, "out": 0.0,
                      "peak": v["price_usd"], "trough": v["price_usd"], "tp1": False,
                      "last": v["price_usd"], "last_liq": v["liq_usd"], "last_ts": now,
                      "last_vol_h24": v.get("vol_h24"), "suspect": None, "seen": now,
                      "features": S.features(v)}
    if snaps:
        end, sol = parse(snaps[-1]["ts"]), snaps[-1].get("sol_usd")
        for t, p in pos.items():
            if sol:
                p["out"] += P.sell_fill(p["left"], p["last"], p["last_liq"], sol, costs)[0]
            gone = (end - p["seen"]).total_seconds() > LOST_AFTER_MIN * 60
            record(t, p, "lost" if gone else "open", end, (end - parse(p["opened"])).total_seconds() / 3600)
    return trades


def _summary(trades: list) -> str:
    done = [t for t in trades if t["exit_reason"] not in UNFINISHED]
    rest = (f"{sum(t['exit_reason'] == 'open' for t in trades)} still open, "
            f"{sum(t['exit_reason'] == 'lost' for t in trades)} lost from the record (not counted)")
    if not done:
        return "0 closed, " + rest
    wins = sum(1 for t in done if t["pnl_pct"] > 0)
    pnl = [t["pnl_pct"] for t in done]
    return (f"{len(done)} closed on {len({t['token'] for t in done})} tokens, {wins} wins "
            f"({wins / len(done) * 100:.0f}%), expectancy {sum(pnl) / len(pnl):+.2f}%, "
            f"median {median(pnl):+.2f}%, " + rest)


def report(trades: list, split: str = "txns_h1") -> str:
    out = ["| Token | Opened | Held min | Exit | P&L % | Best % | Worst % | Age d | Liq $k | 1h % "
           "| Buy/sell | Vol accel | Trades 1h | DEX |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for t in sorted(trades, key=lambda t: t["opened"]):
        f = t["features"]
        out.append(f"| {t['symbol']} | {t['opened'][5:16]} | {t['hold_minutes']:.0f} | {t['exit_reason']} "
                   f"| {t['pnl_pct']:+.2f} | {t['max_gain_pct']:+.1f} | {t['max_drawdown_pct']:+.1f} "
                   f"| {f['age_days']} | {f['liq_usd'] / 1000:.0f} | {f['chg_h1']:+.1f} "
                   f"| {f['buy_sell_ratio_h1']} | {f['volume_accel']} | {f['txns_h1']} | {f['dex'] or '?'} |")
    out += ["", "All: " + _summary(trades)]
    done = [t for t in trades if t["exit_reason"] not in UNFINISHED and
            isinstance(t["features"].get(split), (int, float))]
    if len(done) >= 4:
        m = median(t["features"][split] for t in done)
        lo = [t for t in done if t["features"][split] <= m]
        hi = [t for t in done if t["features"][split] > m]
        out += [f"{split} at or under {m}: " + _summary(lo), f"{split} over {m}: " + _summary(hi)]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Replay the rulebook on recorded snapshots (hints only).")
    ap.add_argument("--wide", action="store_true", help="open the universe to every recorded token")
    ap.add_argument("--no-cooldown", action="store_true", help="let a token be re-entered straight away")
    ap.add_argument("--set", action="append", default=[], metavar="SECTION.KEY=VALUE",
                    help="override one rulebook number for this replay, e.g. entry.min_txns_h1=50")
    ap.add_argument("--split", default="txns_h1", help="entry feature for the median split")
    a = ap.parse_args()
    rules = store.read_json(store.root() / "rulebook.json", None)
    if a.wide:
        rules = wide_rules(rules)
    for item in a.set:                      # after --wide, so a universe number can be put back
        key, value = item.split("=", 1)
        section, name = key.split(".", 1)
        rules[section][name] = float(value)
    print(report(replay(load_snapshots(), rules, cooldown=not a.no_cooldown), a.split))


if __name__ == "__main__":
    main()
