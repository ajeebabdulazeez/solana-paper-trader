"""One bot cycle: discover -> fetch -> manage open paper positions -> open new ones -> record.

Run with:  python3 -m bot.run
The bot only ever executes rulebook.json. It never edits the rules; reviews do.
"""
import sys
from collections import Counter
from datetime import datetime, timezone

from . import portfolio as P
from . import store
from . import strategy as S
from . import geckoterminal as GT
from .dexscreener import DexScreener
from .ledger import write_csv
from .report import build_status
from .rugcheck import RugCheck, assess, compact

CHAIN = "solana"
FMT = "%Y-%m-%dT%H:%M:%SZ"


def iso(dt) -> str:
    return dt.strftime(FMT)


def parse_iso(s: str):
    return datetime.strptime(s, FMT).replace(tzinfo=timezone.utc)


def hours_since(now, stamp) -> float:
    return (now - parse_iso(stamp)).total_seconds() / 3600.0


def discover(dex, d, errors, gecko=None, meta=None, now=None):
    """Collect Solana token addresses from DexScreener's feeds and GeckoTerminal's pool lists."""
    found, pairs, gecko_sample = {}, [], None
    feeds = [
        ("boosts_top", dex.boosts_top), ("boosts_latest", dex.boosts_latest),
        ("profiles_latest", dex.profiles_latest), ("takeovers_latest", dex.takeovers_latest),
    ]
    for name, fn in feeds:
        if not d.get(name):
            continue
        try:
            for item in fn():
                if item.get("chainId") == CHAIN and item.get("tokenAddress"):
                    found.setdefault(item["tokenAddress"], name)
        except Exception as e:  # one feed failing must not stop the run
            errors.append(f"{name}: {e}")

    def take(pair_list, source):
        for p in pair_list:
            addr = (p.get("baseToken") or {}).get("address")
            if p.get("chainId") == CHAIN and addr:
                pairs.append(p)
                found.setdefault(addr, source)

    if d.get("trending_metas"):
        try:
            metas = dex.metas_trending()[: d.get("max_metas", 6)]
        except Exception as e:
            errors.append(f"metas_trending: {e}")
            metas = []
        for m in metas:
            slug = m.get("slug")
            if not slug:
                continue
            try:
                take(dex.meta_pairs(slug), "meta:" + str(slug)[:30])
            except Exception as e:
                errors.append(f"meta {slug}: {e}")
    for q in d.get("search_queries", []):
        try:
            take(dex.search(q), "search:" + q[:30])
        except Exception as e:
            errors.append(f"search {q}: {e}")

    g = d.get("geckoterminal") or {}
    if g.get("enabled") and gecko is not None and meta is not None:
        last = meta.get("gecko_last")
        if not last or hours_since(now, last) * 60 >= g.get("every_minutes", 20):
            meta["gecko_last"] = iso(now)
            jobs = [("trending", p) for p in range(1, g.get("trending_pages", 0) + 1)]
            jobs += [("h24_volume_usd_desc", p) for p in range(1, g.get("top_volume_pages", 0) + 1)]
            jobs += [("h24_tx_count_desc", p) for p in range(1, g.get("top_tx_pages", 0) + 1)]
            pools = []
            for kind, page in jobs:
                try:
                    pools += gecko.trending(page) if kind == "trending" else gecko.top(kind, page)
                except Exception as e:
                    errors.append(f"gecko {kind} p{page}: {e}")
                    break  # do not hammer a failing API
            gecko_sample = pools[0] if pools else None
            for t in GT.pick_tokens(pools, now, g["min_reserve_usd"], g["max_age_days"]):
                found.setdefault(t, "gecko")
    return found, pairs, gecko_sample


