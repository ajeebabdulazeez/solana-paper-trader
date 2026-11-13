# Lessons and rule changes

The running record of what paper results have shown and why each rulebook version exists. Newest first. Each review adds an entry; a rule only changes when the data here supports it.

## How to review (instructions for each review session)

1. Run `python3 -m bot.report` and read `data/STATUS.md` and the latest `data/runs/*.jsonl` errors.
2. First check the bot is healthy: runs arriving, no repeated errors, `batch_miss` low, signals appearing. Fix plumbing before judging strategy.
3. Judge the current rulebook version only on its own trades. Under about 30 closed trades, treat every pattern as a hint, not a finding.
4. Look for: which exit reasons lose the most, which entry features separate winners from losers, how much gain was left on the table, and which funnel stage blocks the most candidates.
5. Change at most one rulebook section per review, bump `version`, and write the entry below: what the data showed, what changed, and what result would prove the change wrong.
6. Never loosen a safety rule to get more trades. Never tune to hit a return target.
7. Once a version looks good, stop changing it: the proof gate needs 100+ trades on one frozen version.

## Log

### v2, 2026-11-13 23:40 UTC review: no rule change (plumbing: trade a token on its SOL pool when the batch call hides it)

**Health.** 116 cycles since 13:43 UTC. Over the last 6 hours: 73 cycles, median gap 5.0 minutes, longest 5.2 minutes. The newest cycle was 1.4 minutes old at review time, so no `.kick`. Errors in 2 of 116 runs, the same two early GeckoTerminal 429s; none in the last 113. `batch_miss` is 7 to 11 per cycle out of about 280 tokens (about 4%): 7 are `no_data` (6 of them never had a Solana pair and drop off after 24 hours) and the rest are recovered by the single lookup. RugCheck has run 3 times (WEALTH, FLOAT, Leonida): each returned `score_normalised` 1, no risks, and LP locked 99.8%, 61.6% and 75.7%, all parsed correctly. No `safety:rugcheck_*` or `skip:*` rows in the funnel.

**Strategy: 3 closed trades on v2, all losses. That is a hint, not a finding.** Equity 4.7553 SOL (-4.89%), no open positions.

| Trade | Opened | Best price while held | Last cycle before the stop | Stop cycle (price) | Net result |
|---|---|---|---|---|---|
| WEALTH | 17:25 | +0.5% | -11.9% | -15.8% | -18.84% |
| FLOAT | 18:50 | +2.4% | -7.3% | -13.8% | -13.55% |
| Leonida | 18:55 | 0.0% | -4.1% | -14.3% | -16.84% |

- All three exits were `stop_loss`, average -16.41%. A stop filled exactly at -12% would cost about -15% after costs, so the overshoot is about 1.4 points per trade. Cycles were on time, so this is not a late-trigger problem: each stop was crossed by a fall of 4 to 10 points between two consecutive cycles, and the price was 1.8 to 3.8 points past the stop level when the bot saw it.
- The stops were not shaken out. At 23:30 UTC, about four hours after their stops, WEALTH was about 25% under its entry and Leonida about 23% under; FLOAT was still at -13% 15 minutes after its stop. Nothing here says the stop is too tight.
- No trade ever got above +2.4%, so nothing was left on the table. The entries were the problem, not the exits.
- Leonida (hint, n=1): the buy came 5 minutes after an -11.5% five-minute candle. The 1-hour change had fallen from +25.9% to +9.0% in 15 minutes, so the token still read as "moderate momentum" while it was already reversing from a spike. The entry rule only looks at the current 5-minute change (-1.0% at the signal).
- WEALTH (hint, n=1, from the last review): the signal was one +5.4% candle in a thin token (125 trades in the hour).
- Market: SOL fell from $80.8 to $77.4 over the session (-4%), most of it after 21:30 UTC. FLOAT sat between -1% and -7% for four hours and was stopped during that slide.

