"""Offline tests: no network. A scripted fake market drives full bot cycles.

Run:  python3 -m unittest discover -s tests -v
"""
import copy
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
from bot import replay as R
from bot.report import review, stats
from bot.rugcheck import assess, compact
from bot.run import run

REPO = Path(__file__).resolve().parent.parent
RULES = json.loads((REPO / "rulebook.json").read_text())
COSTS = RULES["costs"]
T0 = datetime(2026, 11, 14, 12, 0, 0, tzinfo=timezone.utc)
SOL_USD = 200.0


def make_pair(token, symbol, price, liq, now, age_days=7, mcap=2_000_000, vol_h24=500_000, vol_h6=120_000,
              vol_h1=40_000, buys_h1=120, sells_h1=60, chg=(0.5, 8.0, 12.0, 20.0), quote="SOL",
              vol_m5=3000):
    created = int((now - timedelta(days=age_days)).timestamp() * 1000)
    qaddr = S.WSOL if quote == "SOL" else "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    return {
        "chainId": "solana", "dexId": "raydium", "pairAddress": "PAIR" + token,
        "baseToken": {"address": token, "name": symbol, "symbol": symbol},
        "quoteToken": {"address": qaddr, "name": quote, "symbol": quote},
        "priceUsd": str(price), "priceNative": str(price / SOL_USD if quote == "SOL" else price),
        "txns": {"m5": {"buys": 10, "sells": 6}, "h1": {"buys": buys_h1, "sells": sells_h1},
                 "h24": {"buys": 3000, "sells": 2500}},
        "volume": {"m5": vol_m5, "h1": vol_h1, "h6": vol_h6, "h24": vol_h24},
        "priceChange": {"m5": chg[0], "h1": chg[1], "h6": chg[2], "h24": chg[3]},
        "liquidity": {"usd": liq, "base": 1, "quote": 1},
        "fdv": mcap, "marketCap": mcap, "pairCreatedAt": created, "boosts": {"active": 0},
    }


