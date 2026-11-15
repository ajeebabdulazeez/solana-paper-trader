"""Replay the rulebook on recorded snapshots. A review aid: it reads data/, writes nothing.

    python3 -m bot.replay                        # the current rulebook on the bot's own universe
    python3 -m bot.replay --wide                 # entry and exit rules on every recorded token
    python3 -m bot.replay --no-cooldown --set entry.min_txns_h1=50
    python3 -m bot.replay --wide --set universe.min_age_days=3 --set universe.max_age_days=30
    python3 -m bot.replay --baseline             # a buy at every eligible cycle, against the entry rules' picks

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

`--baseline` asks a different question: do the entry rules pick better moments than no rule at all?
It opens a position at every cycle a token was inside the universe and runs each through the same
exits and costs. If the cycles the entry rules pass do no better than all cycles, the rules are
not adding anything on this record, whatever a handful of trades looked like.

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


def _eligible(v: dict, uni: dict, any_quote: bool) -> bool:
    """Could the rulebook trade this row at all (priced, and inside the universe)?"""
    if v["price_usd"] is None or not v["liq_usd"]:
        return False
    if v["quote_symbol"] is None and not any_quote:
        return False
    u = dict(uni, allowed_quote_symbols=[v["quote_symbol"]]) if any_quote else uni
    return S.universe_reject(v, u) is None


def _signal(v: dict, h: list, now_ts: float, entry: dict) -> bool:
    """Do the entry rules say buy? `h` is the token's recent (time, liquidity) history."""
    peak = max(l for ts, l in h if ts >= now_ts - 3900)
    return S.entry_reject(v, entry, (1 - v["liq_usd"] / peak) * 100) is None


def _open(v: dict, ts: str, now, size: float, sol: float, costs: dict):
    """A hypothetical position bought at this row, or None if nothing could be bought."""
    tokens, _, _ = P.buy_fill(size, v["price_usd"], v["liq_usd"], sol, costs)
    if tokens <= 0:
        return None
    return {"symbol": v["symbol"], "opened": ts, "mid": v["price_usd"],
            "entry_liq": v["liq_usd"], "sol_in": size, "left": tokens, "out": 0.0,
            "peak": v["price_usd"], "trough": v["price_usd"], "tp1": False,
            "last": v["price_usd"], "last_liq": v["liq_usd"], "last_ts": now,
            "last_vol_h24": v.get("vol_h24"), "suspect": None, "seen": now,
            "features": S.features(v)}


def _manage(p: dict, v: dict, now, sol: float, ex: dict, costs: dict):
    """Give one reading to one hypothetical position, as the bot would. Returns (exit reason,
    hours held); the reason is None while the position stays open. A closed position is sold."""
    price, liq = v["price_usd"], v["liq_usd"]
    p["seen"] = now
    p["suspect"] = S.hold_suspect(p["last"], p["last_liq"], p["suspect"], price, liq,
                                  S.traded_since(v, p["last_vol_h24"]),
                                  (now - p["last_ts"]).total_seconds())
    if p["suspect"]:
        return None, None
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
    return reason, held_h


def _record(t: str, p: dict, reason: str, now, held_h: float) -> dict:
    return {
        "token": t, "symbol": p["symbol"], "opened": p["opened"], "closed": now.strftime(FMT),
        "hold_minutes": round(held_h * 60, 1), "exit_reason": reason,
        "pnl_pct": round((p["out"] / p["sol_in"] - 1) * 100, 2),
        "max_gain_pct": round((p["peak"] / p["mid"] - 1) * 100, 2),
        "max_drawdown_pct": round((p["trough"] / p["mid"] - 1) * 100, 2), "features": p["features"]}


def replay(snaps: list, rules: dict, cooldown: bool = True) -> list:
    """Hypothetical trades, in the order they closed. Positions left at the end are marked at their
    last price: "open" if the token was still in the record, "lost" if it left it while held."""
    ex, costs, pf, uni = rules["exit"], rules["costs"], rules["portfolio"], rules["universe"]
    any_quote = uni.get("allowed_quote_symbols") is None
    pos, last_exit, hist, trades = {}, {}, {}, []

    def record(t, p, reason, now, held_h):
        trades.append(_record(t, p, reason, now, held_h))

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
            reason, held_h = _manage(p, v, now, sol, ex, costs)
            if reason:
                record(t, p, reason, now, held_h)
                del pos[t]
                last_exit[t] = now
        for t, v in views.items():                          # then entries
            h = [x for x in hist.get(t, []) if x[0] >= now_ts - 7200] + [(now_ts, v["liq_usd"])]
            hist[t] = h
            if t in pos or not _eligible(v, uni, any_quote):
                continue
            if cooldown and t in last_exit and \
                    (now - last_exit[t]).total_seconds() / 3600 < pf["token_cooldown_hours"]:
                continue
            if not _signal(v, h, now_ts, rules["entry"]):
                continue
            p = _open(v, d["ts"], now, pf["position_size_sol"], sol, costs)
            if p:
                pos[t] = p
    if snaps:
        end, sol = parse(snaps[-1]["ts"]), snaps[-1].get("sol_usd")
        for t, p in pos.items():
            if sol:
                p["out"] += P.sell_fill(p["left"], p["last"], p["last_liq"], sol, costs)[0]
            gone = (end - p["seen"]).total_seconds() > LOST_AFTER_MIN * 60
            record(t, p, "lost" if gone else "open", end, (end - parse(p["opened"])).total_seconds() / 3600)
    return trades


