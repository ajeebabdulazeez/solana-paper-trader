"""Trade ledger as a spreadsheet: data/trades.csv, rewritten every run.

One row per paper trade, newest first. Open positions are included with status OPEN
and their result so far. GitHub shows the file as a searchable table, and it opens
directly in Excel or Google Sheets.
"""
import csv

COLUMNS = [
    "trade_no", "status", "token", "opened_utc", "closed_utc", "hold_minutes",
    "sol_in", "usd_in", "buy_price_usd", "avg_sell_price_usd", "sol_out",
    "pnl_sol", "pnl_pct", "exit_reason", "took_partial_profit", "fees_sol",
    "max_gain_pct", "max_drawdown_pct", "rulebook_version", "token_address", "chart",
]


def _chart(pair):
    return f"https://dexscreener.com/solana/{pair}" if pair else ""


def _r(x, n):
    return "" if x is None else round(x, n)


def _px(x):
    """Token prices span many magnitudes: keep 6 significant figures."""
    return "" if x in (None, "") else float(f"{float(x):.6g}")


def closed_row(t: dict) -> dict:
    usd_in = t.get("usd_in")
    return {
        "trade_no": t["id"], "status": "CLOSED", "token": t["symbol"],
        "opened_utc": t["opened"], "closed_utc": t["closed"], "hold_minutes": t["hold_minutes"],
        "sol_in": t["sol_in"], "usd_in": _r(usd_in, 2),
        "buy_price_usd": _px(t["entry_exec_usd"]), "avg_sell_price_usd": _px(t.get("avg_sell_usd", "")),
        "sol_out": t["sol_out"], "pnl_sol": t["pnl_sol"], "pnl_pct": t["pnl_pct"],
        "exit_reason": t["exit_reason"], "took_partial_profit": "yes" if t.get("tp1_hit") else "no",
        "fees_sol": t.get("fees_sol", ""), "max_gain_pct": t["max_gain_pct"],
        "max_drawdown_pct": t["max_drawdown_pct"], "rulebook_version": t["rulebook_version"],
        "token_address": t["token"], "chart": _chart(t.get("pair")),
    }


def open_row(p: dict, sol_usd) -> dict:
    """Result so far: SOL already banked plus the remainder at the last seen price, before exit costs."""
    su = sol_usd or p.get("entry_sol_usd")
    marked = p["sol_returned"] + (p["tokens_remaining"] * p["last_price_usd"] / su if su else 0.0)
    pnl = marked - p["sol_in"]
    mid = p["entry_mid_usd"]
    sold = p.get("sold_tokens") or 0.0
    return {
        "trade_no": p["id"], "status": "OPEN", "token": p["symbol"],
        "opened_utc": p["opened"], "closed_utc": "", "hold_minutes": "",
        "sol_in": round(p["sol_in"], 6), "usd_in": _r(p["sol_in"] * p["entry_sol_usd"], 2),
        "buy_price_usd": _px(p["entry_exec_usd"]),
        "avg_sell_price_usd": _px(p.get("sold_usd", 0.0) / sold) if sold > 0 else "",
        "sol_out": round(p["sol_returned"], 6), "pnl_sol": round(pnl, 6),
        "pnl_pct": round(pnl / p["sol_in"] * 100, 2), "exit_reason": "",
        "took_partial_profit": "yes" if p["tp1_done"] else "no", "fees_sol": round(p["fees_sol"], 6),
        "max_gain_pct": round((p["peak_usd"] / mid - 1) * 100, 2),
        "max_drawdown_pct": round((p["trough_usd"] / mid - 1) * 100, 2),
        "rulebook_version": p["rulebook_version"], "token_address": p["token"], "chart": _chart(p.get("pair")),
    }


def write_csv(path, state: dict, trades: list, sol_usd) -> int:
    rows = [open_row(p, sol_usd) for p in state["positions"]] + [closed_row(t) for t in trades]
    rows.sort(key=lambda r: r["trade_no"], reverse=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    return len(rows)