**Funnel since the last review (62 runs).** Signals: 2 (18:50 and 18:55). The last signal was 4.7 hours before this review, so the 12-hour zero-signal rule is not met and no threshold was relaxed. Of 374 universe-token checks, 177 (47%) were a token already held or in its 12-hour cooldown, 112 were `h1_weak`, 49 `buy_pressure`, 15 `h6_down`, 9 `h1_overheated`, 6 `m5_dropping`, 4 `volume_accel`. The universe is 6 or 7 tokens (mihao, FLOAT, NIO, WASTED, paws, Leonida, WEALTH), and three of them are now on cooldown until 07:35, 07:55 and 11:15 UTC on 14 Nov. That leaves 4 tokens the bot can actually buy. Universe size is the bottleneck, ahead of any entry threshold.

**Correction to the last review.** It expected the universe to grow "from tomorrow" as young tokens aged in. Ten tokens under 3 days old pass every other universe number now, but the oldest is 2.1 days (Max, eligible about 21:00 UTC on 14 Nov) and the next is 1.55 days. So ageing adds almost nothing before the 24-hour mark.

**Pool selection: the question from the last review is answered, and it was a real bug.** `data/debug/quote_reject_pairs.json` now has 7 tokens, sampled between 18:40 and 19:10 UTC. In all 7 the batch call returned exactly one pool for the token, and it is not always the deepest one:

| Token | Pool the bot saw | Best SOL pool | Verdict on the SOL pool |
|---|---|---|---|
| STANK | raydium, STONK, $88k | meteora, $120k (deeper than the one the bot saw) | passes the universe by itself |
| CHOO | pumpswap, WBTC, $109k | meteora, $74k | passes the universe by itself |
| DacityCoin | pumpswap, TTWO, $313k | meteora, $103k | fails `liq_to_mcap` (2.3% against a 3% floor) |
| AMD | pumpswap, AMD, $95k | meteora, $24k | too thin |
| MAMESUKE | raydium, STONK, $31k | meteora, $22k | too thin |
| BIG | pumpswap, TTWO, $103k | meteora, $4k | too thin |
| HUNG | pumpswap, NVDAX, $47k | meteora, $8k | too thin |

The last review set the test in advance: change pool selection only if a sampled token has a SOL, USDC or USDT pool that passes the universe thresholds by itself. Two of seven do, and for STANK the bot was not even looking at the deepest pool.

**Changed.** Rulebook: nothing, v2 stays, no threshold touched. Bot code (plumbing, no version bump):

1. Each cycle, a token that is good enough for the watchlist but whose pool is quoted in something other than SOL, USDC or USDT gets one full pool lookup (at most 12 tokens per cycle, about 9 today; the endpoint is the one the debug sampler already used live). If the token has a pool quoted in a genuine allowed token (the mint address is checked, not only the symbol) with at least the watchlist's $30k minimum, the token is judged and traded on that pool. Liquidity, volume, trade counts, price impact and stops all come from that pool, not from the bigger exotic pool. The token's age is taken from its oldest pool, so a young SOL pool cannot make an old token eligible. If there is no such pool, nothing changes and the token stays rejected under `u:quote_token:*`.
2. An open position is always priced on the pool it was opened on. If that pool's data cannot be fetched in a cycle, the price stop still runs on the token's other pool, but another pool's liquidity is not read as a liquidity drop (same principle as "an outage is not a rug").
3. New funnel row `allowed_pool_used`: how many tokens were switched to an allowed-quote pool that cycle. New error prefix `pool lookup`.
4. `python3 -m bot.report` gains a "By DEX of the entry pool" table.

An offline dry run of two cycles on a copy of the live state (latest snapshot plus the sampled pools) gave: no errors, STANK and CHOO join the universe (7 to 9), DacityCoin moves from `u:quote_token:TTWO` to `u:liq_to_mcap`, AMD, BIG and HUNG stay rejected. Tests: 4 added, 2 adjusted, 22 pass.

