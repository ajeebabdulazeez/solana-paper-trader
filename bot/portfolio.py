"""Paper portfolio: simulated fills with fees, slippage and price impact.

Fill model (deliberately pessimistic):
- swap fee and a fixed network fee are charged on every buy and sell
- base slippage moves the price against us on every fill
- price impact assumes a constant-product pool with half the reported
  liquidity on each side, so thin pools punish size and a drained pool
  returns almost nothing
- exits fill at the price observed when the bot runs, not at the stop level,
  so gaps between runs are paid for in full
"""


def buy_fill(sol_amount, price_usd, liq_usd, sol_usd, costs):
    """Spend `sol_amount` SOL in total. Returns (tokens, exec_price_usd, fee_sol)."""
    fee = sol_amount * costs["swap_fee_pct"] / 100.0 + costs["fixed_fee_sol"]
    net_sol = max(0.0, sol_amount - fee)
    usd_in = net_sol * sol_usd
    side = (liq_usd or 0.0) / 2.0
    if side <= 0 or price_usd <= 0:
        return 0.0, None, fee
    impact = usd_in / side if costs.get("price_impact", True) else 0.0
    exec_price = price_usd * (1.0 + impact) * (1.0 + costs["base_slippage_pct"] / 100.0)
    return usd_in / exec_price, exec_price, fee


def sell_fill(tokens, price_usd, liq_usd, sol_usd, costs):
    """Sell `tokens`. Returns (sol_received_net, exec_price_usd, fee_sol)."""
    side = (liq_usd or 0.0) / 2.0
    if tokens <= 0 or not price_usd or price_usd <= 0 or side <= 0 or not sol_usd:
        return 0.0, 0.0, 0.0
    value = tokens * price_usd
    out_usd = value / (1.0 + value / side) if costs.get("price_impact", True) else value
    out_usd *= 1.0 - costs["base_slippage_pct"] / 100.0
    gross_sol = out_usd / sol_usd
    fee = gross_sol * costs["swap_fee_pct"] / 100.0 + costs["fixed_fee_sol"]
    net = max(0.0, gross_sol - fee)
    return net, out_usd / tokens, min(fee, gross_sol)


def new_state(starting_sol: float) -> dict:
    return {
        "cash_sol": starting_sol,
        "starting_sol": starting_sol,
        "positions": [],
        "trade_seq": 0,
        "closed_count": 0,
        "realized_pnl_sol": 0.0,
        "last_exit": {},
        "day": {"date": None, "start_equity": starting_sol, "opens": 0},
    }


def equity(state: dict, sol_usd) -> float:
    """Cash plus open positions marked at the last seen mid price (before exit costs)."""
    total = state["cash_sol"]
    for p in state["positions"]:
        px = p.get("last_price_usd") or 0.0
        su = sol_usd or p.get("entry_sol_usd")
        if su:
            total += p["tokens_remaining"] * px / su
    return total


def open_position(state, v, sol_amount, sol_usd, costs, now_iso, rulebook_version, feats, rug):
    tokens, exec_price, fee = buy_fill(sol_amount, v["price_usd"], v["liq_usd"], sol_usd, costs)
    if tokens <= 0:
        return None
    state["trade_seq"] += 1
    state["cash_sol"] -= sol_amount
    state["day"]["opens"] += 1
    pos = {
        "id": state["trade_seq"],
        "token": v["token"], "symbol": v["symbol"], "pair": v["pair"],
        "opened": now_iso,
        "rulebook_version": rulebook_version,
        "sol_in": sol_amount,
        "tokens": tokens, "tokens_remaining": tokens,
        "entry_mid_usd": v["price_usd"], "entry_exec_usd": exec_price,
        "entry_liq_usd": v["liq_usd"], "entry_sol_usd": sol_usd,
        "last_price_usd": v["price_usd"], "last_liq_usd": v["liq_usd"],
        "peak_usd": v["price_usd"], "trough_usd": v["price_usd"],
        "tp1_done": False,
        "sol_returned": 0.0, "fees_sol": fee,
        "missing_runs": 0,
        "features": feats, "rugcheck": rug,
    }
    state["positions"].append(pos)
    return pos


def sell(state, pos, fraction, price_usd, liq_usd, sol_usd, costs):
    """Sell `fraction` of what remains. Returns SOL received."""
    qty = pos["tokens_remaining"] * fraction
    net, exec_price, fee = sell_fill(qty, price_usd, liq_usd, sol_usd, costs)
    pos["sold_tokens"] = pos.get("sold_tokens", 0.0) + qty
    pos["sold_usd"] = pos.get("sold_usd", 0.0) + qty * exec_price
    pos["tokens_remaining"] -= qty
    pos["sol_returned"] += net
    pos["fees_sol"] += fee
    state["cash_sol"] += net
    return net


def close_record(state, pos, reason, now_iso, exit_price_usd, hold_minutes):
    """Remove a fully sold position and build its journal record."""
    state["positions"] = [p for p in state["positions"] if p["id"] != pos["id"]]
    pnl = pos["sol_returned"] - pos["sol_in"]
    state["realized_pnl_sol"] += pnl
    state["closed_count"] += 1
    state["last_exit"][pos["token"]] = now_iso
    mid = pos["entry_mid_usd"]
    return {
        "id": pos["id"], "token": pos["token"], "symbol": pos["symbol"], "pair": pos["pair"],
        "rulebook_version": pos["rulebook_version"],
        "opened": pos["opened"], "closed": now_iso, "hold_minutes": round(hold_minutes, 1),
        "exit_reason": reason, "tp1_hit": pos["tp1_done"],
        "sol_in": round(pos["sol_in"], 6), "sol_out": round(pos["sol_returned"], 6),
        "usd_in": round(pos["sol_in"] * pos["entry_sol_usd"], 2),
        "avg_sell_usd": (pos["sold_usd"] / pos["sold_tokens"]) if pos.get("sold_tokens") else 0.0,
        "pnl_sol": round(pnl, 6), "pnl_pct": round(pnl / pos["sol_in"] * 100.0, 2),
        "fees_sol": round(pos["fees_sol"], 6),
        "entry_mid_usd": mid, "entry_exec_usd": pos["entry_exec_usd"],
        "exit_mid_usd": exit_price_usd,
        "max_gain_pct": round((pos["peak_usd"] / mid - 1) * 100, 2),
        "max_drawdown_pct": round((pos["trough_usd"] / mid - 1) * 100, 2),
        "entry_liq_usd": pos["entry_liq_usd"],
        "features": pos["features"], "rugcheck": pos["rugcheck"],
    }
