"""Offline tests: no network. A scripted fake market drives full bot cycles.

Run:  python3 -m unittest discover -s tests -v
"""
import json
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bot import portfolio as P
from bot import store
from bot import strategy as S
from bot.report import review, stats
from bot.rugcheck import assess, compact
from bot.run import run

REPO = Path(__file__).resolve().parent.parent
RULES = json.loads((REPO / "rulebook.json").read_text())
COSTS = RULES["costs"]
T0 = datetime(2026, 11, 14, 12, 0, 0, tzinfo=timezone.utc)
SOL_USD = 200.0


def make_pair(token, symbol, price, liq, now, age_days=7, mcap=2_000_000, vol_h24=500_000, vol_h6=120_000,
              vol_h1=40_000, buys_h1=120, sells_h1=60, chg=(0.5, 8.0, 12.0, 20.0), quote="SOL"):
    created = int((now - timedelta(days=age_days)).timestamp() * 1000)
    qaddr = S.WSOL if quote == "SOL" else "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    return {
        "chainId": "solana", "dexId": "raydium", "pairAddress": "PAIR" + token,
        "baseToken": {"address": token, "name": symbol, "symbol": symbol},
        "quoteToken": {"address": qaddr, "name": quote, "symbol": quote},
        "priceUsd": str(price), "priceNative": str(price / SOL_USD if quote == "SOL" else price),
        "txns": {"m5": {"buys": 10, "sells": 6}, "h1": {"buys": buys_h1, "sells": sells_h1},
                 "h24": {"buys": 3000, "sells": 2500}},
        "volume": {"m5": 3000, "h1": vol_h1, "h6": vol_h6, "h24": vol_h24},
        "priceChange": {"m5": chg[0], "h1": chg[1], "h6": chg[2], "h24": chg[3]},
        "liquidity": {"usd": liq, "base": 1, "quote": 1},
        "fdv": mcap, "marketCap": mcap, "pairCreatedAt": created, "boosts": {"active": 0},
    }


class FakeDex:
    """`market` maps token -> pair dict (or None for 'API has nothing')."""

    def __init__(self):
        self.market, self.feed, self.calls, self.fail = {}, [], 0, False

    def boosts_top(self):
        return [{"chainId": "solana", "tokenAddress": t} for t in self.feed]

    def boosts_latest(self):
        return [{"chainId": "ethereum", "tokenAddress": "0xnope"}]

    def profiles_latest(self):
        return []

    def takeovers_latest(self):
        raise RuntimeError("feed down")  # a failing feed must not stop the run

    def metas_trending(self):
        return []

    def meta_pairs(self, slug):
        return []

    def search(self, q):
        return []

    def pairs_for_tokens(self, chain, addrs):
        self.calls += 1
        if self.fail:
            raise RuntimeError("outage")
        return [self.market[a] for a in addrs if self.market.get(a)]

    def pairs_for_token(self, chain, addr):
        self.calls += 1
        if self.fail:
            raise RuntimeError("outage")
        return [self.market[addr]] if self.market.get(addr) else []


class FakeRug:
    def __init__(self):
        self.calls, self.bad, self.broken = 0, set(), set()

    def summary(self, mint):
        self.calls += 1
        if mint in self.broken:
            raise RuntimeError("rugcheck down")
        if mint in self.bad:
            return {"score": 9000, "score_normalised": 71, "lpLockedPct": 0,
                    "risks": [{"name": "Large Amount of LP Unlocked", "level": "danger"}]}
        return {"score": 300, "score_normalised": 5, "lpLockedPct": 100, "risks": []}


class FakeGecko:
    def __init__(self):
        self.calls, self.pools = 0, []

    def trending(self, page):
        self.calls += 1
        return self.pools if page == 1 else []

    def top(self, sort, page):
        self.calls += 1
        return []


def gecko_pool(base, quote, reserve, created):
    return {"id": "solana_POOL" + base, "type": "pool",
            "attributes": {"reserve_in_usd": str(reserve), "pool_created_at": created},
            "relationships": {"base_token": {"data": {"id": "solana_" + base}},
                              "quote_token": {"data": {"id": "solana_" + quote}}}}