**This changes which trades v2 takes.** Pushed at 23:39 UTC on 13 Nov and live from the 23:40 cycle; trades opened from then on can be on a pool the bot could not see before. They are recognisable in the journal: `features.dex` and `pair` name the pool.

**First live cycle (23:40 UTC).** No errors, `api_calls` 41 (was 32), `allowed_pool_used` 4, `universe_ok` 9 (was 7). The four switched tokens, read from the snapshot:

| Token | Before (23:35) | After (23:40) | Universe result |
|---|---|---|---|
| STANK | STONK pool, $86k | SOL pool, $142k | eligible |
| CHOO | WBTC pool, $105k | SOL pool, $70k | eligible |
| DacityCoin | TTWO pool, $314k | SOL pool, $97k | `liq_to_mcap` |
| Dacity | TTWO pool, $240k | SOL pool, $56k, age kept at 33.5 days | `too_old` |

Prices on the SOL pools were within 3% of the exotic pools. STANK and CHOO were both `h1_weak` on that cycle, so no trade yet.

**Blind spot this makes more relevant (not fixed, cannot be from this data).** The SOL pools of STANK and CHOO are Meteora pools. Meteora pool fees vary by pool and can be well above the flat 0.5% swap fee the cost model charges; DexScreener does not report the fee. The bot could already buy tokens whose main pool is on Meteora, so this is not new, but more trades may now land there. The costs section was not touched. Judge Meteora-pool trades separately (the new report table) and treat a small edge on them as unproven.

**For the next review.**

- Confirm the pool lookups stayed clean overnight: `allowed_pool_used` about 4 per cycle, `api_calls` about 41, no `pool lookup` errors.
- If the next closed trades repeat Leonida's shape (bought within a few cycles of a 5-minute drop of 10% or more, or with the 1-hour change collapsing from above the overheated line), the entry section is the candidate. With three trades it is a story, not evidence.
- At 13:45 UTC on 14 Nov the 24-hour check from the last review falls due: `universe_ok` under 10 per run means discovery or the universe filters are still the bottleneck.

**Would prove this review wrong.** The pool change is wrong if `pool lookup` errors repeat across cycles, if cycles slow down or `api_calls` climbs past about 60, or if a trade opened on a switched pool shows a fill or a liquidity reading that does not match that pool on DexScreener: then revert `refine_pools`. Leaving the rules alone is wrong if the next 5 to 10 closed trades are again stopped out without ever being more than a few percent in profit: at that point the entry rules are buying local tops and the entry section should change, even under 30 trades.

### v2, 2026-11-13 18:35 UTC review: no rule change (plumbing: quote-token diagnostics)

**Health.** 54 cycles since 13:43 UTC. Since the external scheduler started at 14:18 there have been 51 cycles with a median gap of 5.0 minutes and a longest gap of 5.2 minutes (one 26-minute gap before that). The newest cycle was under 2 minutes old at review time, so no `.kick` was needed. Errors in 2 of 54 runs, both GeckoTerminal 429s from before the 2-pages-per-cycle fix; none in the last 51 runs. `batch_miss` is 2 to 7 per cycle out of about 290 tokens fetched (about 2%), and 6 of the 7 are tokens DexScreener has no Solana pair for (`no_data`); they drop off after 24 hours. RugCheck ran once (for WEALTH): the saved sample has `score_normalised` 1, `risks` [] and `lpLockedPct` 99.75, and `compact()`/`assess()` read all three correctly. No `safety:rugcheck_*` rejections.

**Funnel caveat (not fixed, harmless).** `discovered_new` (3,979) and `watch_too_old` (3,754) are not unique tokens. About 66 too-old tokens are dropped at the end of every run and found again from the DexScreener feeds on the next. That costs about 3 extra batch calls per cycle (28 calls in total, far under the limits) and has no effect on trading. Read those two rows as noise.