def baseline(snaps: list, rules: dict) -> list:
    """The yardstick for the entry rules: a full-size position opened at EVERY cycle a token passed
    the universe filters, whatever the entry rules said, and run through the same exits, costs and
    bad-print guard. No cooldown and no limit on positions. One dict per closed position, as in
    `replay`, plus `signal` (the entry rules said buy at that cycle) and `first` (they had not said
    so on the token's row before it, which is the cycle the bot would actually buy on). Positions
    still open or lost at the end of the record are left out.
    """
    ex, costs, pf, uni = rules["exit"], rules["costs"], rules["portfolio"], rules["universe"]
    any_quote = uni.get("allowed_quote_symbols") is None
    held, hist, was_signal, out = {}, {}, {}, []
    for d in snaps:
        sol = d.get("sol_usd")
        if not sol:
            continue
        now = parse(d["ts"])
        now_ts = now.timestamp()
        for row in d["rows"]:
            v = view(row)
            t = v["token"]
            still = []
            for p in held.get(t, []):                       # exits first, as the bot does
                reason, held_h = _manage(p, v, now, sol, ex, costs)
                if reason:
                    out.append(dict(_record(t, p, reason, now, held_h), signal=p["signal"], first=p["first"]))
                else:
                    still.append(p)
            held[t] = still
            h = [x for x in hist.get(t, []) if x[0] >= now_ts - 7200] + [(now_ts, v["liq_usd"])]
            hist[t] = h
            ok = _eligible(v, uni, any_quote)
            sig = ok and _signal(v, h, now_ts, rules["entry"])
            first, was_signal[t] = sig and not was_signal.get(t), sig
            if not ok:
                continue
            p = _open(v, d["ts"], now, pf["position_size_sol"], sol, costs)
            if p:
                p["signal"], p["first"] = sig, first
                still.append(p)
    return out


def baseline_report(rows: list) -> str:
    out = ["| Positions opened at | Cycles | Tokens | Win rate | Mean % | Median % |", "|---|---|---|---|---|---|"]
    for name, group in (("every cycle a token was eligible", rows),
                        ("cycles the entry rules passed", [r for r in rows if r["signal"]]),
                        ("the first passing cycle of each run", [r for r in rows if r["first"]])):
        pnl = [r["pnl_pct"] for r in group]
        if not pnl:
            out.append(f"| {name} | 0 | 0 | - | - | - |")
            continue
        out.append(f"| {name} | {len(pnl)} | {len({r['token'] for r in group})} "
                   f"| {sum(x > 0 for x in pnl) / len(pnl) * 100:.0f}% | {sum(pnl) / len(pnl):+.2f} | {median(pnl):+.2f} |")
    out += ["", "The first row is what the exits and the costs do to a buy made at any moment. The entry rules "
            "only earn their place if the rows under it are clearly better. Neighbouring cycles of one token "
            "end almost alike, so the cycle counts overstate the evidence: go by the number of tokens."]
    return "\n".join(out) + "\n"


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
    ap.add_argument("--baseline", action="store_true",
                    help="instead of trades: how a buy at every eligible cycle would have done, "
                         "against the cycles the entry rules pick")
    a = ap.parse_args()
    rules = store.read_json(store.root() / "rulebook.json", None)
    if a.wide:
        rules = wide_rules(rules)
    for item in a.set:                      # after --wide, so a universe number can be put back
        key, value = item.split("=", 1)
        section, name = key.split(".", 1)
        rules[section][name] = float(value)
    if a.baseline:
        print(baseline_report(baseline(load_snapshots(), rules)))
        return
    print(report(replay(load_snapshots(), rules, cooldown=not a.no_cooldown), a.split))


if __name__ == "__main__":
    main()
