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

### v2, 2026-11-13 18:45 UTC review: no rule change (plumbing: quote-token diagnostics)

**Health.** 54 cycles since 13:43 UTC. Since the external scheduler started at 14:18 there have been 51 cycles with a median gap of 5.0 minutes and a longest gap of 5.2 minutes (one 26-minute gap before that). The newest cycle was under 2 minutes old at review time, so no `.kick` was needed. Errors in 2 of 54 runs, both GeckoTerminal 429s from before the 2-pages-per-cycle fix; none in the last 51 runs. `batch_miss` is 2 to 7 per cycle out of about 290 tokens fetched (about 2%), and 6 of the 7 are tokens DexScreener has no Solana pair for (`no_data`); they drop off after 24 hours. RugCheck ran once (for WEALTH): the saved sample has `score_normalised` 1, `risks` [] and `lpLockedPct` 99.75, and `compact()`/`assess()` read all three correctly. No `safety:rugcheck_*` rejections.

**Funnel caveat (not fixed, harmless).** `discovered_new` (3,979) and `watch_too_old` (3,754) are not unique tokens. About 66 too-old tokens are dropped at the end of every run and found again from the DexScreener feeds on the next. That costs about 3 extra batch calls per cycle (28 calls in total, far under the limits) and has no effect on trading. Read those two rows as noise.

**Strategy: nothing to judge yet.** v2 has 0 closed trades and 1 open (WEALTH, opened 17:25 UTC; at 18:30 it was -5.5% on price, peak +0.5%, trough -6.6%). One entry signal in 4.8 hours. The 12-hour zero-signal rule is not met (the bot has not existed for 12 hours and it did signal once), so no threshold was relaxed. For scale: a round trip costs about 3% of a 0.5 SOL position (0.5% fee and 0.5% slippage each way, 0.002 SOL fixed each way, plus pool impact), so the +20% target nets about +17% and the -12% stop costs about -15%.

- Universe: `universe_ok` is 6 to 8 per run, and it was the same 8 tokens all session (mihao, FLOAT, Leonida, NIO, WEALTH, :3, paws, WASTED). `u:too_young` (about 18 per run) is the biggest block. In the latest snapshot 9 of those young tokens pass every other universe number (ages 0.2 to 2.0 days; the quote token is unknown), so the universe should grow by itself from tomorrow if they keep their liquidity.
- Entry: of 369 universe-token checks, `h1_weak` blocked 241 (65%), `buy_pressure` 46, `h6_down` 28, `volume_accel` 16, `h1_overheated` 13, `m5_dropping` 8, `h24_dumped` 3, and 13 were the held token; 1 signal. Only 33% of observations had a 1-hour change of +2% or more (median -1.2%) on an afternoon when SOL slid from $81.2 to $80.0. That is the filter working in a soft market, not a bug.
- Quote-token exclusion is bigger than it looked. Replaying the snapshots through the rulebook and matching the per-run funnel counts (an exact match on all 53 v2 runs) shows five tokens that pass every other universe filter are rejected on every run for their quote token: BIG, STANK, AMD, DacityCoin and CHOO. That is 5 of 13 otherwise-eligible tokens. Four of the five have pump.fun mint addresses, and such tokens normally trade against SOL (an inference, not confirmed). The bot judges each token by its deepest pool only, so a deeper pool quoted in TTWO, STONK, AMD, NVDAX or WBTC would hide an ordinary SOL pool. The repo data cannot show whether those SOL pools exist or how deep they are. In the replay CHOO met the entry rules 6 times and DacityCoin once, but on exotic-pool numbers, so that is only indicative.
- Hint from one open trade (n=1, not a finding): the WEALTH signal came from a single +5.4% five-minute candle in a thin token (125 trades and $14k volume in the hour, `volume_accel` 1.21 against a 1.2 bar). The 1-hour change had been -4.9% thirty minutes earlier. By 18:30 `volume_accel` was 0.44 and sells outnumbered buys.

**Changed.** Rulebook: nothing, v2 stays. Plumbing only, no version bump, no decision changed:

1. `data/debug/quote_reject_pairs.json`: for up to 8 quote-rejected tokens, once per token and one extra DexScreener call per cycle, the bot records every pool of that token (quote, liquidity, 24h volume, trades) and how many pairs the batch call returned for it.
2. Snapshot rows gain a 21st field, `quote_symbol`, so a review can replay the universe filter exactly instead of inferring it.

Test added: `test_quote_rejected_token_has_its_pools_recorded_once`. 18 tests pass.

**For the next review.**

- Read `data/debug/quote_reject_pairs.json`. If those tokens have a SOL, USDC or USDT pool that passes the universe thresholds by itself, pool selection is hiding eligible tokens: make `best_pairs` prefer the deepest allowed-quote pool (plumbing; no threshold or safety rule changes) and note the time it went live, because it changes which trades v2 takes. `pairs_in_batch` shows whether the batch call already returns those pools or a per-token lookup is needed. If their only real pools are the exotic ones, the exclusion is right and stays.
- If the first closed trades repeat the WEALTH pattern (the 5-minute move makes up most of the 1-hour move, low `txns_h1`), the entry section is the candidate, for example a higher `min_txns_h1`. Not before there are closed trades to show it.

**Would prove this review wrong.** Leaving the rules alone is wrong if, at the 24-hour mark (about 13:45 UTC on 14 Nov), `universe_ok` is still under 10 per run after the young tokens have aged in, or if 12 hours pass with cycles arriving and no signal: then relax one threshold as the review rules allow. The plumbing change is wrong if a `quote sample` error starts repeating in `data/runs`: remove it.

### v2, 2026-11-13: wider discovery (trading rules unchanged)

First live run (13:43 UTC) parsed the DexScreener API cleanly: no errors, SOL price derived, 158 of 160 discovered tokens returned data. Finding: DexScreener's boost, profile, takeover and meta feeds are a poor source for our universe. Of 160 tokens, 86 had under $30k liquidity, 66 were older than 35 days, 4 were under 3 days old, and only 1 was in the tradable band (it failed the buy-pressure test). At that rate 10 trades a day is impossible.

Change: added GeckoTerminal trending and most-traded Solana pools as a discovery source (pre-filtered to pools with at least $30k reserve and at most 35 days old). Prices and decisions still come from DexScreener.

Would prove it wrong: if after a day the tradable universe (funnel `universe_ok`) is still under about 10 tokens per run, discovery is still the bottleneck and needs another source. Second live run (13:52 UTC) confirmed GeckoTerminal parsing: 33 tokens discovered, tradable universe rose from 1 to 6, with 14 more under 3 days old waiting to age in. GeckoTerminal returned HTTP 429 on the 10th call, so calls are now spaced 6.5s and pages cut to 9 per cycle (plumbing fix, no version bump). Six tokens were rejected for an unlisted quote token; the funnel now records which. Third live run (14:18 UTC): GeckoTerminal still returned 429 on the 6th call at 6.5s spacing, so the bot now fetches 2 pages per cycle and rotates through 9 pages (each refreshed about every 25 minutes). The unlisted quote tokens were AMD, NVDAX, TTWO, STONK and WBTC (tokenized-stock and other exotic pairs): correctly excluded, no change. GitHub never started the 5-minute timer in 45 minutes. A long-running session design was tried and dropped at Ajeeb's request the same morning: the workflow is back to one short run per cycle, started by an external 5-minute scheduler calling GitHub's run-workflow API (reliable), with GitHub's own timer as a best-effort fallback; pushing a change to `.kick` also starts one run. Not yet verified live: RugCheck handling (only called when an entry signal fires; check `data/debug/rugcheck_sample.json` and run errors).

### v1, 2026-11-13: starting hypotheses

No data yet. Thresholds are guesses based on the agreed approach: established tokens (3 to 30 days), real liquidity, safety-screened, moderate momentum entries, tight risk per trade. First job of the first reviews is to confirm the bot's data plumbing against the live API, which could not be tested before launch.