**Strategy: nothing to judge yet.** v2 has 0 closed trades and 1 open (WEALTH, opened 17:25 UTC; at 18:30 it was -5.5% on price, peak +0.5%, trough -6.6%). One entry signal in 4.8 hours. The 12-hour zero-signal rule is not met (the bot has not existed for 12 hours and it did signal once), so no threshold was relaxed. For scale: a round trip costs about 3% of a 0.5 SOL position (0.5% fee and 0.5% slippage each way, 0.002 SOL fixed each way, plus pool impact), so the +20% target nets about +17% and the -12% stop costs about -15%.

- Universe: `universe_ok` is 6 to 8 per run, and it was the same 8 tokens all session (mihao, FLOAT, Leonida, NIO, WEALTH, :3, paws, WASTED). `u:too_young` (about 18 per run) is the biggest block. In the latest snapshot 9 of those young tokens pass every other universe number (ages 0.2 to 2.0 days; the quote token is unknown), so the universe should grow by itself from tomorrow if they keep their liquidity.
- Entry: of 369 universe-token checks, `h1_weak` blocked 241 (65%), `buy_pressure` 46, `h6_down` 28, `volume_accel` 16, `h1_overheated` 13, `m5_dropping` 8, `h24_dumped` 3, and 13 were the held token; 1 signal. Only 33% of observations had a 1-hour change of +2% or more (median -1.2%) on an afternoon when SOL slid from $81.2 to $80.0. That is the filter working in a soft market, not a bug.
- Quote-token exclusion is bigger than it looked. Replaying the snapshots through the rulebook and matching the per-run funnel counts (an exact match on all 53 v2 runs) shows five tokens that pass every other universe filter are rejected on every run for their quote token: BIG, STANK, AMD, DacityCoin and CHOO. That is 5 of 13 otherwise-eligible tokens. Four of the five have pump.fun mint addresses, so I suspected an ordinary SOL pool was being hidden: the bot judges each token by its deepest pool only. The first live samples (below) say that suspicion is wrong. In the replay CHOO met the entry rules 6 times and DacityCoin once, but on exotic-pool numbers, so that is only indicative.
- Hint from one open trade (n=1, not a finding): the WEALTH signal came from a single +5.4% five-minute candle in a thin token (125 trades and $14k volume in the hour, `volume_accel` 1.21 against a 1.2 bar). The 1-hour change had been -4.9% thirty minutes earlier. By 18:30 `volume_accel` was 0.44 and sells outnumbered buys.

**Changed.** Rulebook: nothing, v2 stays. Plumbing only, no version bump, no decision changed:

1. `data/debug/quote_reject_pairs.json`: for up to 8 quote-rejected tokens, once per token and one extra DexScreener call per cycle, the bot records every pool of that token (quote, liquidity, 24h volume, trades) and how many pairs the batch call returned for it.
2. Snapshot rows gain a 21st field, `quote_symbol`, so a review can replay the universe filter exactly instead of inferring it.

Test added: `test_quote_rejected_token_has_its_pools_recorded_once`. 18 tests pass. Live from the 18:40 UTC cycle; the 18:40 and 18:45 cycles both ran with no errors and 21-field snapshot rows.

**First live samples (18:40 and 18:45 UTC).** The exotic pool is the token's real market, not a mask over a SOL pool:

| Token | Main pool | Liquidity | Best SOL/USDC pool | Liquidity |
|---|---|---|---|---|
| BIG | pumpswap, quoted in TTWO | $103,075 | meteora, SOL | $3,870 |
| HUNG | pumpswap, quoted in NVDAX | $46,619 | meteora, SOL | $7,686 |