def fetch_views(dex, tokens, must_have, d, now_ms, errors):
    """Current market view per token. Returns (views, raw_pairs, batch_misses, confirmed_absent)."""
    raw, answered = [], set()
    size = max(1, int(d.get("batch_size", 30)))
    for i in range(0, len(tokens), size):
        chunk = tokens[i:i + size]
        try:
            raw += dex.pairs_for_tokens(CHAIN, chunk)
            answered.update(chunk)
        except Exception as e:
            errors.append(f"pairs batch {i // size}: {e}")
    views = S.best_pairs(raw, now_ms, CHAIN)
    missing = [t for t in tokens if t in answered and t not in views]
    urgent = [t for t in missing if t in must_have]
    others = [t for t in missing if t not in must_have][: int(d.get("max_single_lookups", 15))]
    looked_up = set()
    for t in urgent + others:
        try:
            ps = dex.pairs_for_token(CHAIN, t)
            looked_up.add(t)
            raw += ps
            one = S.best_pairs(ps, now_ms, CHAIN)
            if t in one:
                views[t] = one[t]
        except Exception as e:
            errors.append(f"pair lookup {t[:8]}: {e}")
    # "Absent" only counts when the API answered and still had nothing: an outage is not a rug.
    absent = {t for t in must_have if t in looked_up and t not in views}
    return views, raw, len(missing), absent


def snapshot_row(v):
    r = lambda x, n=0: None if x is None else round(x, n)  # noqa: E731
    return [
        v["token"], v["symbol"], v["price_usd"], r(v["liq_usd"]), r(v["mcap"]),
        r(v["vol_m5"]), r(v["vol_h1"]), r(v["vol_h6"]), r(v["vol_h24"]),
        v["buys_m5"], v["sells_m5"], v["buys_h1"], v["sells_h1"], v["buys_h24"], v["sells_h24"],
        v["chg_m5"], v["chg_h1"], v["chg_h6"], v["chg_h24"], r(v["age_days"], 2),
    ]