class FakeDex:
    """`market` maps token -> pair dict (or None for 'API has nothing')."""

    def __init__(self):
        self.market, self.feed, self.calls, self.fail = {}, [], 0, False
        self.all_pools = {}  # token -> every pool, when the single lookup should show more than one

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
        if self.fail or getattr(self, "fail_single", False):
            raise RuntimeError("outage")
        if addr in self.all_pools:
            return self.all_pools[addr]
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
        self.assertEqual(S.entry_reject(self.view(buys_h1=100, sells_h1=120), e, 0), "buy_pressure")
        thin = self.view(buys_h1=e["min_txns_h1"] * 2 // 3 - 1, sells_h1=e["min_txns_h1"] // 3)
        self.assertEqual(S.entry_reject(thin, e, 0), "txns_h1")      # too few trades in the hour to read
        self.assertEqual(S.entry_reject(self.view(vol_h1=10_000), e, 0), "volume_accel")
        self.assertEqual(S.entry_reject(self.view(), e, 25.0), "liquidity_falling")

    def test_best_pairs_prefers_a_deep_enough_allowed_quote_pool(self):
        deep = make_pair("TOK", "TOK", 1.0, 300_000, T0, quote="TTWO")
        sol = make_pair("TOK", "TOK", 1.0, 80_000, T0)
        thin = make_pair("TOK", "TOK", 1.0, 5_000, T0)
        allowed = RULES["universe"]["allowed_quote_symbols"]
        pick = lambda pairs, **kw: S.best_pairs(pairs, int(T0.timestamp() * 1000), "solana", **kw)["TOK"]  # noqa: E731
        self.assertEqual(pick([deep, sol])["quote_symbol"], "TTWO")                 # old behaviour: deepest
        self.assertEqual(pick([deep, sol, thin], allowed_quotes=allowed, min_allowed_liq=30_000)["liq_usd"], 80_000)
        self.assertEqual(pick([deep, thin], allowed_quotes=allowed, min_allowed_liq=30_000)["quote_symbol"], "TTWO")

    def test_ignored_reading_is_confirmed_by_the_next_one_and_never_ignored_for_long(self):
        first = S.hold_suspect(1.0, 100_000, None, 0.0004, 100_000)
        self.assertEqual(first, {"price": 0.0004, "liq": 100_000, "runs": 1})
        self.assertIsNone(S.hold_suspect(1.0, 100_000, first, 0.00041, 99_000))     # same again: real
        self.assertIsNone(S.hold_suspect(1.0, 100_000, first, 1.01, 100_000))       # back to normal
        second = S.hold_suspect(1.0, 100_000, first, 5000.0, 100_000)               # contradicts both
        self.assertEqual(second["runs"], 2)
        self.assertIsNone(S.hold_suspect(1.0, 100_000, second, 0.0004, 100_000))    # the limit

    def test_suspect_print_needs_a_big_price_jump_with_flat_liquidity(self):
        self.assertTrue(S.suspect_print(0.0021, 56_000, 0.0000004, 52_000))    # Dacity, 2026-11-14 01:25
        self.assertTrue(S.suspect_print(0.0000004, 52_000, 0.0021, 56_000))    # and the way back up
        self.assertFalse(S.suspect_print(0.001013, 86_083, 0.0003458, 49_806))  # inuhao: a real -66% crash
        self.assertFalse(S.suspect_print(0.0001862, 30_209, 0.00039, 44_859))   # chudhaos: a real +109%
        self.assertFalse(S.suspect_print(1.0, 100_000, 0.70, 100_000))          # an ordinary gap down
        self.assertFalse(S.suspect_print(None, None, 1.0, 100_000))             # nothing to compare with

    def test_unbacked_move_is_a_big_move_that_almost_nobody_traded(self):
        # Real readings. The liquidity moved with the price, so suspect_print cannot see these two.
        self.assertFalse(S.suspect_print(0.0006272, 62_201, 0.0003898, 49_748))
        self.assertTrue(S.unbacked_move(0.0006272, 62_201, 0.0003898, 2_564, 299))   # Leonida 16:50, -38%
        self.assertTrue(S.unbacked_move(1.0, 110_782, 1.449, 12, 300))               # GLITCH 04:50, +45%
        self.assertTrue(S.unbacked_move(0.0021, 56_763, 0.0000004, 216, 300))        # Dacity: both checks agree
        # Real moves came with the volume it takes to move the pool.
        self.assertFalse(S.unbacked_move(0.001013, 86_083, 0.0003458, 58_441, 300))  # inuhao, -66%
        self.assertFalse(S.unbacked_move(1.0, 121_179, 0.537, 22_782, 300))          # AMC, -46%
        self.assertFalse(S.unbacked_move(0.0009278, 69_326, 0.0007032, 4_031, 305))  # AI, -24%: thin but real
        # Not judged: an ordinary move, a late cycle (the 5-minute volume cannot vouch for it), no data.
        self.assertFalse(S.unbacked_move(1.0, 100_000, 0.85, 0, 300))                # -15% is the stop's business
        self.assertFalse(S.unbacked_move(1.0, 100_000, 1.24, 0, 300))
        self.assertFalse(S.unbacked_move(0.0006272, 62_201, 0.0003898, 2_564, 900))
        self.assertFalse(S.unbacked_move(0.0006272, 62_201, 0.0003898, 2_564, None))
        self.assertFalse(S.unbacked_move(0.0006272, 62_201, 0.0003898, None, 300))

    def test_traded_since_takes_the_better_of_two_volume_witnesses(self):
        # AI, 2026-11-14 06:30: the 5-minute volume read $30 while the 24-hour volume had risen $4,031.
        self.assertEqual(S.traded_since({"vol_m5": 30.0, "vol_h24": 94_165.0}, 90_134.0), 4_031.0)
        # GLITCH's bad print: neither moved. Old volume rolling off must not count against the 5-minute figure.
        self.assertEqual(S.traded_since({"vol_m5": 12.0, "vol_h24": 150_760.0}, 150_794.0), 12.0)
        self.assertEqual(S.traded_since({"vol_m5": 500.0, "vol_h24": 9_000.0}, None), 500.0)
        self.assertIsNone(S.traded_since({"vol_h24": 9_000.0}, 8_000.0))             # a row with no volume field

    def test_unbacked_move_is_held_back_once_and_never_twice(self):
        note = S.hold_suspect(0.0006272, 62_201, None, 0.0003898, 49_748, 2_564, 299)
        self.assertEqual(note["runs"], 1)
        self.assertIsNone(S.hold_suspect(0.0006272, 62_201, note, 0.00039, 49_700, 500, 599))    # still there: real
        self.assertIsNone(S.hold_suspect(0.0006272, 62_201, note, 0.0006233, 61_723, 875, 599))  # back: nothing happened
        self.assertIsNone(S.hold_suspect(0.0006272, 62_201, None, 0.0003898, 49_748))            # callers without volume

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


class Replay(unittest.TestCase):
    def test_token_that_leaves_the_record_while_held_is_lost_not_a_winner(self):
        from bot.run import snapshot_row
        row = lambda tok, px, now: snapshot_row(  # noqa: E731
            S.pair_view(make_pair(tok, tok, px, 100_000, now), int(now.timestamp() * 1000)))
        snaps = []
        for k in range(10):
            now = T0 + timedelta(minutes=5 * k)
            rows = [row("STAY", 1.0 + 0.01 * k, now)] + ([row("GONE", 1.1, now)] if k < 2 else [])
            snaps.append({"ts": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "sol_usd": SOL_USD, "rows": rows})
        trades = {t["symbol"]: t for t in R.replay(snaps, RULES)}
        self.assertEqual({k: t["exit_reason"] for k, t in trades.items()}, {"STAY": "open", "GONE": "lost"})
        text = R.report(list(trades.values()))
        self.assertIn("0 closed, 1 still open, 1 lost from the record (not counted)", text)


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
        self.set("LOSE", 0.70, vol_m5=20_000)  # gapped -30% between runs, on real selling
        s = self.step()
        self.assertEqual(s["closed"][0][1], "stop_loss")
        t = self.trades()[0]
        self.assertLess(t["pnl_pct"], -30)    # pays the full gap plus costs, not a tidy -12%
        self.assertEqual(self.state()["positions"], [])

    def test_one_cycle_bad_price_print_fills_nothing_but_a_repeated_one_is_acted_on(self):
        self.list_token("GLITCH")
        self.step()
        self.set("GLITCH", 0.0004)            # -99.96% with the pool's liquidity untouched: a bad print
        s = self.step()
        self.assertEqual((s["closed"], s["funnel"].get("suspect_price")), ([], 1))
        pos = self.state()["positions"][0]
        self.assertEqual((pos["last_price_usd"], pos["trough_usd"]), (1.0, 1.0))
        self.assertAlmostEqual(s["equity_sol"], 5.0, delta=0.02)   # still marked at the last good price
        self.set("GLITCH", 5000.0)            # a different impossible print confirms nothing
        s = self.step()
        self.assertEqual((s["closed"], s["funnel"].get("suspect_price")), ([], 1))
        self.assertFalse(self.state()["positions"][0]["tp1_done"])
        self.set("GLITCH", 0.98)              # back to normal: the position was never touched
        s = self.step()
        self.assertEqual((s["closed"], s["funnel"].get("suspect_price")), ([], None))
        pos = self.state()["positions"][0]
        self.assertEqual((pos["last_price_usd"], pos["peak_usd"], pos["trough_usd"]), (0.98, 1.0, 0.98))
        self.assertEqual(self.trades(), [])
        events = store.read_jsonl(self.tmp / "data" / "journal" / "events.jsonl")
        self.assertEqual([e["event"] for e in events], ["open", "suspect_price", "suspect_price"])
        for px in (0.0004, 5000.0, 0.0004):   # garbage that never settles is not ignored for ever
            self.set("GLITCH", px)
            s = self.step()
        self.assertEqual(s["closed"][0][1], "stop_loss")

    def test_bad_print_upwards_does_not_take_profit_and_the_position_carries_on(self):
        self.list_token("SPIKE")
        self.step()
        self.set("SPIKE", 5000.0)             # x5000 with flat liquidity
        s = self.step()
        self.assertEqual(s["funnel"].get("suspect_price"), 1)
        pos = self.state()["positions"][0]
        self.assertFalse(pos["tp1_done"])
        self.assertEqual(pos["peak_usd"], 1.0)
        self.set("SPIKE", 1.05)               # back to normal: nothing happened
        s = self.step()
        self.assertEqual((s["closed"], s["funnel"].get("suspect_price")), ([], None))
        self.assertEqual(self.state()["positions"][0]["last_price_usd"], 1.05)
        self.set("SPIKE", 0.0004)             # a low print that is still there one cycle later is real
        self.assertEqual(self.step()["closed"], [])
        s = self.step()
        self.assertEqual(s["closed"][0][1], "stop_loss")
        self.assertLess(self.trades()[0]["pnl_pct"], -99)

    def test_big_move_on_almost_no_volume_waits_one_cycle_for_a_second_reading(self):
        # Leonida, 2026-11-14 16:50 UTC: -38% for one cycle, liquidity down 20% with it, $2.3k traded.
        self.list_token("DIP")
        self.step()
        self.set("DIP", 0.62, liq=80_000, vol_m5=2_300)
        s = self.step()
        self.assertEqual((s["closed"], s["funnel"].get("suspect_price")), ([], 1))
        pos = self.state()["positions"][0]
        self.assertEqual((pos["last_price_usd"], pos["trough_usd"]), (1.0, 1.0))
        self.set("DIP", 0.99, vol_m5=900)     # back where it was: no stop was filled at a price nobody paid
        s = self.step()
        self.assertEqual((s["closed"], s["funnel"].get("suspect_price")), ([], None))
        self.assertEqual(self.state()["positions"][0]["trough_usd"], 0.99)
        # GLITCH, 04:50 UTC the same day: +45% for one cycle on $12. No take-profit at a fantasy price.
        self.set("DIP", 1.45, liq=122_000, vol_m5=12)
        s = self.step()
        self.assertEqual(s["funnel"].get("suspect_price"), 1)
        pos = self.state()["positions"][0]
        self.assertEqual((pos["tp1_done"], pos["peak_usd"]), (False, 1.0))
        self.set("DIP", 1.0, vol_m5=34)
        self.assertEqual(self.step()["closed"], [])
        # A fall that is still there on the next cycle is real, however little volume was reported.
        self.set("DIP", 0.62, liq=80_000, vol_m5=2_300)
        self.assertEqual(self.step()["closed"], [])
        s = self.step()
        self.assertEqual((s["closed"][0][1], s["funnel"].get("suspect_price")), ("stop_loss", None))
        self.assertLess(self.trades()[0]["pnl_pct"], -38)
        events = store.read_jsonl(self.tmp / "data" / "journal" / "events.jsonl")
        self.assertEqual([e["event"] for e in events],
                         ["open", "suspect_price", "suspect_price", "suspect_price", "close"])
        self.assertEqual(events[1]["traded_usd"], 2_300)

    def test_real_move_shows_in_the_24h_volume_even_when_the_5_minute_figure_lags(self):
        # AI, 2026-11-14 06:30 UTC: -24% that stayed, 5-minute volume $30, 24-hour volume up $4k.
        self.list_token("LAG")
        self.step()
        self.set("LAG", 0.76, liq=88_000, vol_m5=30, vol_h24=507_000)
        s = self.step()
        self.assertEqual(s["closed"][0][1], "stop_loss")
        self.assertNotIn("suspect_price", s["funnel"])

    def test_late_cycle_acts_on_a_big_move_without_asking_the_five_minute_volume(self):
        self.list_token("LATE")
        self.step(minutes=20)                  # the next cycle comes 20 minutes later
        self.set("LATE", 0.62, liq=80_000, vol_m5=100)
        s = self.step()
        self.assertEqual(s["closed"][0][1], "stop_loss")
        self.assertNotIn("suspect_price", s["funnel"])

    def test_real_crash_with_falling_liquidity_is_stopped_at_once(self):
        self.list_token("CRASH")
        self.step()
        # -66%, the pool shrank with it and the selling shows in the volume (like inuhao, 2026-11-13)
        self.set("CRASH", 0.34, liq=75_000, vol_m5=58_000)
        s = self.step()
        self.assertEqual(s["closed"][0][1], "stop_loss")
        self.assertNotIn("suspect_price", s["funnel"])
        self.assertLess(self.trades()[0]["pnl_pct"], -60)

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
        self.assertIn("| raydium | %d |" % len(self.trades()), r)   # results split by the entry pool's DEX
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
        self.assertEqual(len(row), 22)
        self.assertEqual(row[20], "SOL")                # quote symbol, so reviews can replay the universe filter
        self.assertEqual(row[21], "raydium")            # DEX of the pool, so reviews can split pools by DEX

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

    def test_quote_rejected_token_has_its_pools_recorded_once(self):
        self.list_token("OK")
        self.list_token("EXO", liq=150_000, quote="TTWO")      # deepest pool is quoted in an exotic token
        sol_pool = make_pair("EXO", "EXO", 1.0, 20_000, self.now)   # its SOL pool is too thin to matter
        sol_pool["pairAddress"] = "PAIRSOL"
        other = make_pair("ELSE", "ELSE", 1.0, 500_000, self.now)
        self.dex.all_pools["EXO"] = [sol_pool, self.dex.market["EXO"], other]
        s = self.step()
        self.assertEqual(s["opened"], ["OK"])                  # a thin SOL pool does not make it tradable
        self.assertEqual(s["funnel"].get("u:quote_token:TTWO"), 1)
        self.assertNotIn("allowed_pool_used", s["funnel"])
        self.assertEqual(s["errors"], ["takeovers_latest: feed down"])
        f = self.tmp / "data" / "debug" / "quote_reject_pairs.json"
        d = store.read_json(f, {})["EXO"]
        self.assertEqual([(p["quote"], p["liq_usd"]) for p in d["pools"]], [("TTWO", 150_000), ("SOL", 20_000)])
        self.assertEqual((d["chosen_quote"], d["pairs_in_batch"], d["pools_returned"]), ("TTWO", 1, 3))
        calls = self.dex.calls
        self.step()
        # One batch call and one pool lookup for EXO; the debug sample itself is taken once, not every cycle.
        self.assertEqual(self.dex.calls, calls + 2)
        self.assertEqual(store.read_json(f, {})["EXO"]["ts"], d["ts"])
        self.dex.fail_single = True                            # a failing lookup is logged, never fatal
        self.list_token("EXO2", quote="WBTC")
        s = self.step()
        self.assertTrue(any(e.startswith("quote sample") for e in s["errors"]))
        self.assertTrue(any(e.startswith("pool lookup") for e in s["errors"]))
        self.assertEqual(len(self.state()["positions"]), 1)

    def hidden_sol_pool(self, token="EXO", sol_liq=90_000, exotic_liq=150_000, sol_age=7, exotic_age=7):
        """Batch call shows only an exotic-quoted pool; the full lookup also shows a SOL pool."""
        if "REF" not in self.dex.market:   # a quiet SOL-quoted token, so the run can derive the SOL price
            self.list_token("REF", chg=(0.0, 0.0, 0.0, 0.0))
        self.list_token(token, liq=exotic_liq, quote="TTWO", age_days=exotic_age)
        sol_pool = make_pair(token, token, 1.0, sol_liq, self.now, age_days=sol_age)
        sol_pool["pairAddress"] = "PAIRSOL" + token
        self.dex.all_pools[token] = [self.dex.market[token], sol_pool]
        return sol_pool

    def test_token_is_traded_on_its_allowed_quote_pool_and_the_position_follows_that_pool(self):
        sol_pool = self.hidden_sol_pool()
        s = self.step()
        self.assertEqual(s["opened"], ["EXO"])
        self.assertEqual(s["funnel"].get("allowed_pool_used"), 1)
        self.assertNotIn("u:quote_token:TTWO", s["funnel"])
        pos = self.state()["positions"][0]
        self.assertEqual((pos["pair"], pos["entry_liq_usd"], pos["features"]["quote"]), ("PAIRSOLEXO", 90_000, "SOL"))
        # The SOL pool is drained while the exotic pool the batch call returns still looks healthy.
        sol_pool["liquidity"]["usd"] = 20
        s = self.step()
        self.assertEqual(s["closed"][0][1], "liquidity_drop")
        self.assertLess(self.trades()[0]["pnl_pct"], -85)      # filled against the drained pool, not the deep one

    def test_failed_pool_lookup_is_not_a_liquidity_drop_but_the_price_stop_still_works(self):
        self.hidden_sol_pool(sol_liq=90_000, exotic_liq=55_000)   # the batch pool is 39% thinner than ours
        self.assertEqual(self.step()["opened"], ["EXO"])
        self.dex.fail_single = True
        s = self.step()
        self.assertEqual(s["closed"], [])                      # another pool's liquidity proves nothing
        self.assertTrue(any(e.startswith("pool lookup") for e in s["errors"]))
        self.dex.market["EXO"]["priceUsd"] = "0.70"            # price is still watched through the batch pool
        s = self.step()
        self.assertEqual(s["closed"][0][1], "stop_loss")

    def test_allowed_pool_must_be_genuine_and_does_not_make_an_old_token_young(self):
        fake = self.hidden_sol_pool("FAKE")
        fake["quoteToken"]["address"] = "LookAlikeMint1111111111111111111111111111111"
        self.hidden_sol_pool("OLD", sol_age=10, exotic_age=33)   # token is 33 days old, its SOL pool 10
        s = self.step()
        self.assertEqual(s["opened"], [])
        self.assertEqual(s["funnel"].get("u:quote_token:TTWO"), 1)   # FAKE: a token merely called SOL
        self.assertEqual(s["funnel"].get("u:too_old"), 1)            # OLD: judged by its oldest pool
        self.assertEqual(s["funnel"].get("allowed_pool_used"), 1)

    def test_replay_reproduces_the_bots_own_trades_from_the_snapshots(self):
        self.list_token("WIN")
        self.list_token("LOSE")
        self.list_token("THIN", buys_h1=60, sells_h1=30)   # under min_txns_h1: never bought
        self.step()
        for win, lose in ((1.25, 0.95), (1.50, 0.80), (1.33, 0.80)):
            self.set("WIN", win)
            self.set("LOSE", lose)
            self.step()
        real = {t["symbol"]: t for t in self.trades()}
        self.assertEqual({k: t["exit_reason"] for k, t in real.items()},
                         {"WIN": "trailing_stop", "LOSE": "stop_loss"})
        snaps = R.load_snapshots()
        again = {t["symbol"]: t for t in R.replay(snaps, RULES)}
        self.assertEqual(set(again), {"WIN", "LOSE"})
        for k, t in real.items():
            self.assertEqual(again[k]["exit_reason"], t["exit_reason"])
            self.assertAlmostEqual(again[k]["pnl_pct"], t["pnl_pct"], delta=0.05)
            self.assertEqual(again[k]["max_gain_pct"], t["max_gain_pct"])
        loose = copy.deepcopy(RULES)
        loose["entry"]["min_txns_h1"] = 50                 # the entries a rule blocks can still be measured
        self.assertIn("THIN", {t["symbol"] for t in R.replay(snaps, loose)})
        wide = R.replay(snaps, R.wide_rules(RULES), cooldown=False)
        self.assertGreaterEqual(len(wide), 2)
        self.assertIn("| WIN |", R.report(wide))

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