Both SOL pools are far under the $50k universe floor, so these two are correctly excluded whichever pool is picked. The batch call returned one pair per token (`pairs_in_batch` 1). In the 18:40 snapshot 14 of 44 watchlist rows were quoted in something other than SOL, USDC or USDT (TTWO 4, STONK 2, NVDAX 2, WBTC, AMD, MIHAO, PUMP), so PumpSwap pools paired against tokenized stocks and other tokens are a real slice of this market. Trading them would mean adding quote symbols to the `universe` section, which is a rule change that needs its own evidence (the P&L would also carry the quote token's price moves); not done.

**For the next review.**

- Read the rest of `data/debug/quote_reject_pairs.json` (up to 8 tokens, filled one per cycle). If every sample looks like BIG and HUNG (SOL pool under $50k), the exclusion is right and the question is closed. Only if a sampled token has a SOL, USDC or USDT pool that passes the universe thresholds by itself is pool selection hiding an eligible token: then make `best_pairs` prefer the deepest allowed-quote pool (plumbing; no threshold or safety rule changes) and note when it went live, because it changes which trades v2 takes.
- If the first closed trades repeat the WEALTH pattern (the 5-minute move makes up most of the 1-hour move, low `txns_h1`), the entry section is the candidate, for example a higher `min_txns_h1`. Not before there are closed trades to show it.

**Would prove this review wrong.** Leaving the rules alone is wrong if, at the 24-hour mark (about 13:45 UTC on 14 Nov), `universe_ok` is still under 10 per run after the young tokens have aged in, or if 12 hours pass with cycles arriving and no signal: then relax one threshold as the review rules allow. The plumbing change is wrong if a `quote sample` error starts repeating in `data/runs`: remove it.

### v2, 2026-11-13: wider discovery (trading rules unchanged)

First live run (13:43 UTC) parsed the DexScreener API cleanly: no errors, SOL price derived, 158 of 160 discovered tokens returned data. Finding: DexScreener's boost, profile, takeover and meta feeds are a poor source for our universe. Of 160 tokens, 86 had under $30k liquidity, 66 were older than 35 days, 4 were under 3 days old, and only 1 was in the tradable band (it failed the buy-pressure test). At that rate 10 trades a day is impossible.

Change: added GeckoTerminal trending and most-traded Solana pools as a discovery source (pre-filtered to pools with at least $30k reserve and at most 35 days old). Prices and decisions still come from DexScreener.

Would prove it wrong: if after a day the tradable universe (funnel `universe_ok`) is still under about 10 tokens per run, discovery is still the bottleneck and needs another source. Second live run (13:52 UTC) confirmed GeckoTerminal parsing: 33 tokens discovered, tradable universe rose from 1 to 6, with 14 more under 3 days old waiting to age in. GeckoTerminal returned HTTP 429 on the 10th call, so calls are now spaced 6.5s and pages cut to 9 per cycle (plumbing fix, no version bump). Six tokens were rejected for an unlisted quote token; the funnel now records which. Third live run (14:18 UTC): GeckoTerminal still returned 429 on the 6th call at 6.5s spacing, so the bot now fetches 2 pages per cycle and rotates through 9 pages (each refreshed about every 25 minutes). The unlisted quote tokens were AMD, NVDAX, TTWO, STONK and WBTC (tokenized-stock and other exotic pairs): correctly excluded, no change. GitHub never started the 5-minute timer in 45 minutes. A long-running session design was tried and dropped at Ajeeb's request the same morning: the workflow is back to one short run per cycle, started by an external 5-minute scheduler calling GitHub's run-workflow API (reliable), with GitHub's own timer as a best-effort fallback; pushing a change to `.kick` also starts one run. Not yet verified live: RugCheck handling (only called when an entry signal fires; check `data/debug/rugcheck_sample.json` and run errors).

### v1, 2026-11-13: starting hypotheses

No data yet. Thresholds are guesses based on the agreed approach: established tokens (3 to 30 days), real liquidity, safety-screened, moderate momentum entries, tight risk per trade. First job of the first reviews is to confirm the bot's data plumbing against the live API, which could not be tested before launch.
