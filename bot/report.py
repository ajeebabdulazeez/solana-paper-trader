"""Performance stats for reviews.  python3 -m bot.report [--version N] [--last N]

Everything is measured in SOL after simulated costs.
"""
import argparse
from collections import defaultdict
from statistics import median

from . import store


def stats(trades: list, starting_sol: float = 5.0) -> dict:
    n = len(trades)
    if n == 0:
        return {"n": 0}
    wins = [t for t in trades if t["pnl_sol"] > 0]
    losses = [t for t in trades if t["pnl_sol"] <= 0]
    gross_win = sum(t["pnl_sol"] for t in wins)
    gross_loss = -sum(t["pnl_sol"] for t in losses)
    total = gross_win - gross_loss
    curve, peak, max_dd = starting_sol, starting_sol, 0.0
    for t in sorted(trades, key=lambda x: x["closed"]):
        curve += t["pnl_sol"]
        peak = max(peak, curve)
        max_dd = max(max_dd, (peak - curve) / peak * 100.0 if peak > 0 else 0.0)
    return {
        "n": n,
        "win_rate_pct": round(len(wins) / n * 100, 1),
        "avg_win_pct": round(sum(t["pnl_pct"] for t in wins) / len(wins), 2) if wins else 0.0,
        "avg_loss_pct": round(sum(t["pnl_pct"] for t in losses) / len(losses), 2) if losses else 0.0,
        "expectancy_pct": round(sum(t["pnl_pct"] for t in trades) / n, 2),
        "expectancy_sol": round(total / n, 5),
        "total_pnl_sol": round(total, 4),
        "profit_factor": round(gross_win / gross_loss, 2) if gross_loss > 0 else None,
        "max_drawdown_pct": round(max_dd, 2),
        "avg_hold_min": round(sum(t["hold_minutes"] for t in trades) / n, 1),
        "fees_sol": round(sum(t.get("fees_sol", 0) for t in trades), 4),
    }


def group(trades, keyfn) -> dict:
    g = defaultdict(list)
    for t in trades:
        g[keyfn(t)].append(t)
    return dict(g)


def feature_split(trades, feature):
    """Median split on one entry feature: does the high or low half pay better?"""
    vals = [(t["features"].get(feature), t) for t in trades]
    vals = [(v, t) for v, t in vals if isinstance(v, (int, float))]
    if len(vals) < 8:
        return None
    m = median(v for v, _ in vals)
    lo = [t for v, t in vals if v <= m]
    hi = [t for v, t in vals if v > m]
    if not lo or not hi:
        return None
    exp = lambda ts: round(sum(t["pnl_pct"] for t in ts) / len(ts), 2)  # noqa: E731
    return {"median": m, "low_n": len(lo), "low_exp_pct": exp(lo), "high_n": len(hi), "high_exp_pct": exp(hi)}


def _line(label, s):
    if s["n"] == 0:
        return f"| {label} | 0 | - | - | - | - | - | - |"
    pf = "-" if s["profit_factor"] is None else s["profit_factor"]
    return (f"| {label} | {s['n']} | {s['win_rate_pct']}% | {s['avg_win_pct']}% | {s['avg_loss_pct']}% "
            f"| {s['expectancy_pct']}% | {s['total_pnl_sol']} | {pf} |")


HEAD = ("| Group | Trades | Win rate | Avg win | Avg loss | Expectancy/trade | Total P&L (SOL) | Profit factor |\n"
        "|---|---|---|---|---|---|---|---|")


def build_status(state: dict, run_summary: dict, trades: list) -> str:
    """Short always-current page the bot rewrites every run (data/STATUS.md)."""
    start = state["starting_sol"]
    eq = run_summary["equity_sol"]
    s = stats(trades, start)
    out = [
        "# Paper trading status", "",
        f"Updated {run_summary['ts']} (UTC), rulebook v{run_summary['rulebook_version']}. "
        "**Simulated trades only. No real money.** Full trade ledger: [trades.csv](trades.csv).", "",
        f"- Equity: **{eq:.4f} SOL** (started with {start} SOL, {((eq / start) - 1) * 100:+.2f}%)",
        f"- Cash: {state['cash_sol']:.4f} SOL, open positions: {len(state['positions'])}, "
        f"closed trades: {state['closed_count']}",
        f"- Watchlist: {run_summary['watchlist']} tokens, entry signals this run: "
        f"{run_summary['funnel'].get('signal', 0)}", "",
    ]
    if s["n"]:
        out += ["## Closed trades", "", HEAD, _line("All", s), "",
                f"Max drawdown {s['max_drawdown_pct']}%, average hold {s['avg_hold_min']} min, "
                f"simulated fees {s['fees_sol']} SOL.", ""]
    if state["positions"]:
        out += ["## Open positions", "", "| # | Token | Opened | SOL in | Change vs entry | TP1 hit |",
                "|---|---|---|---|---|---|"]
        for p in state["positions"]:
            chg = (p["last_price_usd"] / p["entry_mid_usd"] - 1) * 100
            out.append(f"| {p['id']} | {p['symbol']} | {p['opened']} | {p['sol_in']:.3f} "
                       f"| {chg:+.1f}% | {'yes' if p['tp1_done'] else 'no'} |")
        out.append("")
    if trades:
        out += ["## Last 10 closed", "", "| # | Token | Closed | Exit | P&L % | P&L SOL |", "|---|---|---|---|---|---|"]
        for t in trades[-10:][::-1]:
            out.append(f"| {t['id']} | {t['symbol']} | {t['closed']} | {t['exit_reason']} "
                       f"| {t['pnl_pct']:+.2f}% | {t['pnl_sol']:+.4f} |")
        out.append("")
    if run_summary["errors"]:
        out += ["## Errors in the last run", ""] + [f"- {e}" for e in run_summary["errors"]] + [""]
    return "\n".join(out)