def run(now=None, dex=None, rug=None, gecko=None) -> dict:
    now = now or datetime.now(timezone.utc)
    now_iso, now_ts, now_ms = iso(now), now.timestamp(), int(now.timestamp() * 1000)
    rules = store.read_json(store.root() / "rulebook.json", None)
    if rules is None:
        raise SystemExit("rulebook.json not found")
    pf, ex, costs, safety = rules["portfolio"], rules["exit"], rules["costs"], rules["safety"]

    dd = store.data_dir()
    sdir = dd / "state"
    state = store.read_json(sdir / "portfolio.json", None) or P.new_state(pf["starting_sol"])
    watch = store.read_json(sdir / "watchlist.json", {})
    liq_hist = store.read_json(sdir / "liq_history.json", {})
    rug_cache = store.read_json(sdir / "rugcheck_cache.json", {})
    meta = store.read_json(sdir / "meta.json", {})
    dex = dex or DexScreener()
    rug = rug or RugCheck()
    gecko = gecko or GT.GeckoTerminal()
    errors, funnel, opened, closed = [], Counter(), [], []

    # 1. Discover new tokens for the watchlist.
    found, meta_pairs, gecko_sample = discover(dex, rules["discovery"], errors, gecko, meta, now)
    for t, src in found.items():
        if t != S.WSOL and t not in watch:
            watch[t] = {"first_seen": now_iso, "source": src, "last_ok": None, "low_since": None}
            funnel["discovered_new"] += 1
            if src == "gecko":
                funnel["discovered_gecko"] += 1
    if gecko_sample and not (dd / "debug" / "gecko_sample.json").exists():
        store.write_json(dd / "debug" / "gecko_sample.json", gecko_sample)

    # 2. Fetch current data for held tokens and the watchlist.
    held = {p["token"] for p in state["positions"]}
    tokens = sorted(held) + [t for t in watch if t not in held]
    views, raw, batch_miss, absent = fetch_views(dex, tokens, held, rules["discovery"], now_ms, errors)
    raw += meta_pairs
    sol_usd = S.sol_usd_from(raw)
    if sol_usd is None:
        try:
            one = S.best_pairs(dex.pairs_for_token(CHAIN, S.WSOL), now_ms, CHAIN)
            sol_usd = one[S.WSOL]["price_usd"] if S.WSOL in one else None
        except Exception as e:
            errors.append(f"sol price: {e}")
    if sol_usd is None:
        errors.append("no SOL price this run: holding, no trades")
    else:
        state["last_sol_usd"] = sol_usd
    trading = sol_usd is not None

    # 3. Manage open paper positions (exits before entries, always).
    for pos in list(state["positions"]):
        v = views.get(pos["token"])
        if v is None:
            if pos["token"] in absent:
                pos["missing_runs"] += 1
                if pos["missing_runs"] >= ex["missing_data_runs_to_write_off"]:
                    pos["tokens_remaining"] = 0.0  # unsellable: total loss on the remainder
                    rec = P.close_record(state, pos, "no_data", now_iso, 0.0,
                                         hours_since(now, pos["opened"]) * 60)
                    store.append_jsonl(dd / "journal" / "trades.jsonl", rec)
                    closed.append(rec)
            continue
        pos["missing_runs"] = 0
        if not trading:
            continue
        price, liq = v["price_usd"], v["liq_usd"]
        pos["last_price_usd"] = price
        pos["peak_usd"] = max(pos["peak_usd"], price)
        pos["trough_usd"] = min(pos["trough_usd"], price)
        chg = (price / pos["entry_mid_usd"] - 1.0) * 100.0
        held_h = hours_since(now, pos["opened"])
        entry_liq = pos.get("entry_liq_usd") or 0.0
        liq_drop = (1.0 - (liq or 0.0) / entry_liq) * 100.0 if entry_liq > 0 else 0.0

        reason = None
        if liq_drop >= ex["liquidity_drop_exit_pct"]:
            reason = "liquidity_drop"
        elif chg <= -ex["stop_loss_pct"]:
            reason = "stop_loss"
        elif pos["tp1_done"] and price <= pos["peak_usd"] * (1.0 - ex["trailing_stop_pct"] / 100.0):
            reason = "trailing_stop"
        elif held_h >= ex["max_hold_hours"]:
            reason = "time_stop"
        elif not pos["tp1_done"] and chg >= ex["take_profit_1_pct"]:
            got = P.sell(state, pos, ex["take_profit_1_fraction"], price, liq, sol_usd, costs)
            pos["tp1_done"] = True
            store.append_jsonl(dd / "journal" / "events.jsonl", {
                "ts": now_iso, "event": "tp1", "id": pos["id"], "symbol": pos["symbol"],
                "price_usd": price, "chg_pct": round(chg, 2), "sol_received": round(got, 6)})
            if pos["tokens_remaining"] <= 1e-12:
                reason = "take_profit"
        if reason:
            if pos["tokens_remaining"] > 1e-12:
                P.sell(state, pos, 1.0, price, liq, sol_usd, costs)
            rec = P.close_record(state, pos, reason, now_iso, price, held_h * 60)
            store.append_jsonl(dd / "journal" / "trades.jsonl", rec)
            store.append_jsonl(dd / "journal" / "events.jsonl", {
                "ts": now_iso, "event": "close", "id": rec["id"], "symbol": rec["symbol"],
                "reason": reason, "pnl_sol": rec["pnl_sol"], "pnl_pct": rec["pnl_pct"]})
            closed.append(rec)

    # 4. Day rollover (UTC) and equity.
    held = {p["token"] for p in state["positions"]}
    eq = P.equity(state, sol_usd)
    today = now.strftime("%Y-%m-%d")
    if state["day"].get("date") != today:
        state["day"] = {"date": today, "start_equity": eq, "opens": 0}

    # 5. Screen the watchlist.
    wl, candidates, snap = rules["watchlist"], [], []
    for t in list(watch):
        w, v = watch[t], views.get(t)
        if v is None:
            funnel["no_data"] += 1
            continue
        w["last_ok"], w["symbol"], w["liq"] = now_iso, v["symbol"], round(v["liq_usd"] or 0)
        wr = S.watch_reject(v, wl)
        if wr:
            w["low_since"] = w.get("low_since") or now_iso
            w["too_old"] = wr == "watch_too_old"
            funnel[wr] += 1
            continue
        w["low_since"] = None
        snap.append(v)
        hist = liq_hist.setdefault(t, [])
        hist.append([round(now_ts), round(v["liq_usd"])])
        ur = S.universe_reject(v, rules["universe"])
        if ur:
            funnel["u:" + ur + (":" + v["quote_symbol"][:10] if ur == "quote_token" else "")] += 1
            continue
        funnel["universe_ok"] += 1
        if t in held:
            funnel["already_held"] += 1
            continue
        last_exit = state["last_exit"].get(t)
        if last_exit and hours_since(now, last_exit) < pf["token_cooldown_hours"]:
            funnel["cooldown"] += 1
            continue
        recent = [l for ts, l in hist if ts >= now_ts - 3900]
        peak = max(recent) if recent else None
        drop_1h = (1.0 - v["liq_usd"] / peak) * 100.0 if peak else None
        er = S.entry_reject(v, rules["entry"], drop_1h)
        if er:
            funnel["e:" + er] += 1
            continue
        funnel["signal"] += 1
        candidates.append(v)

    # 6. Open new paper positions, best score first, behind the safety check.
    day_chg = (eq / state["day"]["start_equity"] - 1.0) * 100.0 if state["day"]["start_equity"] else 0.0
    loss_locked = day_chg <= -pf["daily_loss_limit_pct"]
    checks = 0
    candidates.sort(key=S.entry_score, reverse=True)
    for v in candidates:
        t = v["token"]
        if not trading:
            funnel["skip:no_sol_price"] += 1
            continue
        if loss_locked:
            funnel["skip:daily_loss_limit"] += 1
            continue
        if len(state["positions"]) >= pf["max_open_positions"]:
            funnel["skip:max_positions"] += 1
            continue
        if state["day"]["opens"] >= pf["max_new_trades_per_day"]:
            funnel["skip:daily_trade_cap"] += 1
            continue
        size = min(pf["position_size_sol"], eq * pf["max_position_pct_equity"] / 100.0, state["cash_sol"])
        if size < 0.05:
            funnel["skip:no_cash"] += 1
            continue
        rugc = None
        if safety.get("use_rugcheck"):
            cached = rug_cache.get(t)
            if cached and hours_since(now, cached["ts"]) < safety["cache_hours"]:
                rugc = cached["c"]
            else:
                if checks >= safety["max_checks_per_run"]:
                    funnel["skip:rugcheck_budget"] += 1
                    continue
                checks += 1
                try:
                    raw_sum = rug.summary(t)
                    rugc = compact(raw_sum)
                    rug_cache[t] = {"ts": now_iso, "c": rugc}
                    sample = dd / "debug" / "rugcheck_sample.json"
                    if not sample.exists():
                        store.write_json(sample, raw_sum)
                except Exception as e:
                    errors.append(f"rugcheck {t[:8]}: {e}")
                    funnel["safety:rugcheck_error"] += 1
                    if safety.get("on_error", "skip") == "skip":
                        continue
            if rugc is not None:
                ok, why = assess(rugc, safety)
                if not ok:
                    funnel["safety:" + why.split(":")[0]] += 1
                    continue
        pos = P.open_position(state, v, size, sol_usd, costs, now_iso, rules["version"], S.features(v), rugc)
        if pos is None:
            funnel["skip:no_fill"] += 1
            continue
        opened.append(pos["symbol"])
        store.append_jsonl(dd / "journal" / "events.jsonl", {
            "ts": now_iso, "event": "open", "id": pos["id"], "symbol": pos["symbol"], "token": t,
            "sol_in": round(size, 6), "price_usd": v["price_usd"], "score": pos["features"]["score"]})

    # 7. Housekeeping: prune watchlist, histories and caches.
    held = {p["token"] for p in state["positions"]}
    for t in list(watch):
        w = watch[t]
        seen = w.get("last_ok") or w["first_seen"]
        low = w.get("low_since")
        if t in held:
            continue
        if (hours_since(now, seen) > wl["drop_after_hours_unseen"] or w.get("too_old")
                or (low and hours_since(now, low) > 6)):
            del watch[t]
    cap = rules["discovery"]["max_watchlist"]
    if len(watch) > cap:
        # Drop currently-rejected tokens first, then the thinnest-liquidity ones. Never a held token.
        order = sorted((t for t in watch if t not in held),
                       key=lambda t: (watch[t].get("low_since") is None, watch[t].get("liq") or 0))
        drop = order[: len(watch) - cap]
        for t in drop:
            del watch[t]
    for t in list(liq_hist):
        liq_hist[t] = [x for x in liq_hist[t] if x[0] >= now_ts - 7200]
        if t not in watch or not liq_hist[t]:
            del liq_hist[t]
    for t in list(rug_cache):
        if hours_since(now, rug_cache[t]["ts"]) > 48:
            del rug_cache[t]

    # 8. Record everything.
    snap.sort(key=lambda v: v["liq_usd"] or 0, reverse=True)
    rows = snap[: wl["max_snapshot_rows"]]
    in_rows = {v["token"] for v in rows}
    rows += [views[t] for t in held if t in views and t not in in_rows]
    store.append_jsonl(dd / "snapshots" / today / f"{now.strftime('%H')}.jsonl",
                       {"ts": now_iso, "sol_usd": sol_usd, "rows": [snapshot_row(v) for v in rows]})
    eq = P.equity(state, sol_usd)
    summary = {
        "ts": now_iso, "rulebook_version": rules["version"], "sol_usd": sol_usd,
        "equity_sol": round(eq, 6), "cash_sol": round(state["cash_sol"], 6),
        "open": len(state["positions"]), "closed_total": state["closed_count"],
        "watchlist": len(watch), "with_data": len(views), "batch_miss": batch_miss,
        "api_calls": getattr(dex, "calls", None), "rugcheck_calls": getattr(rug, "calls", None),
        "gecko_calls": getattr(gecko, "calls", None),
        "funnel": dict(sorted(funnel.items())), "opened": opened,
        "closed": [[c["symbol"], c["exit_reason"], c["pnl_pct"]] for c in closed],
        "errors": [e[:160] for e in errors[:10]],
    }
    store.append_jsonl(dd / "runs" / f"{today}.jsonl", summary)
    if raw and not (dd / "debug" / "pair_sample.json").exists():
        store.write_json(dd / "debug" / "pair_sample.json", raw[0])
    store.write_json(sdir / "portfolio.json", state)
    store.write_json(sdir / "watchlist.json", watch)
    store.write_json(sdir / "liq_history.json", liq_hist, indent=None)
    store.write_json(sdir / "rugcheck_cache.json", rug_cache)
    store.write_json(sdir / "meta.json", meta)
    all_trades = store.read_jsonl(dd / "journal" / "trades.jsonl")
    write_csv(dd / "trades.csv", state, all_trades, sol_usd)
    (dd / "STATUS.md").write_text(build_status(state, summary, all_trades), encoding="utf-8")
    return summary


def main():
    s = run()
    print(f"{s['ts']} v{s['rulebook_version']} equity={s['equity_sol']} SOL open={s['open']} "
          f"watch={s['watchlist']} signals={s['funnel'].get('signal', 0)} "
          f"opened={s['opened']} closed={s['closed']} errors={len(s['errors'])}")
    for e in s["errors"]:
        print("  !", e, file=sys.stderr)


if __name__ == "__main__":
    main()