class Fills(unittest.TestCase):
    def test_buy_then_sell_flat_price_loses_exactly_the_costs(self):
        tokens, exec_price, fee = P.buy_fill(0.5, 1.0, 100_000, SOL_USD, COSTS)
        net_sol = 0.5 - (0.5 * 0.005 + 0.002)
        self.assertAlmostEqual(fee, 0.0045)
        usd_in = net_sol * SOL_USD
        expect_price = 1.0 * (1 + usd_in / 50_000) * 1.005
        self.assertAlmostEqual(exec_price, expect_price)
        self.assertAlmostEqual(tokens, usd_in / expect_price)
        got, _, _ = P.sell_fill(tokens, 1.0, 100_000, SOL_USD, COSTS)
        value = tokens * 1.0
        out = value / (1 + value / 50_000) * 0.995 / SOL_USD
        self.assertAlmostEqual(got, out - (out * 0.005 + 0.002))
        self.assertLess(got, 0.5)
        self.assertGreater(got, 0.5 * 0.96)  # a round trip costs roughly 2-4%, not more

    def test_drained_pool_returns_almost_nothing(self):
        tokens, _, _ = P.buy_fill(0.5, 1.0, 100_000, SOL_USD, COSTS)
        got, _, _ = P.sell_fill(tokens, 1.0, 20, SOL_USD, COSTS)  # $20 of liquidity left
        self.assertLess(got, 0.05)
        self.assertEqual(P.sell_fill(tokens, 1.0, 0, SOL_USD, COSTS)[0], 0.0)


class Rules(unittest.TestCase):
    def view(self, **kw):
        return S.pair_view(make_pair("TOK", "TOK", 1.0, 100_000, T0, **kw), int(T0.timestamp() * 1000))

    def test_good_token_passes(self):
        v = self.view()
        self.assertIsNone(S.universe_reject(v, RULES["universe"]))
        self.assertIsNone(S.entry_reject(v, RULES["entry"], 0.0))

    def test_universe_rejections(self):
        u = RULES["universe"]
        self.assertEqual(S.universe_reject(self.view(age_days=1), u), "too_young")
        self.assertEqual(S.universe_reject(self.view(age_days=45), u), "too_old")
        self.assertEqual(S.universe_reject(self.view(vol_h24=10_000), u), "volume_h24")
        self.assertEqual(S.universe_reject(self.view(mcap=100_000), u), "mcap_small")
        self.assertEqual(S.universe_reject(self.view(mcap=40_000_000), u), "liq_to_mcap")
        thin = S.pair_view(make_pair("T", "T", 1.0, 20_000, T0), int(T0.timestamp() * 1000))
        self.assertEqual(S.universe_reject(thin, u), "liquidity")

    def test_entry_rejections(self):
        e = RULES["entry"]
        self.assertEqual(S.entry_reject(self.view(chg=(0.5, 60.0, 80.0, 90.0)), e, 0), "h1_overheated")
        self.assertEqual(S.entry_reject(self.view(chg=(0.5, 0.5, 5.0, 5.0)), e, 0), "h1_weak")
        self.assertEqual(S.entry_reject(self.view(chg=(-6.0, 8.0, 12.0, 20.0)), e, 0), "m5_dropping")
        self.assertEqual(S.entry_reject(self.view(buys_h1=50, sells_h1=60), e, 0), "buy_pressure")
        self.assertEqual(S.entry_reject(self.view(vol_h1=10_000), e, 0), "volume_accel")
        self.assertEqual(S.entry_reject(self.view(), e, 25.0), "liquidity_falling")

    def test_sol_price_from_sol_pairs(self):
        pairs = [make_pair("A", "A", 2.0, 1e5, T0), make_pair("B", "B", 0.01, 1e5, T0),
                 make_pair("C", "C", 5.0, 1e5, T0, quote="USDC")]
        self.assertAlmostEqual(S.sol_usd_from(pairs), SOL_USD)

    def test_rugcheck_assessment(self):
        s = RULES["safety"]
        self.assertEqual(assess(compact({"score_normalised": 5, "risks": []}), s), (True, None))
        self.assertEqual(assess(compact({"score_normalised": 55, "risks": []}), s)[1], "rugcheck_score")
        ok, why = assess(compact({"score_normalised": 5, "risks": [{"name": "Mint", "level": "DANGER"}]}), s)
        self.assertFalse(ok)
        self.assertTrue(why.startswith("rugcheck_risk"))
        self.assertEqual(assess(compact({"weird": True}), s)[1], "rugcheck_no_score")