def review(trades: list, runs: list, starting_sol: float) -> str:
    out = ["# Review report", "", "## Overall and by rulebook version", "", HEAD, _line("All", stats(trades, starting_sol))]
    for ver, ts in sorted(group(trades, lambda t: t["rulebook_version"]).items()):
        out.append(_line(f"v{ver}", stats(ts, starting_sol)))
    out += ["", "## By exit reason", "", HEAD]
    for reason, ts in sorted(group(trades, lambda t: t["exit_reason"]).items()):
        out.append(_line(reason, stats(ts, starting_sol)))
    # Pool fees and depth differ by DEX and the cost model is flat, so keep these apart.
    out += ["", "## By DEX of the entry pool", "", HEAD]
    for dex, ts in sorted(group(trades, lambda t: str((t.get("features") or {}).get("dex"))).items()):
        out.append(_line(dex, stats(ts, starting_sol)))
    out += ["", "## Entry features (median split, expectancy % per trade)", "",
            "| Feature | Median | Low half (n) | High half (n) |", "|---|---|---|---|"]
    for f in ["age_days", "liq_usd", "mcap", "vol_h24", "chg_h1", "chg_h6", "chg_h24",
              "buy_sell_ratio_h1", "volume_accel", "txns_h1", "liq_to_mcap", "boosts", "score"]:
        fs = feature_split(trades, f)
        if fs:
            out.append(f"| {f} | {fs['median']} | {fs['low_exp_pct']}% ({fs['low_n']}) "
                       f"| {fs['high_exp_pct']}% ({fs['high_n']}) |")
    if trades:
        s = stats(trades, starting_sol)
        out += ["", f"Max drawdown {s['max_drawdown_pct']}%, avg hold {s['avg_hold_min']} min, "
                    f"fees {s['fees_sol']} SOL. Left on the table: average max gain "
                    f"{round(sum(t['max_gain_pct'] for t in trades) / len(trades), 2)}% vs realised "
                    f"{s['expectancy_pct']}%."]
    if runs:
        total = defaultdict(int)
        for r in runs:
            for k, v in r.get("funnel", {}).items():
                total[k] += v
        errs = sum(1 for r in runs if r.get("errors"))
        out += ["", f"## Funnel over the last {len(runs)} runs ({errs} runs had errors)", "",
                "| Stage | Count |", "|---|---|"]
        out += [f"| {k} | {v} |" for k, v in sorted(total.items(), key=lambda kv: -kv[1])]
        miss = sum(r.get("batch_miss", 0) for r in runs)
        out += ["", f"Batch misses: {miss}. Latest equity: {runs[-1]['equity_sol']} SOL."]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", type=int, help="only trades from this rulebook version")
    ap.add_argument("--last", type=int, help="only the last N closed trades")
    ap.add_argument("--runs", type=int, default=288, help="how many recent runs to summarise")
    a = ap.parse_args()
    dd = store.data_dir()
    trades = store.read_jsonl(dd / "journal" / "trades.jsonl")
    if a.version is not None:
        trades = [t for t in trades if t["rulebook_version"] == a.version]
    if a.last:
        trades = trades[-a.last:]
    runs = []
    for f in sorted((dd / "runs").glob("*.jsonl"))[-3:]:
        runs += store.read_jsonl(f)
    state = store.read_json(dd / "state" / "portfolio.json", {"starting_sol": 5.0})
    print(review(trades, runs[-a.runs:], state.get("starting_sol", 5.0)))


if __name__ == "__main__":
    main()