class Cycle(unittest.TestCase):
    """Full bot cycles against a scripted market, in a throwaway directory."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copy(REPO / "rulebook.json", self.tmp / "rulebook.json")
        os.environ["BOT_ROOT"] = str(self.tmp)
        os.environ.pop("BOT_DATA", None)
        self.dex, self.rug, self.gecko, self.now = FakeDex(), FakeRug(), FakeGecko(), T0

    def tearDown(self):
        os.environ.pop("BOT_ROOT", None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def step(self, minutes=5):
        s = run(self.now, self.dex, self.rug, self.gecko)
        self.now += timedelta(minutes=minutes)
        return s

    def state(self):
        return store.read_json(self.tmp / "data" / "state" / "portfolio.json", None)

    def trades(self):
        return store.read_jsonl(self.tmp / "data" / "journal" / "trades.jsonl")

    def list_token(self, token, price=1.0, liq=100_000, **kw):
        self.dex.feed.append(token)
        self.set(token, price, liq, **kw)

    def set(self, token, price, liq=100_000, **kw):
        self.dex.market[token] = make_pair(token, token, price, liq, self.now, **kw)

    def test_winner_takes_profit_then_trails_out(self):
        self.list_token("WIN")
        s = self.step()
        self.assertEqual(s["opened"], ["WIN"])
        st = self.state()
        self.assertAlmostEqual(st["cash_sol"], 4.5)
        self.set("WIN", 1.25)                 # +25% -> TP1 sells half
        self.step()
        pos = self.state()["positions"][0]
        self.assertTrue(pos["tp1_done"])
        self.assertAlmostEqual(pos["tokens_remaining"], pos["tokens"] / 2)
        self.set("WIN", 1.50)                 # runs further, new peak
        self.step()
        self.assertEqual(len(self.state()["positions"]), 1)
        self.set("WIN", 1.33)                 # -11% from peak -> trailing stop
        s = self.step()
        self.assertEqual(s["closed"][0][1], "trailing_stop")
        t = self.trades()[0]
        self.assertGreater(t["pnl_sol"], 0)
        self.assertEqual(t["max_gain_pct"], 50.0)
        self.assertTrue(1.2 < t["avg_sell_usd"] < 1.33)   # half sold near 1.25, half near 1.33, minus slippage
        self.assertAlmostEqual(t["usd_in"], 0.5 * SOL_USD, places=2)
        st = self.state()
        self.assertAlmostEqual(st["cash_sol"], 5.0 + t["pnl_sol"], places=5)

    def test_loser_is_stopped_out_at_the_observed_price_not_the_stop_level(self):
        self.list_token("LOSE")
        self.step()
        self.set("LOSE", 0.70)                # gapped -30% between runs
        s = self.step()
        self.assertEqual(s["closed"][0][1], "stop_loss")
        t = self.trades()[0]
        self.assertLess(t["pnl_pct"], -30)    # pays the full gap plus costs, not a tidy -12%
        self.assertEqual(self.state()["positions"], [])

    def test_rug_liquidity_pull_is_a_near_total_loss(self):
        self.list_token("RUG")
        self.step()
        self.set("RUG", 0.9, liq=20)          # pool drained to $20
        s = self.step()
        self.assertEqual(s["closed"][0][1], "liquidity_drop")
        self.assertLess(self.trades()[0]["pnl_pct"], -85)

    def test_vanished_token_is_written_off_but_an_outage_is_not(self):
        self.list_token("GONE")
        self.step()
        self.dex.fail = True                  # API outage: must NOT count as vanished
        for _ in range(8):
            self.step()
        self.assertEqual(len(self.state()["positions"]), 1)
        self.assertEqual(self.state()["positions"][0]["missing_runs"], 0)
        self.dex.fail = False
        self.dex.market["GONE"] = None        # API answers, token is gone
        for _ in range(RULES["exit"]["missing_data_runs_to_write_off"]):
            self.step()
        t = self.trades()[0]
        self.assertEqual(t["exit_reason"], "no_data")
        self.assertEqual(t["pnl_pct"], -100.0)

    def test_time_stop_and_cooldown(self):
        self.list_token("FLAT")
        self.step()
        self.now += timedelta(hours=6, minutes=1)
        self.set("FLAT", 1.02)
        s = self.step()
        self.assertEqual(s["closed"][0][1], "time_stop")
        self.set("FLAT", 1.02)
        s = self.step()                       # signal still valid but token is cooling down
        self.assertEqual(s["opened"], [])
        self.assertEqual(s["funnel"].get("cooldown"), 1)

    def test_safety_check_blocks_and_fails_closed(self):
        self.list_token("BAD")
        self.list_token("ERR")
        self.rug.bad.add("BAD")
        self.rug.broken.add("ERR")
        s = self.step()
        self.assertEqual(s["opened"], [])
        self.assertEqual(s["funnel"].get("safety:rugcheck_score"), 1)
        self.assertEqual(s["funnel"].get("safety:rugcheck_error"), 1)
        calls = self.rug.calls
        self.step()                           # the failed verdict is cached; the errored one is retried
        self.assertEqual(self.rug.calls, calls + 1)

    def test_position_and_daily_caps(self):
        for i in range(14):
            self.list_token(f"T{i:02d}")
        self.rug_budget = RULES["safety"]["max_checks_per_run"]
        s = self.step()
        self.assertEqual(len(s["opened"]), 5)          # max_open_positions
        self.assertEqual(self.state()["cash_sol"], 2.5)
        opened_today = 5
        for _ in range(6):                              # close everything by time stop, reopen, repeat
            self.now += timedelta(hours=6, minutes=1)
            for i in range(14):
                self.set(f"T{i:02d}", 1.0)
            s = self.step()
            if self.now.strftime("%Y-%m-%d") != "2026-11-14":
                break
            opened_today += len(s["opened"])
        self.assertLessEqual(opened_today, RULES["portfolio"]["max_new_trades_per_day"])

    def test_accounting_identity_over_a_messy_session(self):
        """equity == starting capital + sum of closed P&L + open mark-to-market P&L."""
        names = [f"M{i}" for i in range(8)]
        for n in names:
            self.list_token(n)
        path = [1.0, 1.1, 1.25, 1.4, 1.2, 0.8, 1.0, 1.3, 0.6, 1.0, 1.22, 1.05]
        for k, mult in enumerate(path):
            for j, n in enumerate(names):
                px = mult * (1 + 0.03 * ((j * 7 + k * 3) % 5 - 2))
                self.set(n, px, liq=100_000 if (j + k) % 9 else 60_000)
            s = self.step(minutes=45)
        st = self.state()
        closed = sum(t["pnl_sol"] for t in self.trades())
        self.assertAlmostEqual(st["realized_pnl_sol"], closed, places=4)
        spent_open = sum(p["sol_in"] - p["sol_returned"] for p in st["positions"])
        self.assertAlmostEqual(st["cash_sol"], 5.0 + closed - spent_open, places=4)
        self.assertGreater(len(self.trades()), 3)
        r = review(self.trades(), [s], 5.0)
        self.assertIn("By exit reason", r)
        self.assertEqual(stats(self.trades())["n"], len(self.trades()))
        self.assertTrue((self.tmp / "data" / "STATUS.md").exists())
        import csv
        with open(self.tmp / "data" / "trades.csv", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), len(self.trades()) + len(st["positions"]))
        self.assertEqual(sum(r["status"] == "OPEN" for r in rows), len(st["positions"]))
        done = [r for r in rows if r["status"] == "CLOSED"]
        self.assertAlmostEqual(sum(float(r["pnl_sol"]) for r in done), closed, places=4)
        for r in done:
            self.assertAlmostEqual(float(r["pnl_pct"]), float(r["pnl_sol"]) / float(r["sol_in"]) * 100, places=1)
            self.assertAlmostEqual(float(r["sol_out"]) - float(r["sol_in"]), float(r["pnl_sol"]), places=5)
        self.assertGreater(float(rows[0]["trade_no"]), float(rows[-1]["trade_no"]))
        snaps = list((self.tmp / "data" / "snapshots").rglob("*.jsonl"))
        self.assertTrue(snaps)
        row = store.read_jsonl(snaps[0])[0]["rows"][0]
        self.assertEqual(len(row), 20)

    def test_gecko_discovery_filters_and_throttles(self):
        from bot.geckoterminal import pick_tokens
        week = (self.now - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        old = (self.now - timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ")
        usdc = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        pools = [gecko_pool("GOOD", S.WSOL, 80_000, week), gecko_pool("THIN", S.WSOL, 900, week),
                 gecko_pool("OLD", S.WSOL, 500_000, old), gecko_pool(S.WSOL, "FLIP", 90_000, week),
                 gecko_pool(S.WSOL, usdc, 9e7, week), {"junk": 1}]
        self.assertEqual(pick_tokens(pools, self.now, 30_000, 35), ["GOOD", "FLIP"])
        self.gecko.pools = pools
        self.set("GOOD", 1.0)
        s = self.step()
        self.assertEqual(s["opened"], ["GOOD"])        # found only via GeckoTerminal
        self.assertEqual(s["funnel"].get("discovered_gecko"), 2)
        self.assertEqual(self.gecko.calls, 2)           # only calls_per_cycle pages per run
        for _ in range(4):
            self.step()
        self.assertEqual(self.gecko.calls, 10)          # rotates through all 9 pages, then wraps
        meta = store.read_json(self.tmp / "data" / "state" / "meta.json", {})
        self.assertEqual(meta["gecko_idx"], 1)

    def test_young_token_waits_on_watchlist_until_old_enough(self):
        self.dex.feed.append("NEW")
        born = self.now - timedelta(days=2, hours=23)
        for _ in range(3):
            self.dex.market["NEW"] = make_pair("NEW", "NEW", 1.0, 100_000, self.now,
                                               age_days=(self.now - born).total_seconds() / 86400)
            s = self.step(minutes=30)
        self.assertEqual(s["opened"], ["NEW"])  # crossed 3 days on the third run
        self.assertEqual(len(self.trades()), 0)


if __name__ == "__main__":
    unittest.main()
