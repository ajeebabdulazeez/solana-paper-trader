# Lessons and rule changes

The running record of what paper results have shown and why each rulebook version exists. Newest first. Each review adds an entry; a rule only changes when the data here supports it.

## How to review (instructions for each review session)

1. Run `python3 -m bot.report` and read `data/STATUS.md` and the latest `data/runs/*.jsonl` errors.
2. First check the bot is healthy: runs arriving, no repeated errors, `batch_miss` low, signals appearing. Fix plumbing before judging strategy.
3. Judge the current rulebook version only on its own trades. Under about 30 closed trades, treat every pattern as a hint, not a finding.
4. Look for: which exit reasons lose the most, which entry features separate winners from losers, how much gain was left on the table, and which funnel stage blocks the most candidates. `python3 -m bot.replay` (add `--wide`, `--no-cooldown` or `--set entry.min_txns_h1=50`) replays the rules on the recorded snapshots, so you can look past the bot's own few trades and keep measuring entries a rule now blocks. Its output is a hint, never a finding; the limits are listed at the top of `bot/replay.py`. `python3 -m bot.replay --baseline` shows how a buy at every eligible cycle would have done, next to the cycles the entry rules pick: an entry idea is only worth a rule if its cycles clearly beat all cycles, across many tokens.
5. Change at most one rulebook section per review, bump `version`, and write the entry below: what the data showed, what changed, and what result would prove the change wrong.
6. Never loosen a safety rule to get more trades. Never tune to hit a return target.
7. Once a version looks good, stop changing it: the proof gate needs 100+ trades on one frozen version.
8. Keep the "Open tests" table below current: move a count when a trade moves it, strike a test when it is decided and say so in the entry. This file is too long to read in one session with the data (325 KB on 20 Nov). A review reads the table, the last two entries in full, and any entry the table points to for a test it is about to decide. A test is decided by the wording in the entry that set it, not by the table's summary of it.

## Open tests (as of the 06:30 UTC review on 23 Nov 2026)

Each line: what would change, where the test was set, the count now. "Real" means the bot's own closed trades.

| Section | Test, and what follows | Set in the entry of | Count now |
|---|---|---|---|
| entry | `min_volume_accel` 1.2 to 1.0 (carried once; the first test closed on 21 Nov level with the real trades) if the next 8 trades it adds hold 4 or more winners and average 3 points or more above the real trades opened over the same days. Added: in the replay with `--set entry.min_volume_accel=1.0`, opened after 22:30 on 21 Nov, on a token and cycle where the live replay opens nothing; a position open at the read counts at its mark. Dropped for good if the eight fall short on either count | 22:30, 21 Nov (first set 22:30, 18 Nov) | 3 of 8, none added since 17:50 on 22 Nov: Singularity `7R4MP...` 10:25 +34.50%, DIGS `9QT8K...` 12:00 -14.46%, Huss `CUg7A...` 17:50 -14.47% (on 22 Nov); 1 winner, +1.86% against -3.81% on the 7 real trades closed over the same days |
| universe | `min_age_days` 1 to 3 if one day's trades in the band 1 to 3 days old cost over 5% of equity, or after 15 closed trades in the band they lose more a trade than older tokens over the same days. (The first branch, two of the first five stops past -20% on price, closed unmet at 06:30 on 22 Nov: one of five) | 14:30, 17 Nov | 9 of 15 trades (chud `EV7J2...` 04:25 on 23 Nov, -16.92%, is the ninth), -4.11% against -1.54% on 21 older (window: opened from 16 Nov, as the earlier counts were made). 23 Nov's band trade cost 1.7% of equity |
| universe | The cap (150 times the pool) comes out if 3 of the first 5 tokens it blocks are still inside the other limits a day later with half their pool or more. To 250 if two blocked tokens between 150 and 250 would have been replay winners. To 120 if a token at 100 to 150 passes for an hour and its pool is gone within a day. "Not needed" if it blocks nothing more by 3 Dec | 06:30, 19 Nov | 0 of 2 blocked, none new (no `u:volume_to_liquidity` row since 14:30 on 22 Nov) |
| exit | The 5% trail goes back to 10% if over the first 10 trailing exits since 22:30 on 16 Nov the 10% trail does better by over 2 points a trade or on 5 of the 10. Within 1 point: leave the exit section alone for good | 22:30, 16 Nov | 9 of 10, unchanged (no trailing exit since BLOB/Singularity on 22 Nov): the 10% trail better on 2 and worse on 7; the 5% trail ahead by 5.4 points a trade, 0.8 without LEOSTAR. Only "5% ahead by over 1 point" (no change) or "within 1 point" (leave the exit section alone for good) can still come out of the tenth |
| discovery | `top_volume_pages` 8 to 4 if `api_calls` passes 55, GeckoTerminal 429s repeat, the watchlist sits at 300 while a token over the floor is dropped, or a token found only by `gecko:vol5` to `vol8` is bought and ends on `liquidity_drop` or a write-off | 22:30, 17 Nov | none met (`api_calls` 43 to 49 since 22:30 on 22 Nov; 22 Nov ended with three 429s; 23 Nov has one, tx p6 at 06:20; chud was found by `profiles_latest`) |
| code | The hidden-pool lookup (`refine_pools`, third case) is reverted if `pool lookup` errors repeat, `api_calls` passes 55, or a token is bought on an uncovered pool the batch call was right to call empty. Judged "not worth its code" on 26 Nov if it has only ever shown tokens gone within the hour | 22:30, 19 Nov | no error; 40 tokens shown (3 new, all under 0.2 days old). ANTx `XsYzw7...` (3.56 days, $96k raydium USDC) `u:volume_h24` on all 136 cycles. No trade on an uncovered pool |
| health | Tell Ajeeb if cycles are regularly over 15 minutes apart. Raise `max_single_lookups` if `batch_miss` less the never-seen tokens reaches 13 | every entry | gap 5.0 minutes, no cycle skipped since 02:45 on 21 Nov; about 4 (18 less 14 never-seen at 06:30 on 23 Nov) |

Decided, do not reopen without new grounds: the 12% stop against 16%, 20% and 30%, the break-even stop after +10%, the first target at 15% (exit tables of 16 Nov and 20 Nov); `m5_change_min_pct` at -5 (20 Nov); a cap on a 5-minute change of +10% (not carried, 20 Nov); the 300-trade floor back to 150 (20 Nov); the deeper GeckoTerminal pages (17 Nov); the band under a day old (the 1-day floor's forward check closed on 21 Nov: ten replay entries at -3.44% against the bot's own 14 at -1.71%, the tenth a stop 22.6 points past its level); the 300-trade floor's blocked band (2 winners in the five of 19 to 21 Nov, a line of 3); the minimum pool size (the 15 closed trades from v8 on had 9 stops at -14.7% on price at the stop cycle, against a line of -16%; closed 22 Nov); the rules as a whole against no rule (24 first signals on 8 tokens after 14:30 on 20 Nov at -0.14%, against -1.00% for every eligible cycle and -4.36% per token: neither worse nor 3 points better; closed 14:30, 22 Nov); a floor of +30% on the 6-hour change (`h6_change_min_pct` 0 to 30: at the tenth real entry under +30%, 2 winners and -3.43% a trade against +0.13% on the 10 at +30% or more, a gap of 3.6 points, short of 5; dropped for good at 06:30, 23 Nov; do not move the 30).

## Log

### v9, 2026-11-23 06:30 UTC review: no rule change, no code change (FLOAT and chud stopped at -16.49% and -16.92%; the 6-hour test reached its tenth entry and the +30% floor is dropped for good; v9 is 16 trades at -1.61%)

**Drawdown first: equity is 4.0163 SOL, -19.67%, nothing open.** It was 4.1241 SOL at 22:30. Above the 22% line (3.90 SOL) by 0.116 SOL, and 0.266 SOL above the proof gate's 25% line (3.75 SOL): about three ordinary stops (0.069 SOL each) with no winner between them. Max drawdown on closed trades unchanged at 23.12%. 23 Nov has used 1 of its 10 new trades (-0.0691 SOL, 1.7% of equity).

**Health.** 98 cycles since 22:30. Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 5.2. The newest cycle was 2.2 minutes old when the review started, so no `.kick` and no message to Ajeeb.

- Errors on 1 of 98 cycles: a GeckoTerminal 429 on `h24_tx_count_desc` p6 at 06:20. 22 Nov ended with three 429s (01:35, 20:20, 21:15), under the line of five, no page twice in a row.
- `api_calls` 43 to 49 (median 46), `batch_miss` 14 to 20 (median 18); at 06:30 it was 18 with 14 never-seen tokens on the watchlist, so about 4 known tokens missed, far under 13. Watchlist 241 to 279.
- RugCheck called once, parsed: chud `score_normalised` 1, no risks, LP locked 72.5%. The sample still matches `bot/rugcheck.py` (`score_normalised`, `risks[].level`, `lpLockedPct`). Never a `rugcheck_no_score` or `rugcheck_error` row.
- No `suspect_price`, `u:volume_to_liquidity`, `safety:*` or `skip:*` rows. Hidden-pool list: 40 tokens (3 new: cCAT, OpenIndex, ZOL, all under 0.2 days old, `u:too_young`); no `pool lookup` error; chud was not on an uncovered pool.
- No bug found, so no change to `bot/`. 47 tests pass.
- What I read: the "Open tests" table, the entries of 22:30 and 14:30 on 22 Nov in full, and the entry of 06:30 on 22 Nov for the wording at the tenth entry of the 6-hour test (quoted below).

**Strategy: v9 has 16 closed trades, 6 winners, -1.61% a trade, -0.1178 SOL. Sixteen trades are a hint, not a finding.** All versions: 46 closed, 14 wins, -4.58% a trade, -0.9837 SOL, profit factor 0.57.

| # | Token | Opened (UTC) | Age | Pool | Trades in the hour before | 1-hour change | 6-hour change | Volume against 6-hour avg | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 45 | FLOAT `Bv1a7...` | 18:50, 22 Nov | 24.86 days | raydium $396k | 465 | +9.7% | +27.2% | 3.10 | +13.5% | stop at 23:00, price -14.0% at the stop cycle (on time) | -16.49% |
| 46 | chud `EV7J2...` | 04:25, 23 Nov | 2.30 days | pumpswap $58k | 621 | +6.7% | +13.0% | 1.28 | +0.6% | stop at 04:55, price -14.1% at the stop cycle (on time) | -16.92% |

- FLOAT drifted between -4.7% and -6.3% from 20:55 to 22:45, then -7.9%, -11.4% and -14.0% on three cycles five minutes apart, the pool down with it ($352k to $335k). A clean stop 2 points past the level. It is the bot's fifth trade on FLOAT and the second stop.
- chud: found by `profiles_latest` on 21 Nov, the bot's first trade on it. Bought on a +5.4% candle's fade (the 5-minute change +0.3% at entry, the 24-hour change -19.3%), at volume 1.28 times its six-hour average, near the 1.2 floor. -1.7% at 04:50, -14.1% at 04:55 (a -10.1% five-minute candle), 2.1 points past the level on an on-time cycle. It went on to -36.6% by 06:05, so the stop saved about 20 points. Its pool ($58k) is the smallest at a v9 entry; one trade, no pattern.
- Signals: 1 in 8 hours, bought; the last 2.1 hours before the review, so the 12-hour rule is not near. Funnel since 22:30 (1,569 universe-token checks): `h1_weak` 982 (63%), `h6_down` 208, cooldown 167, `txns_h1` 149, `buy_pressure` 31, `h1_overheated` 11, held 10, `m5_dropping` 6, `volume_accel` 4, signal 1. `h1_weak` is the blocking stage again; no ground for a relaxation.
- Exit reasons, all versions: 28 stops -17.73% (-2.1927 SOL), 14 trailing exits +21.75% (+1.2916 SOL), 4 six-hour exits -4.77% (-0.0826 SOL). Both new stops filled about 2 points past the level on time: the ordinary five-minute gap, not late cycles. Left on the table: best 17.52% on average against -4.58% realised (both new trades had little to leave: +13.5% and +0.6% at best).
- Median splits (46 trades, hints): 6-hour change -10.65% / +1.48%; volume against its six-hour average -11.05% / +1.88%; market cap -9.27% / +0.10%; pool to market cap +1.33% / -10.50%. The same four; both new losses sit in the low half of the 6-hour change, chud in the low half of volume and market cap.
- `python3 -m bot.replay`: 42 closed on 23 tokens, 16 wins, -0.20%; it reproduces FLOAT (-16.34%) and chud (-16.79%) within 0.2 points. `--baseline` over the whole record: every eligible cycle -3.68% (38,014 on 65 tokens), cycles the rules passed -1.28% (193 on 23), first passing cycle -2.25% (103 on 23).

**The 6-hour test reached its tenth entry and closes: the +30% floor is dropped for good.** The wording fixed at 06:30 on 22 Nov, before the seventh trade: "at 10, the rule changes if 2 or fewer win and the gap is 5 points or more; otherwise the idea is dropped for good. No third carry." The 22:30 entry of 17 Nov set the groups: real entries opened after 22:30 on 17 Nov, under +30% against +30% or more.

- Under +30%, the ten: BAWSAQ, DIGS, NIO, HOGE, Rings, FIONA, DIGS, BLOB, FLOAT (ninth, -16.49%), chud (tenth, -16.92%): 2 winners, -3.43% a trade.
- +30% or more over the same days: 10, 5 winners, +0.13% (unchanged; no entry at +30% or more since DESSA).
- The gap is 3.6 points. 2 winners meets the first half; the gap is short of 5, so the rule does not change and the idea is dropped. Struck from the table and added to the decided line.
- What stands behind it, said once so a later review does not reopen it on the median split alone: across all 46 real trades the 6-hour split is still the widest on the record (-10.65% / +1.48%), but the forward test, which is the one written to decide it, went from a 12.8-point gap on 21 Nov to 3.6 points over its last five trades. The median split is mostly the trades before v8.

**The other counts.**

- Volume at 1.0: 3 of 8, unchanged; no added entry since Huss 17:50 on 22 Nov (the replay with `--set entry.min_volume_accel=1.0` opens nothing after 22:30 that the live replay does not). 1 winner, +1.86% against -3.81% on the 7 real trades closed since 22:30 on 21 Nov.
- Trail: 9 of 10, unchanged (both new exits were stops).
- Tokens 1 to 3 days old: 9 of 15 (chud), -4.11% against -1.54% on 21 older tokens opened over the same days (the window the earlier counts used: from 16 Nov). The band loses more a trade again, by more. 23 Nov's band trade cost 1.7% of equity, under the 5% day branch. Six more band trades decide it.
- Cap: nothing blocked. Discovery and the hidden-pool lookup: no condition met.

**Changed. No rule: rulebook v9 stays. No code change. In this file: the "Open tests" table is updated (the 6-hour row struck to the decided line).**

- Why no rule change. The one test that reached its count closed by its own wording on "no change". The others are short of their counts. Signals are arriving and the bot is healthy. v9 at 16 trades and -1.61% has fallen back below zero on two ordinary stops; that is what 16 trades do, and changing a section now would end the version with the most trades for no finding. The drawdown is closer to the gate's line (0.27 SOL), but the gate is a measurement, and steering trades to stay above it would be tuning toward a number.

**For the next review (14:30 UTC on 23 Nov).**

- First: cycles, errors, equity against 3.90 and 3.75 SOL (say so at the top if equity is under 3.90), the table.
- The next trailing exit is the tenth of the trail test; read it by the wording in the table.
- The next band trade (1 to 3 days old) is the tenth of 15.
- If no signal for 12 hours, rerun the relaxation table of 14:30 on 21 Nov before deciding.

**Would prove this review wrong.**

- Dropping the +30% floor is wrong only if the test was read off its own wording: the groups were counted from the journal (opened after 22:30 on 17 Nov, split at a 6-hour change of 30), and a miscount of one trade would not lift a 3.6-point gap to 5 unless it moved a loss of -16% or worse between groups. New grounds would be a new test written before its trades, not a reread of the median split.
- Leaving v9 alone is wrong if its next 14 trades take it under the record's -4.58% a trade; it should still reach 30 before an entry change is read on it.
- Reading both stops as the ordinary five-minute gap is wrong if the next stops on tokens over 3 days old keep filling 5 points or more past the level on on-time cycles (since 22:30 the one such stop, FLOAT, filled 2.0 points past). Three in the next ten would be new grounds.

### v9, 2026-11-22 22:30 UTC review: no rule change, no code change (DESSA stopped 5.7 points past its level on an on-time cycle; one signal in 8 hours; the 6-hour gap is down to 0.2 points; no test reached its count; v9 is 14 trades at +0.54%)

**Drawdown first: equity is 4.1241 SOL, -17.52%, FLOAT open at -5.9% on price.** It was 4.2222 SOL at 14:30. Lowest since 14:30: 4.1165. Above the 22% line (3.90 SOL) and 0.374 SOL above the proof gate's 25% line (3.75 SOL). Max drawdown on closed trades unchanged at 23.12%. 22 Nov has used 6 of its 10 new trades; its five closed trades made +0.0248 SOL.

**Health.** 99 cycles since 14:30. Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 5.2. The newest cycle was 1.7 minutes old when the review started, so no `.kick` and no message to Ajeeb.

- Errors on 2 of 99 cycles, both GeckoTerminal 429s on different lists and pages (`h24_tx_count_desc` p5 at 20:20, `h24_volume_usd_desc` p1 at 21:15). 22 Nov has three, under the line of five, and no page failed twice in a row.
- `api_calls` 41 to 48 (median 45), `batch_miss` 13 to 28 (median 19); at 22:30 it was 14 with 10 never-seen tokens on the watchlist, so about 4 known tokens missed, far under 13. Watchlist at most 275.
- RugCheck called once, parsed: FLOAT `score_normalised` 1, no risks, LP locked 75.2%. The sample still matches `bot/rugcheck.py` (`score_normalised`, `risks[].level`, `lpLockedPct`). Never a `rugcheck_no_score` or `rugcheck_error` row.
- No `suspect_price`, `u:volume_to_liquidity`, `safety:*` or `skip:*` rows.
- Hidden-pool list: 37 tokens. The first one between 1 and 30 days old: ANTx `XsYzw7...`, 3.23 days, a raydium USDC pool of $96k found at 19:25, judged `u:volume_h24` on all 39 cycles. It shows the lookup working on an old enough token; it was not bought, so the code row's revert conditions are not touched.
- No bug found, so no change to `bot/`. 47 tests pass.
- What I read: the "Open tests" table and the entries of 14:30 and 06:30 on 22 Nov in full. No test reached a count, so no older entry was needed.

**Strategy: v9 has 14 closed trades, 6 winners, +0.54% a trade, +0.0199 SOL. Fourteen trades are a hint, not a finding.** All versions: 44 closed, 14 wins, -4.03% a trade, -0.8461 SOL, profit factor 0.60.

| # | Token | Opened (UTC, 22 Nov) | Age | Trades in the hour before | 1-hour change | 6-hour change | Volume against 6-hour avg | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|---|---|
| 44 | DESSA `npz2F...` | 14:05 | 27.04 days | 1,317 | +23.6% | +51.2% | 3.65 | +17.7% | stop, price -17.7% at the stop cycle (14:45, on time) | -20.37% |
| 45 | FLOAT `Bv1a7...` | 18:50 | 24.86 days | 465 | +9.7% | +27.2% | 3.10 | +13.5% | open at -5.9%; the 6-hour limit is at 00:50 | |

- DESSA: a pumpswap pool of $171k, bought on a 5-minute candle of +9.2%. The next cycle read +17.7% (2.3 points short of the first target), then it gave all of it back: -5.3% at 14:20, -10.1% at 14:40 (inside the level), -17.7% at 14:45, then -12.4% at 14:50. Every cycle five minutes apart; a 7.6-point drop inside one five-minute gap. That is the known cost of one price every five minutes, not a late trigger, and on one trade it is no ground to look at the stop again (decided on 16 and 20 Nov).
- FLOAT: the bot's fourth trade on it (two trailing exits, one 6-hour exit before). A raydium pool of $396k, bought at +9.7% in the hour. Best +13.5% at 20:20, +10.1% at 20:25, then -4.5% at 20:30: the price fell 13.3% in one cycle with the pool down 14.7% ($413k to $352k), so price and pool moved together and it is a real sell, not a bad print. It has drifted between -4% and -8% since 20:55. It is the ninth entry under +30% in six hours.
- Signals: 1 in 8 hours, bought. The last was 3.7 hours before the review, so the 12-hour rule is not near. Funnel since 14:30 (1,709 universe-token checks): `h1_weak` 1,092 (64%), cooldown 249, `h6_down` 157, `txns_h1` 94, held 48, `buy_pressure` 35, `m5_dropping` 15, `volume_accel` 10, `h24_dumped` 7, `h1_overheated` 1, signal 1. `h1_weak` is the blocking stage, as on every review since 20 Nov; no ground for a relaxation.
- Exit reasons, all versions: 26 stops -17.80% (-2.0551 SOL), 14 trailing exits +21.75% (+1.2916 SOL), 4 six-hour exits -4.77% (-0.0826 SOL). Left on the table: best 18.0% on average against -4.03% realised.
- Median splits (44 trades, hints): 6-hour change -10.36% / +2.29%; volume against its six-hour average -10.78% / +2.72%; market cap -8.92% / +0.86%; pool to market cap +2.14% / -10.21%. The same four, a little narrower again. DESSA sat in the "good" half of three of them and lost 20%, which is what a median split on 44 trades across seven versions is worth.
- `python3 -m bot.replay`: 40 closed on 22 tokens, 16 wins, +0.62%; it reproduces DESSA at -20.25% (journal -20.37%). `--baseline` over the whole record: every eligible cycle -3.60% (36,580 on 65 tokens), cycles the rules passed -0.86% (188 on 22), first passing cycle -1.83% (100 on 22).

**The counts.**

- The 6-hour change: 8 of 10 under +30% unchanged (2 winners, -0.11%); FLOAT (+27.2%) is the ninth, open. The +30% group took DESSA (+51.2%, -20.37%): 10, 5 winners, +0.13%. The gap is 0.2 points (it was 2.5). For the rule to change at the tenth, both FLOAT and the next entry must lose and the under-30 group must end 5 points behind the other; at FLOAT's mark and an ordinary stop for the tenth it would be about 2.5 behind. A winner in either drops the idea for good.
- Volume at 1.0: 3 of 8 added (Huss `CUg7A...` 17:50 on 22 Nov, 6.02 days old, volume 1.19 times, a stop at -14.47%, is the third). 1 winner, +1.86% against +1.35% on the 5 real trades closed over the same days. It needs 3 winners in the next 5 to reach 4 of 8.
- Trail: 9 of 10, unchanged (DESSA was a stop).
- Tokens 1 to 3 days old: 8 of 15, -2.51%, against 20 older tokens over the same days at -0.79% (DESSA moved the older group).
- Cap: nothing blocked. Discovery and the hidden-pool lookup: no condition met.

**Changed. No rule: rulebook v9 stays. No code change. In this file: the "Open tests" table counts are updated.**

- Why no rule change. No test reached its count, signals are arriving, and the bot is healthy. v9 has 14 trades at +0.54%; a stop and an open position since 14:30 are ordinary trades and say nothing new. Changing a section now would end the version with the most trades on it for no finding.

**For the next review (06:30 UTC on 23 Nov).**

- First: cycles, errors (did 22 Nov end with more than five 429s), equity against 3.90 and 3.75 SOL, the table.
- Where FLOAT `Bv1a7...` 18:50 ends (by 00:50 at the latest): the ninth entry of the 6-hour test.
- The next trailing exit is the tenth of the trail test; read it by the wording in the table.
- ANTx `XsYzw7...` (uncovered pool, 3.23 days): if it ever passes the universe, check that its pool is the one traded before reading anything into a trade on it.
- If no signal for 12 hours, rerun the relaxation table of 14:30 on 21 Nov before deciding.

**Would prove this review wrong.**

- Leaving v9 alone is wrong if its next 16 trades take it under the record's -4.03% a trade; it should still reach 30 before an entry change is read on it.
- Reading DESSA's stop as the five-minute gap and not a reason to look at the stop is wrong if the next stops on tokens over 3 days old keep filling 5 points or more past the level on on-time cycles (DESSA is one; the stop cycles from v8 on averaged -14.7% on price at 06:30). Three in the next ten would be new grounds for the stop's gap cost, read with the 3-day floor's band.

### v9, 2026-11-22 14:30 UTC review: no rule change, no code change (BLOB +23.37% and Singularity +21.14% on the trail; the rules-against-no-rule test reached 8 tokens and closes in between; v9 is 13 trades at +2.15%)

**Drawdown first: equity is 4.2222 SOL, -15.56%, DESSA open at -4.3%.** It was 4.0828 SOL at 06:30. Lowest since 06:30: 4.0466. Above the 22% line (3.90 SOL) and 0.472 SOL above the proof gate's 25% line (3.75 SOL). Max drawdown on closed trades unchanged at 23.12%. 22 Nov has used 5 of its 10 new trades and the closed ones made +0.1112 SOL.

**Health.** 98 cycles since 06:30. Last 6 hours: 72 cycles, median gap 5.0 minutes, longest 5.2. The newest cycle was 1.5 minutes old when the review started, so no `.kick` and no message to Ajeeb.

- No error on any of the 98 cycles (22 Nov's only error is still the 429 at 01:35). `api_calls` 39 to 48 (median 45), `batch_miss` 13 to 21 (median 18); at 14:30 it was 13 with 10 never-seen tokens on the watchlist, so about 3 known tokens missed, far under 13.
- RugCheck called three times, all parsed: BLOB `score_normalised` 1, no risks, LP locked 100.0%; Singularity 1, no risks, 76.3%; DESSA 1, no risks, 100.0%. The sample still matches `bot/rugcheck.py` (`score_normalised`, `risks[].level`, `lpLockedPct`). Never a `rugcheck_no_score` or `rugcheck_error` row.
- No `suspect_price`, `u:volume_to_liquidity`, `safety:*` or `skip:*` rows. Hidden-pool list: 26 tokens, no new one between 1 and 30 days old, no `pool lookup` error. None of the three buys was on an uncovered pool.
- No bug found, so no change to `bot/`. 47 tests pass.
- What I read: the "Open tests" table, the entries of 06:30 on 22 Nov and 22:30 on 21 Nov in full, and the lines of the 14:30 entry of 20 Nov that set the rules-against-no-rule test (its wording is quoted below).

**Strategy: v9 has 13 closed trades, 6 winners, +2.15% a trade, +0.1063 SOL. Thirteen trades are a hint, not a finding.** All versions: 43 closed, 14 wins, -3.65% a trade, -0.7597 SOL, profit factor 0.63.

| # | Token | Opened (UTC, 22 Nov) | Age | Trades in the hour before | 1-hour change | 6-hour change | Volume against 6-hour avg | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|---|---|
| 41 | DIGS `9QT8K...` | 05:45 | 24.72 days | 1,187 | +9.8% | +8.5% | 3.34 | +5.6% | 6-hour limit | -3.45% |
| 42 | BLOB `8s11P...` | 07:15 | 21.65 days | 438 | +15.2% | +13.3% | 3.10 | +35.1% | half at the first target, the rest on the 5% trail at 07:57 | +23.37% |
| 43 | Singularity `7R4MP...` | 11:25 | 1.64 days | 831 | +22.0% | +34.9% | 1.75 | +37.8% | half at the first target, the rest on the 5% trail at 11:55 | +21.14% |
| 44 | DESSA `npz2F...` | 14:05 | 27.04 days | 1,317 | +23.6% | +51.2% | 3.65 | +17.7% | open at -4.3% | |

- BLOB is the second winner bought under +30% in six hours (Rings 21:20 on 21 Nov was the first). With a 10% trail the replay holds it to 09:15 and makes +36.22% (best +94.7%): the 5% trail sold the rest at 07:57, before the run went on to +94.7%.
- Singularity was 1.64 days old (the 3-day floor's band) and on an ordinary pool, not one of the uncovered `Singularity`/`Singularit` pools in the hidden list.
- Signals: 3 in 8 hours, all bought. Funnel since 06:30 (1,717 universe-token checks): `h1_weak` 1,051, `txns_h1` 195, cooldown 179, `h6_down` 97, `buy_pressure` 81, held 47, `h1_overheated` 32, `m5_dropping` 19, `volume_accel` 13, signal 3. No ground for a relaxation.
- Exit reasons, all versions: 25 stops -17.70% (-1.9687 SOL), 14 trailing exits +21.75% (+1.2916 SOL), 4 six-hour exits -4.77%. No stop since FIONA. Left on the table: best 18.0% on average against -3.65% realised.
- Median splits (43 trades, hints): 6-hour change -10.36% / +3.37%; volume against its six-hour average -10.78% / +3.82%; market cap -8.92% / +1.87%; pool to market cap +2.13% / -9.72%. The same four as at 06:30, a little narrower.
- `python3 -m bot.replay`: 39 closed on 21 tokens, 16 wins, +1.16%; it reproduces DIGS (-3.31%), BLOB (+23.65%) and Singularity (+21.37%) within 0.3 points.

**The rules against no rule reached their count and close in between.** The wording (14:30, 20 Nov): of the first 15 first signals in `--baseline` opened after 14:30 on 20 Nov (8 or more tokens), "if they average worse than every eligible cycle of the same days, the entry rules are worse than no rule on six days running and the entry section stops being tuned by thresholds until an idea clears the bar set above. If they average better by 3 points or more, the three days were three bad days and this entry made too much of them." The 22:30 entry of 21 Nov said it would be read on every first signal up to the one that brings the eighth token.

- The eighth token is BLOB at 07:15 on 22 Nov, the 24th first signal: 24 on 8 tokens, 9 winners, -0.14%. Every eligible cycle of the same days: -1.00% (8,554 on 29 tokens; -1.33% on 7,938 if cut at 07:15), -4.36% per token. A DIGS first signal at the same 07:15 makes it 25 at -0.81%.
- Better than every cycle by 0.9 to 1.2 points: not worse, so the "worse than no rule" branch is not met, and not 3 points, so neither is "three bad days". Per token the first signals are 4.2 points ahead, which is the only count that leans one way.
- What follows. The entry section stays open to tuning (the worse branch did not fire), and the bar for a new entry idea set on 20 Nov stands. The honest summary is that on this record the entry rules cannot be told from a buy at any moment by cycle; the lead, where there is one, is per token. Struck and added to the decided line.

**The other counts.**

- The 6-hour change: 8 of 10 real entries under +30% (DIGS 05:45 -3.45%, BLOB +23.37% are seven and eight): 2 winners, -0.11%. At +30% or more: 9, 5 winners, +2.41% (Singularity +34.9% joined it; DESSA +51.2% is open). Gap 2.5 points. A third winner in the next two drops the idea for good; it changes only if both lose and the gap reaches 5.
- Volume at 1.0: 2 of 8 added (Singularity 10:25 +34.50%, an hour before the live buy on the same run; DIGS 12:00 -14.46%, a stop). +10.02% against +6.78% on the four real trades closed over the same days. One winner of two, far from a count.
- Trail: 9 of 10. BLOB favours 10% by 12.6 points, Singularity favours 5% by 3.5 (+21.37% against +17.84%). 5% ahead by 5.4 points a trade; without LEOSTAR, 0.8. Only "no change" or "leave the exit section alone for good" can come out of the tenth.
- Tokens 1 to 3 days old: 8 of 15 (Singularity +21.14% is the eighth), -2.51% against +0.24% on 19 older tokens over the same days (it was -5.89% against -0.91%). The band still loses more a trade, by less.
- Cap: ANT `2Phhx...` never reached it. Its pool read $121k at 12:10 on 22 Nov and $0 at 12:15, at 0.69 days old with 24-hour volume about 250 times the pool: the seventh token of that shape, every one gone before it was a day old. Nothing blocked.
- Discovery and the hidden-pool lookup: no condition met.

**Changed. No rule: rulebook v9 stays. No code change. In this file: the "Open tests" table is updated (the rules-against-no-rule row struck to the decided line).**

- Why no rule change. The one test that reached its count closed in between, which by its own wording changes nothing. The others are short of their counts. v9 has 13 trades and is the first version above zero; it has not reached 30, let alone the 50 at which it would be frozen, and nothing in the record supports moving a threshold that would end it now. Two good trades are not a reason to change anything either.

**For the next review (22:30 UTC on 22 Nov).**

- First: cycles, errors, equity against 3.90 and 3.75 SOL, the table.
- Where DESSA `npz2F...` 14:05 ends: in the +30% group of the 6-hour test.
- The next entry under +30% in six hours is the ninth; the next trailing exit is the tenth of the trail test; read each by the wording in the table.
- If no signal for 12 hours, rerun the relaxation table of 14:30 on 21 Nov before deciding.

**Would prove this review wrong.**

- Closing the rules-against-no-rule test in between is wrong if a later reading of the same window finds the first signals worse than every eligible cycle (an off-by-one in which signal is the 24th would not do it: 25 at -0.81% is still ahead). It is also wrong if the 14:30 entry of 20 Nov meant "per token" as the comparison; then the first signals are 4.2 points ahead and "three bad days" was the verdict. I read "every eligible cycle" as by cycle, which is how the 20 Nov entry wrote its own numbers first.
- Leaving v9 alone is wrong if its next 17 trades take it under the record's -3.65% a trade; it should still reach 30 before an entry change is read on it.

### v9, 2026-11-22 06:30 UTC review: no rule change, no code change (FIONA stopped at -13.94%; three tests reached a count: the 6-hour change is carried to 10, the pool-size test and the first branch of the 3-day floor close unmet)

**Drawdown first: equity is 4.0828 SOL, -18.34%, DIGS open at +4.6%.** It was 4.1290 SOL at 22:30. Above the 22% line (3.90 SOL) and 0.333 SOL above the proof gate's 25% line (3.75 SOL). Max drawdown on closed trades unchanged at 23.12%.

**Health.** 98 cycles since the last review (22:30 to 06:30). Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 5.2. The newest cycle was 1.6 minutes old when the review started, so no `.kick` and no message to Ajeeb.

- Errors on 1 of 98 cycles: a GeckoTerminal 429 on the volume list's page 8 at 01:35. 21 Nov ended with three 429s (00:50, 05:15, 09:30), under the line of five.
- `api_calls` 44 to 50 (median 47), universe 15 to 19 tokens (median 17), watchlist 211 to 262. `batch_miss` 20 to 24 (median 22); at 06:30 it was 20 with 16 never-seen tokens on the watchlist, so about 4 known tokens missed, far under 13.
- RugCheck called twice, both parsed: FIONA `score_normalised` 1, no risks, LP locked 69.5%; DIGS 1, no risks, 98.0%. The sample still matches `bot/rugcheck.py`. Never a `rugcheck_no_score` or `rugcheck_error` row.
- The bad-print guard was asked once and was right: FIONA at 03:30 read +25.4% over the reading before ($0.002323 against $0.001853, pool "up" from $134k to $151k) on $2.8k traded in five minutes; the next cycle read $0.001802. Ignoring it changed nothing (no target was near).
- No `u:volume_to_liquidity`, `safety:*` or `skip:*` rows. Hidden-pool list: 25 tokens, all `u:too_young` or `watch_too_old`; no errors.
- No bug found, so no change to `bot/`. 47 tests pass.
- What I read: the "Open tests" table, the entries of 22:30 and 14:30 on 21 Nov in full, and the line of the 22:30 entry of 17 Nov that set the 6-hour test (its wording is quoted below).

**Strategy: v9 has 10 closed trades, 4 winners, -1.31% a trade, -0.0626 SOL. Ten trades are not a hint.** v8 and v9: 15 closed, 5 wins, -2.53%. All versions: 40 closed, 12 wins, -4.95% a trade, -0.9285 SOL.

| # | Token | Opened (UTC, 22 Nov) | Age | Trades in the hour before | 1-hour change | 6-hour change | Buy pressure | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|---|---|
| 40 | FIONA `B34nX...` (v9) | 01:00 | 2.17 days | 2,600 | +14.1% | +11.6% | 1.21 | +16.2% | stop, price -12.4% at the stop cycle (03:50, on time) | -13.94% |
| 41 | DIGS `9QT8K...` (v9) | 05:45 | 24.72 days | 1,187 | +9.8% | +8.5% | 1.39 | +4.8% | open at +4.6% | |

- FIONA: a pumpswap pool of $137k. It had run from $0.00166 at 00:00 to $0.00222 at 00:35 and was fading when bought (the 5-minute change -6.3% at 00:55, -0.2% at 01:00); buy pressure passed by 0.01. It reached +16.2% at 02:00, four points short of the first target, then drifted down and stopped at 03:50, only 0.4 points past the level. A clean stop, not a gap.
- Buy pressure at 1.21 to 1.24 (just over the 1.2 floor) on all real trades: 8, 3 winners, -0.33%, no worse than the record. Not a pattern.
- Signals: 2 in 8 hours. Funnel since 22:30: `h1_weak` 941, a token in its cooldown 234, `txns_h1` 197, `h6_down` 107, `buy_pressure` 70, `h1_overheated` 62, held 40, `m5_dropping` 16, `volume_accel` 15, signal 2. `h1_weak` is again the blocking stage; nothing calls for a relaxation.
- Exit reasons, all versions: 25 stops -17.70% a trade (-1.9687 SOL), 12 trailing exits +21.67% (+1.1087 SOL), 3 six-hour exits -5.20%. Left on the table: best 17.39% on average against -4.95% realised.
- Median splits (40 trades, hints): 6-hour change -12.39% / +2.48%; volume against its six-hour average -12.22% / +2.31%; market cap -10.70% / +0.79%; pool to market cap +2.21% / -12.11%.
- `python3 -m bot.replay`: 36 closed on 20 tokens, 14 wins, +0.10%; it reproduces FIONA at -13.80% and DIGS at 05:45.

**Three counts reached their end.**

1. **The 6-hour change is carried to 10.** The wording (22:30, 17 Nov): `h6_change_min_pct` goes to 30 "if of the next 6 closed entries with a 6-hour change under +30% ... one or none is a winner while the entries at +30% or more over the same days average at least 5 points better. The idea is wrong, and should be dropped for good, if 3 or more of those 6 win, or if the entries at +30% or more do no better than the others. In between, carry it to 10." FIONA (+11.6%) is the sixth. The six: BAWSAQ, DIGS, NIO, HOGE, Rings, FIONA: 1 winner, -3.47%. The other group: 8, 4 winners, +0.07%. The gap is 3.5 points: one winner, but short of 5, and the other group does better, so neither branch: carried to 10. The 17 Nov entry did not say how the tenth is read, so I fix it now, before the next trade, in proportion to the first: at 10, the rule changes if 2 or fewer win and the gap is 5 points or more; otherwise the idea is dropped for good. No third carry. On all real trades the split is 19 under +30% (1 winner, -12.18%) against 21 at +30% or more (11 winners, +1.59%), which is why the test is worth finishing, and the forward gap shrinking from 12.8 to 3.5 in two trades is why it is not yet a finding.
2. **The pool-size test closes unmet.** The 15 closed trades from v8 on have 9 stops at -14.7% on price at the stop cycle (FIONA -12.4% is the ninth), against a line of worse than -16%. Minimum pool size is not looked at; struck and added to the decided line.
3. **The 3-day floor's first branch closes unmet.** The five stops on tokens 1 to 3 days old are rockstar -14.5%, HOGE -15.4%, BAWSAQ -12.1%, Leonida -23.6%, FIONA -12.4% on price: one past -20%, the branch needed two. FIONA's day cost 1.4% of equity, not 5%. The 15-trade branch stays: 7 of 15 trades at -5.89% against 17 older tokens over the same days at -0.91%; at 15 it changes the floor if the band still loses more.

**The other counts.**

- Volume at 1.0: 0 of 8 added after 22:30 on 21 Nov. DIGS `9QT8K...` 17:00 on 21 Nov (the old window, for the record) ended on the six-hour limit at -10.67%; with it the old window's added trades are 8 at -0.62%, behind the real trades of those days (-0.36%), which supports not adopting 1.0 at 22:30.
- Rules against no rule: 19 first signals on 6 tokens (new: Rings 23:00 -14.88%, FIONA 01:00 -13.80%): +0.33%, against -1.91% by cycle and -6.68% per token. Not read until 8 tokens.
- Trail 7 of 10, unchanged (FIONA was a stop). Cap: nothing blocked; ANT `2Phhx...` turns a day old at about 19:35. Discovery: no condition met.

**Changed. No rule: rulebook v9 stays. No code change. In this file: the table is updated (the pool-size row struck to the decided line, the 3-day floor's first branch removed, the 6-hour row's count at 10 fixed).**

- Why no rule change. No test reached a "change" verdict: the 6-hour change carries by its own wording, the two closed tests closed unmet, and the rest are short of their counts. v9 has 10 trades; letting it reach 30 untouched is worth more than any threshold the record can currently support.

**For the next review (14:30 UTC on 22 Nov).**

- First: cycles, errors, equity against 3.90 and 3.75 SOL, the table.
- Where DIGS `9QT8K...` 05:45 ends: it is the seventh entry under +30% (6-hour test) and a first signal on a seventh token (rules against no rule).
- ANT `2Phhx...` at about 19:35 (cap), for the 22:30 review.
- If no signal for 12 hours, rerun the relaxation table of 14:30 on 21 Nov before deciding.

**Would prove this review wrong.**

- Carrying the 6-hour change is wrong if, at the tenth entry under +30%, 2 or fewer have won and the other group averages 5 points better: then 30 should have gone in now and the four trades in between cost what they cost. The rule then changes at that review. If 3 or more of the 10 win, or the gap is under 5, the idea is dropped for good and carrying it was right.
- Fixing the count at 10 myself is wrong if a later review finds the 17 Nov entry meant a different reading at 10; it should say so before the tenth trade, not after.
- Closing the pool-size test is wrong if the next stops from v8 on fill well past their level on deep-looking pools (RAMBO's -32% in the replay is the shape); that would be new grounds, read with the 3-day floor's band.

### v9, 2026-11-21 22:30 UTC review: no rule change, no code change (three winners in four trades on 21 Nov; Rings +42.26% is the best trade so far and the first winner bought under +30% in six hours; three tests read: the band under a day old stays out, the 300-trade floor's check is not reopened, volume at 1.0 is not adopted)

**Drawdown first: equity is 4.1290 SOL, -17.42%, nothing open.** It was 3.9719 SOL at 14:30. Above the 22% line (3.90 SOL) and 0.379 SOL above the proof gate's 25% line (3.75 SOL). Max drawdown on closed trades is unchanged at 23.12%. Three trades moved the figure; nothing was done to steer it.

**Health.** 2,435 cycles since launch, 775 on v9, 98 since the last review (14:35 to 22:30). Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 5.2.

- No cycle was skipped, so there is no message to Ajeeb. Two extra cycles (15:28:50, and 20:59:53, 38 seconds before the 21:00 one); nothing was held at either. The newest cycle was 1.9 minutes old when the review started, so no `.kick`.
- No error on any of the 98 cycles. 21 Nov has three GeckoTerminal 429s, the last at 09:30. The line set at 06:30 (more than 5 in the day, or one page failing twice in a row) is not met.
- `api_calls` 41 to 49 (median 46; the line is 55), `allowed_pool_used` 1 to 2, universe 14 to 18 tokens a cycle (median 15), `u:too_young` 12 to 22 (median 15), watchlist 180 to 259. No `safety:*`, `skip:*`, `suspect_price` or `u:volume_to_liquidity` rows.
- RugCheck was called three times and each answer parsed: SHIT `score_normalised` 30 with one risk at `warn` ("High holder correlation"), LP locked 99.4%; greg 1, no risks, 63.0%; Rings 1, no risks, 62.9% (it read 35.4% at 01:50). The saved sample still matches what `bot/rugcheck.py` reads (`score_normalised`, `risks[].level`, `lpLockedPct`). The record has never had a `rugcheck_no_score` or `rugcheck_error` row.
- SHIT's score of 30 is exactly the limit, and the rule refuses a score over 30, so it passed by the rule as written. It is the second buy with a risk on its report: Max, trade 14, had 29 and "Copycat token" at `warn` and lost 20.33%; SHIT won. Two trades say nothing, and the safety section is not a thing to tune on results either way. Recorded so that a later review can count how buys at 25 to 30 end.
- `batch_miss` 19 to 26 a cycle (median 23; it was 17), over the 15 single lookups on all 98. The rise is never-seen tokens (entries of the saved watchlist with no `last_ok`): 16 to 19, median 17. `batch_miss` less the never-seen tokens: 3 to 7, median 6. The line to act is 13. One known token went unpriced for long: DNET `93VXF...` on 29 cycles, a pool of $6k, under the watchlist's floor.
- The bad-print guard was asked once and answered rightly: Rings at 22:00 read 25.3% over the reading before, on $23.0k traded in the five minutes against about $9.2k needed to move a pool of $154k that far. The reading was acted on in the same cycle and the next one was higher.
- No bug found, so no change to `bot/`. 47 tests pass.
- The day: 21 Nov started at 3.9213 SOL, has used 4 of its 10 new trades and stands at +5.30%.
- What I read: the "Open tests" table, the entries of 14:30 and 06:30 on 21 Nov in full, the 22:30 entry of 18 Nov in full (it set the volume test), and the lines that set the four other tests this review reads or nears: the 1-day floor's forward check (14:30, 17 Nov), the blocked band (14:30 on 19 Nov and 06:30 on 20 Nov), the 6-hour change (22:30, 17 Nov) and the rules against no rule (14:30, 20 Nov). Not the whole file (404 KB).

**Strategy: v9 has 9 closed trades, 4 winners, +0.09% a trade, -0.0050 SOL. Nine trades are not a hint.** v8 and v9 as one series: 14 closed, 5 wins, -1.71% a trade, -0.1133 SOL. All versions: 39 closed, 12 wins on nine tokens, -4.72% a trade, -0.8710 SOL. SOL $70.1 to $70.7.

| # | Token | Opened (UTC, 21 Nov) | Age | Trades in the hour before | 1-hour change at entry | 6-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|---|
| 37 | SHIT (v9) | 16:20 | 3.70 days | 12,151 | +16.0% | +194% | +22.6% | half at the first target (+22.6% on price), the rest on the 5% trail (+15.7% on price) | +14.57% |
| 38 | greg (v9) | 17:00 | 10.61 days | 5,942 | +2.9% | +129% | +2.9% | stop, price at -14.2% | -16.96% |
| 39 | Rings (v9) | 21:20 | 11.09 days | 411 | +3.6% | +19.6% | +63.9% | half at +45.2% on price, the rest on the 5% trail (+48.2% on price) | +42.26% |

- SHIT, trade 37 (`Fn95N...`, found by `profiles_latest`, the bot's first trade on it; a pumpswap pool of $119k). Its 1-hour change read +102% to +144% from 15:30 to 15:55 and stayed over the 25% cap until 16:15; at 16:20 it read +16.0% with buy pressure 5.72 and the bot bought. The "fell into the band from above the cap" shape. Half sold at 17:05, the rest five minutes later, 0.8 points under the trail level. Fifty minutes after that the price was at +40.7% of the entry, and at 18:25 at -1.1%.
- greg, trade 38 (`4Ye6Y...`, found by `boosts_top` at 10:15 on 21 Nov; a pumpswap pool of $67k). The same shape and the other result: outside the universe until 15:45 (a pool under $50k), `h1_overheated` on every cycle from 15:45 to 16:55 (+177% at 16:20), then +2.9% at 17:00, 0.9 over the floor, with the last five minutes at +11.1%. The reading before the stop was -8.4% (17:55) and the stop cycle read -14.2%, 2.2 points past the level with the cycle on time; -21.5% twenty minutes later. The run it was bought after: the wide replay with the trade-count floor at 150 buys it at 13:50 on a $43k pool (outside the universe) and makes +75.26%, best +170.8%. The bot bought three hours later, at 2.3 times the 13:45 price, on the first reading under the cap.
- Rings, trade 39 (`65iH8...`, the fourth real trade on it: a stop and a trailing exit on 16 Nov, +12.90% at 01:50 today; a meteora pool of $143k). The cooldown ended at 14:05. `h1_weak` on every cycle from 20:45 to 21:15, then at 21:20: +3.6% in the hour, buy pressure 2.42, volume 2.21 times its six-hour average, 411 trades, +19.6% over six hours. For once a "moderate rise". +11.1% at 21:30, +19.5% at 21:50 (half a point short of the target), +15.8%, then +45.2% at 22:00, where half was sold, and +63.9% at 22:05. The rest went at 22:10 at +48.2%, 7.5 points under the trail level (+55.7%) with the cycle on time. At 22:30 the price was at +47.0%. With a 10% trail the replay sells at 22:15 for +38.33% against +42.60%.
- It is the largest gain on the record (JESTER's +30.76% was) and the first winner of 18 real entries bought under +30% in six hours. Rings is now three of the twelve winners.
- A line the 22:30 entry of 18 Nov wrote against itself: reading JESTER as one trade and not a turn "is wrong if v8's next 10 closed trades include 4 or more winners. Then the rules as they stand are better than this record shows, and the right response is still to leave them alone so the version can reach 30 trades". The ten trades since JESTER (30 to 39, v8 and v9 as one series) hold four winners and average -0.36%. Met, and the response it names is the one taken here.
- Three signals in the 8 hours (16:20, 17:00, 21:20), all bought; the last was 1.2 hours before the review. The 12-hour rule is not met and no threshold was relaxed.
- Funnel, 1,519 universe-token checks: `h1_weak` 940 (62%), `txns_h1` 205, a token in its cooldown 127, `h6_down` 68, `buy_pressure` 57, `h1_overheated` 56, the held token 29, `m5_dropping` 17, `volume_accel` 16, `h24_dumped` 1, signal 3. Twenty tokens were inside the universe; their median 1-hour change was 0.0% and 32% of readings were at +2% or better.
- Exit reasons, all versions: 24 stops, -17.86% a trade, -1.9111 SOL, the price at the stop cycle averaging -15.5%; twelve trailing exits +1.1087 SOL (+21.67% a trade); three 6-hour exits -0.0686. Stops still fill 2 to 4 points past the level on time: one price every five minutes, not late cycles.
- Left on the table: up 17.42% at the best on average, realised -4.72%. The seven trailing exits since the trail went to 5% gave back 10.4, 8.6, 11.1, 14.7, 8.5, 8.0 and 21.6 points from their best.
- Median splits (39 trades, hints): 6-hour change at entry -10.50% and +1.35%; volume against its six-hour average -12.22% and +3.17%; market cap -10.70% and +1.57%.

**Three tests reached their end. None changes a rule.**

1. **The band under a day old stays out (the 1-day floor's forward check, set at 14:30 on 17 Nov).** The wording: the floor "costs more than it saves if the next 10 replayed entries on tokens under a day old (lost positions counted at their last price) average better than the bot's own closed trades over the same days and no more than one of them ends worse than -25%".
   - The tenth entry is MAYA `FJKt1...` at 15:25 on 21 Nov: 10 hours old, found by `boosts_top` (the ordinary kind, never on an uncovered pool), a pool of $133k, 11,644 trades in the hour. It read -11.3% at 18:15, inside the stop level, and -34.6% at 18:20: a stop 22.6 points past the level with every cycle on time, -36.74% net.
   - The ten: 4 winners, -3.44% a trade, one worse than -25%. The bot's own closed trades over the same days: 14 at -1.71%. Not better, so the test is not met and the floor is not shown to cost more than it saves.
   - How close it was: an ordinary stop at -15% in tenth place would have met it (-1.27% against -1.71%). The verdict rests on which entry came tenth, and I take it as written, because fixing the count in advance is the point of the test. What stands behind it is steadier than one trade: the eleventh entry (RIEMANN `dkpuQ...` 15:28, stop, -16.03%) makes 11 at -4.58%; seven of the eleven are stops and they average -21.0% against -17.86% on the bot's own stops; and MAYA joins the two real stops of 17 Nov that put the floor in (-28.3% and -23.5% on price) and GTAVI in this check (-22.3%): four stops under a day old more than 10 points past the level.
   - The cautions the 14:30 entry of 20 Nov asked to be said with the reading: the replay has no RugCheck; the same days' real trades lost at any age; the two stops of 17 Nov are why the floor is there. All three lean the same way as the verdict.
   - The row is struck and the floor joins the decided list. New grounds would be a change in what the bot can see (a price more often than every five minutes), not more replay entries.
2. **The 300-trade floor's forward check is not reopened (set at 14:30 on 19 Nov).** It needed three winners in the next five entries in the band the floor blocks (wide replay, 150 to 299 trades, 3 to 30 days old). The five: FLOAT 14:00 on 20 Nov -14.76%, JESTER 07:00 -5.30%, RAMBO 07:40 +6.46%, greg `4Ye6Y...` 13:50 +75.26%, Max `5qaP7...` 18:30 on 21 Nov -14.73% (168 trades, a stop). Two winners, both outside the universe (RAMBO on its pool-to-market-cap test, greg on a $43k pool), one of them a cycle from a -34% stop. A sixth, WISHMAS 20:05, was a stop at -15.06%. The count is closed for good; the floor stays at 300.
3. **`min_volume_accel` at 1.0 is not adopted (set at 22:30 on 18 Nov; the window closed at this review).** The wording: 1.0 is a case "if, over the next three days, that setting adds three or more trades on three or more tokens and they average better than the live rules' trades over the same days".
   - Counted as the earlier entries counted it: seven closed added trades on five tokens, 2 winners, +0.82% a trade (HOGE -15.80%, Leonida 12:35 +23.31%, FLOAT -14.38%, DIGS 05:35 -5.64%, SHIT 14:55 -12.96%, Leonida 20:30 -15.74%, and the new one, SHIT 15:00 on 21 Nov at volume 1.13 times, +46.97%, best +99.3%). The real trades of the same days: 10, 4 winners, -0.36%.
   - **By the letter, on closed trades, the test is met**, by 1.2 points. The 14:30 entry said that not relaxing would then be wrong and 1.0 a candidate by its own test. I read it as a candidate and do not adopt it, for these reasons.
   - The margin is one trade and does not survive the close. The setting had a position open when the window shut: DIGS `9QT8K...` 17:00, at -9.3% with half an hour of its six left. Marked there, the added trades are 8 at -0.44%, behind the real ones. Counting DIGS 07:20 on 19 Nov as added too (the earlier entries called it the live 05:20 trade two hours late): 9 at -0.98%. Met or not met turns on bookkeeping, which means the two groups are level.
   - Five of the seven closed trades are losses and the median is -12.96%. Both winners are earlier entries on tokens the live rules bought within two hours anyway (Leonida at 14:15, SHIT at 16:20), so what the setting adds is an earlier buy on the same run, at the price of five stops and 6-hour exits elsewhere.
   - The bot's own trades lean the other way. By volume against the six-hour average at entry: 1.2 to 1.5, 13 trades, 2 winners, -11.57%; 1.5 to 2.0, 15, 5 winners, -5.23%; 2.0 to 3.0, 6, 2 winners, +2.88%; 3.0 or more, 5, 3 winners, +5.47%. The entries nearest the floor are the worst on the record, and 1.0 reaches further down. (Thirty-nine trades across seven versions: a hint, and not a case for raising the floor either.)
   - It would end v9 at nine trades, on the day the version first stands at break-even, for a setting whose forward window shows no difference.
   - The row is carried once, with a count and a margin the first test lacked: see the table and "Would prove this review wrong".

**The open counts.**

- The 6-hour change: 5 of the 6 real entries under +30%, and the fifth is the first winner (Rings 21:20, bought at +19.6%, +42.26%). The five: 1 winner, -1.37% (it was four at -12.28%). The other group took SHIT (+194%) and greg (+129%): 8, 4 winners, +0.07%. The gap is 1.4 points (it was 12.8). The sixth entry decides: a winner makes 2 of 6 and carries the test to 10; a loser leaves one winner, and the rule changes only if the gap is then 5 points, which an ordinary stop would not make it (about 3.7). On all real trades: under +30%, 18 on 12 tokens, 1 winner, -12.08%; +30% or more, 21 on 16 tokens, 11 winners, +1.59%. The baseline's first signals opened after 22:30 on 17 Nov, printed beside it as asked: under +30%, 14 on 7 tokens, 1 winner, -7.32%; +30% or more, 24 on 9 tokens, 9 winners, -3.57%. The 06:30 entry called this split the strongest pattern on the record and did not act on it because the test had fixed its own count. One trade took 11 of the 12.8 points away. Not acted on; the number stays at 30.
- The rules against no rule: the count of 15 first signals is reached, on 5 tokens of the 8 it needs (FLOAT four, Rings five, NVDA, SHIT three, greg two). The fifteen: 6 winners, -1.15%, against -1.04% by cycle (5,453 on 24 tokens) and -5.65% per token for every eligible cycle of the same days. With the caution of 22:30 on 20 Nov (opened six hours or more before the end of the record): 10 on 4 tokens at -2.47% against -1.45% by cycle and -4.47% per token. Level by cycle, ahead per token, and two more first signals (Rings 21:45 and 21:55, +29.46% and +22.83%) would turn the mean to +2.06%: five tokens decide nothing, which is why the test asks for eight. NVDA 14:05 closed in the replay at -2.57% on the 6-hour limit; the bot could not have bought it (RugCheck). Carried until the first signals cover 8 tokens. I will read it then on every first signal up to the one that brings the eighth token, since the first fifteen are already five tokens' worth; say so if a later review reads it differently.
- Over the whole record `--baseline` reads: every eligible cycle 31,661 on 60 tokens, -3.62%; cycles the rules passed 151 on 19, +1.48% (was +0.06% on 136); first passing cycle 82 on 19, 39% wins, -0.46% (was -1.50% on 73). Opened from 18 Nov on: every cycle -2.94% (17,179 on 36), first passing -4.96% (38 on 12 tokens, 10 wins; it was -8.97% on 29). The bot's own trades opened since 18 Nov: 13 closed, 5 winners, -0.48%.
- Trailing exits: 7 of 10. SHIT ends at +14.88% with the 5% trail against +9.84% with 10%, Rings 21:20 at +42.60% against +38.33%. The 10% trail is better on 1 of 7 (Rings 01:50) and worse on 6; 5% is ahead by 8.2 points a trade, 2.6 without LEOSTAR. The test's first branch (10% better on 5 of the 10) can no longer be met with three to go; the second (over 2 points a trade) would need the last three to favour 10% by about 26 points each.
- The pool-size test: 14 of 15 trades from v8 on, 8 stops averaging -15.0% on price. The next closed trade ends the count. It is met only if that trade is a stop past -24% on price.
- Tokens 1 to 3 days old: no new trade in the band. 4 of 5 stops, one past -20%; 6 of 15 trades at -4.55%, against 17 on older tokens over the same days at -0.91% (it was 14 at -3.95%).
- The cooldown: SHIT 18:10 in `--no-cooldown` ended on its stop, -19.86%. Ten cases for keeping it, one against.
- What the universe kept out since 14:30 (`--wide`): MAYA -36.74%, RIEMANN -16.03%, HUSS `3umHF...` -15.42%, DCTY `9hjBL...` -17.04% (32.6 days old), BANDANA -16.89%, BUCKME -16.67% (a $34k pool). Six closed, all stops, -19.80%. CATME `3iqoi...` (two hours old) left the record 15 minutes after its buy: its pool read $0 at 20:20.
- `python3 -m bot.replay`: 35 closed on 19 tokens, 14 wins, +0.49% (was 31, 12 wins, -0.67%). It reproduces trades 37, 38 and 39 within 0.4 points of the journal.

**The cap's neighbours, and pools that went.**

- No token was blocked. Median ratio inside the universe 3.5; the highest was 56, ANT `ANTBT...`, after the batch call's pool for it changed from a $365k pool to a $53k one at 15:20 with the price unchanged (a pool flip, not a drain).
- FIONA `B34nX...` at 20:50, the reading the table asked for: pool $118.6k (it was $112k a day earlier), ratio 28. It sat at 97 to 101 times for about half an hour on 20 Nov, never an hour over 100, and a day later its pool is larger. No case for moving the cap to 120.
- ANT `wzGUP...` (uncovered pool, 61 cycles, `u:too_young` on all): its pool read $0 at 18:50, at 8 hours old, with the ratio at 75 and climbing. It never reached the cap's test. A sixth of the kind, ANT `2Phhx...`, was found at 20:59 (1.4 hours old, a pool of $132k then and $116k at 22:30, 20 cycles, still followed); it would turn a day old at about 19:35 on 22 Nov.
- Uncovered pools: `data/debug/hidden_pool_tokens.json` names 18. New since 14:30: DCTY `ERtsR...` (12 cycles, $0 at 17:55), win `FRoxV...` (2), CLAUDIA `AmHUZ...` (6), Singularity `6aZEw...` (8), FIONA `26zq1...` (12, $0 at 21:50), ANT `2Phhx...` and Singularit `5nEAx...` (3 cycles, still followed). All one to three hours old, all `u:too_young`. Still none between 1 and 30 days old. No `pool lookup` or `hidden sample` error.
- Pools that go to $0 in one cycle: 20 in 8 hours (about 60 a day), twenty addresses under 14 names, pools of $106k to $224k, every one found by GeckoTerminal's most-traded-by-volume list (pages 3 to 8), every one under 8 hours old, none ever inside the universe. Five more readings fell under half without going to zero, on four pools (JENSEN `DkHsZ...` twice, XTO `9AEAH...` from $1.4M to $1k, ANTx, BIGFOOT); none was inside the universe. NVDA's reading fell from $380k to $81k at 16:40 with the price unchanged, a pool flip like ANT's.
- Discovery: the 20 tokens inside the universe came from `boosts_top` 5, `profiles_latest` 4, GeckoTerminal before pages were labelled 3, `gecko:tx6` 2, and one each from `gecko:trend1`, `gecko:trend2`, `gecko:tx4`, `gecko:vol7`, a trending meta and `takeovers_latest`. The three tokens bought came from `profiles_latest`, `boosts_top` and `gecko:trend2`. None of the conditions for reopening the pages is met.

**Changed. No rule: rulebook v9 stays. No code change. In this file: the "Open tests" table is brought up to date (two rows struck and moved to the decided line, the volume row replaced).**

- Why no rule change. v9 has nine closed trades. Of the three tests that ended, two said "leave it" by their own wording and the third made a candidate that the same window's evidence does not carry. No other test reached its count: the 6-hour change 5 of 6, the 3-day floor 4 of 5 stops, the trail 7 of 10, the pool-size test 14 of 15, the rules against no rule 15 on 5 tokens of 8. There were three signals in 8 hours, so the 12-hour rule gives no ground for a relaxation.
- Why a good day changes nothing. Four winners in the last five trades put v9 at +0.09% a trade and the day at +5.30%. That is one token's two runs and two others (FLOAT, SHIT); the record is still 39 trades, 12 winners, -4.72% a trade, no edge shown. The useful thing is that v9 is now the version with the most trades on it and the only one at break-even, which is a reason to let it run to 30, not a finding.
- What the day did show: how little this record can bear. In one afternoon a single trade (Rings) cut the strongest split on the record from 12.8 points to 1.4, a single replay entry (MAYA) turned a test that stood "met as it stands" into "not met", and a single replay entry (SHIT 15:00) turned the volume test the other way. Every one of those tests was read at the count fixed in advance, and that is the only reason the three verdicts do not contradict each other.

**For the next review (06:30 UTC on 22 Nov).**

- First: cycles, errors (did 21 Nov end with more than five 429s), equity against 3.90 and 3.75 SOL, and the "Open tests" table.
- The pool-size test ends with the next closed trade: the price at the stop cycle of the 9 stops if it is a stop (the line is an average worse than -16%).
- The 6-hour change: 5 of 6. The sixth entry under +30% is read by the wording of the 22:30 entry of 17 Nov; print the baseline row beside it.
- The rules against no rule: 5 tokens of 8. Count the tokens before reading the mean.
- The new volume row: 0 of 8. Where DIGS `9QT8K...` 17:00 ended (it belongs to the old window; for the record only).
- ANT `2Phhx...` at about 19:35 on 22 Nov: blocked by the cap or gone before. The next stop on a token 1 to 3 days old: its price at the stop cycle against -20%.
- If there is no signal for 12 hours, rerun the relaxation table of the 14:30 entry of 21 Nov before deciding; do not relax on the clock alone.
- Follow tokens by address, not by name.

**Would prove this review wrong.**

- Not adopting `min_volume_accel` 1.0 is wrong if the next 8 trades it adds hold 4 or more winners and average 3 points or more above the real trades opened over the same days. Added means: in `python3 -m bot.replay --set entry.min_volume_accel=1.0`, opened after 22:30 on 21 Nov, on a token and cycle where the live replay opens nothing; a position open at the read counts at its mark. Then 1.0 is that review's one change. If the eight fall short on either count, drop it for good.
- Keeping the band under a day old out is wrong by nothing this record can show: the forward check is closed. It would be reopened by a change in the bot (a faster price, or a stop that can fill between cycles), which is Ajeeb's call and not a threshold.
- Closing the blocked band at 2 of 5 has no further test: the check of 19 Nov was the test and it has been run. greg at 13:50 (+75.26% on 163 trades and a $43k pool) is the case a later idea about early entries would start from; it is one trade and it was outside the universe on pool size, not on trade count.
- Reading SHIT's RugCheck score of 30 as "the rule as written" is wrong if the rule was meant to refuse at 30. The code says over 30 and the README does not say; Ajeeb can settle it in one word, and tightening it would be his change to make, not a review's on two trades.
- Calling the day's result a good day and not a turn is wrong if v9's next ten trades hold four or more winners on four or more tokens. Then leave it alone all the same.
- Waiting on the 6-hour change, the trail, the 3-day floor, the cap, the pool-size test and the rules against no rule is wrong by the tests in the table, which are unchanged.

### v9, 2026-11-21 14:30 UTC review: no rule change, no code change (12 hours 15 minutes without a signal and no relaxation the record supports; the cap blocked its second token, whose pool was gone 35 minutes later; RugCheck refused NVDA)

**Drawdown first: equity is 3.9719 SOL, -20.56%, nothing open.** Unchanged since Rings was sold at 02:05: no trade in the 12.4 hours before this review. Above the 22% line (3.90 SOL) and 0.222 SOL above the proof gate's 25% line (3.75 SOL). Max drawdown on closed trades is unchanged at 23.12%.

**Health.** 2,337 cycles since launch, 677 on v9, 97 since the last review (06:35 to 14:30). Last 6 hours: 72 cycles, median gap 5.0 minutes, longest 5.2.

- No cycle was skipped, so 02:45 was a single skipped cycle, as the last entry read it, and there is no message to Ajeeb. One extra cycle (07:23:42, between 07:20 and 07:25; nothing held). The newest cycle was 2.0 minutes old when the review started, so no `.kick`.
- Errors on 1 of the 97 cycles: a GeckoTerminal 429 on the volume list's page 2 at 09:30, read at 09:35. That is three on 21 Nov so far (00:50, 05:15, 09:30), on three different pages, each read on the next cycle. The last entry's line is more than 5 in the day or one page failing twice in a row: not met.
- `api_calls` 42 to 47 (median 44; the line is 55), `allowed_pool_used` 2, universe 14 to 19 tokens a cycle, `u:too_young` 9 to 15 (median 12), watchlist 167 to 214. No `skip:*` or `suspect_price` rows.
- RugCheck was called once and the answer parsed: NVDA `NVDAV...` at 14:05, `score_normalised` 81 against a limit of 30, five risks (four at `danger`: mint authority, permanent control, freeze authority, low liquidity; one at `warn`), LP locked 0%. Refused as `safety:rugcheck_score`. That is the check doing its job on a tokenised share whose issuer can mint and freeze, not a parsing fault: the score was read as a number and the levels as levels. The saved sample still matches what `bot/rugcheck.py` reads (`score_normalised`, `risks[].level`, `lpLockedPct`). The record has never had a `rugcheck_no_score` or `rugcheck_error` row. Refusals so far: four cycles, on 19 Nov (14:35, 16:15, 16:30) and today; NVDA was also the first.
- `batch_miss` 15 to 20 a cycle (median 17), over the 15 single lookups on 95 of the 97. Never-seen tokens (entries of the saved watchlist with no `last_ok`): 12 to 17, median 15. `batch_miss` less the never-seen tokens: 1 to 6, median 3 (it was 2 to 9, median 7). The line to act is 13. One known token was unpriced on the newest cycle (ASTEROID `58kRy...`, a pool of $11k, under the watchlist's floor).
- No bug found, so no change to `bot/`. 47 tests pass.
- The day: 21 Nov started at 3.9213 SOL, has used 1 of its 10 new trades and stands at +1.29%.
- What I read: the "Open tests" table, the entries of 06:30 on 21 Nov and 22:30 on 20 Nov in full, and the lines of the 14:30 entry of 20 Nov that set the three cautions on the 1-day floor's forward check. Not the whole file (385 KB).

**Strategy: v9 has 6 closed trades, 2 winners, -6.50% a trade, -0.1621 SOL. No new trade; six trades are not a hint.** All versions: 36 closed, 10 wins on eight tokens, -6.22% a trade, -1.0281 SOL. SOL $65.8 to $70.6.

**Twelve hours without a signal, and why nothing was relaxed.** From Rings at 01:50 to NVDA at 14:05 the funnel shows no signal: 12 hours 15 minutes with every cycle arriving, the longest stretch since the 14 hours of 17 to 18 Nov. The entry of 14:30 on 19 Nov asks a review that counts such hours to say whether it counted NVDA: counted, the stretch ended at 14:05; not counted (RugCheck refuses it, so it can never be a trade), it is 12 hours 40 minutes and still running at 14:30. Over 12 hours either way. The task allows one modest relaxation as a hypothesis when that happens. I measured each candidate on the replay before deciding (added trades are those the relaxed rule makes that today's rules do not):

| One threshold relaxed | Added over the whole record | Added in these 12 hours |
|---|---|---|
| `h1_change_min_pct` 2 to 1 | 1 closed, -6.55% | NVDA 13:50, which RugCheck refuses |
| `min_buy_sell_ratio_h1` 1.2 to 1.1 | 21 on 14 tokens, 3 winners, -11.58% | Huss `CUg7A...` 10:35, stop, -18.35% |
| `min_txns_h1` 300 to 150 (decided on 20 Nov) | 17 on 13 tokens, 4 winners, -5.09% | JESTER `VAYMV...` 07:00, 6-hour exit, -5.30% |
| `h6_change_min_pct` 0 to -10 | 5 on 5 tokens, 1 winner, -4.67% | HOGE `FVzqG...` 02:55, 6-hour exit, +10.69% |
| `min_volume_accel` 1.2 to 1.0 (its own test closes tonight) | 10 on 7 tokens, 4 winners, +0.56%; the six since 22:30 on 18 Nov -6.87% | none |

- Every relaxation but one adds trades that lose more than the rules lose now, and the one that does not (volume) adds nothing in the quiet hours it would be meant to fill. So none was made. A relaxation is a hypothesis that more entries of today's kind are worth having, and the record says the opposite: the rules' first signals since 18 Nov average -8.97% (29 on 10 tokens).
- What the rules did pass in those hours. Rings at 13:30 (+4.5% in the hour, buy pressure 1.98; the cooldown kept the bot out until 14:05): in `--no-cooldown` it is a stop at -17.30%, 25 minutes later. NVDA at 14:05 (a tokenised share, on a Saturday; +2.1% in the hour, 0.1 over the floor, on 308 trades): refused by RugCheck, open at -3.3% in the replay.
- What the universe kept out in those hours (`--wide`): THUG 02:25 -12.63% (a $32k pool), DIGS 04:55 +7.33% ($46k), RAMBO 07:45 -33.88%, PUNANI 11:25 -18.30% (7 hours old). Four closed, one winner, -14.37%.
- RAMBO `KMifr...` is worth a line of its own. 17.7 days old, a pumpswap pool of $298k, followed since 13 Nov. Volume woke at 07:40, the price was +24% by 08:05, then -25.7% in one cycle at 08:20, -22.6% at 08:25, -39.5% at 08:55 and -89.4% at 09:25: 98% under its 08:05 high 80 minutes later, with the pool at $43k. The entry rules passed it at 07:45; the universe did not, on one test (pool at 2.3% of market cap against a floor of 3%). The replay's stop filled at -32.4% on price against a 12% level with every cycle on time. A deep pool on an old token is not protection, and the stop cannot be relied on to hold its level at any age.
- Funnel, 1,519 universe-token checks: `h1_weak` 901 (59%), `txns_h1` 237 (16%; it was 5% overnight), a token in its cooldown 136, `h6_down` 107, `h24_dumped` 59, `buy_pressure` 44, `h1_overheated` 25, `m5_dropping` 9, signal 1. Twenty tokens were inside the universe; their median 1-hour change was +0.5% and 36% of readings were at +2% or better (27% at 06:30). So prices were not flat: trading was thin (a Saturday morning), and the two tests that did the blocking after `h1_weak` are the trade-count floor and buy pressure, the two whose relaxations lose most in the table above.
- Exit reasons, all versions, unchanged: 23 stops, -17.90% a trade, -1.8429 SOL, the price at the stop cycle averaging -15.6%; ten trailing exits +0.8834 SOL (+20.32% a trade); three 6-hour exits -0.0686. Left on the table: up 16.39% at the best on average, realised -6.22%. Median splits (36 trades, hints): 6-hour change at entry -15.34% and +2.89%; volume against its six-hour average -12.00% and +0.24%.

**The open counts. None reached its end.**

- The cap, 0 of 2 blocked tokens still there a day later. ANT `DYDSu...` turned a day old between 10:10 and 10:15. `u:volume_to_liquidity` blocked it on six cycles, 10:15 to 10:40 (361 to 368 times its pool of $129k to $132k, 6,100 trades in every hour, buy pressure 1.10), and at 10:45 the pool read $0. It had been followed for 23 hours, on an uncovered pool until 10:05. Buy pressure (1.10 against 1.2) and volume (0.94 to 0.98 times its six-hour average against 1.2) would have refused it as well, as with the two ANTs before it, so the cap is still a second lock and has not yet been the only one.
- The rules against no rule: 8 of 15 first signals on 2 tokens of the 8 it needs. New: Rings 13:30, -17.30%. Mean -4.62%, against -2.98% by cycle (3,764 on 22 tokens) and -6.20% per token for every eligible cycle of the same days. With the caution of 22:30 on 20 Nov (cycles opened six hours or more before the end of the record): 7 first signals at -2.81% against -2.82% by cycle and -3.43% per token. NVDA 14:05 is a first signal on a third token and is open in the replay; `--baseline` has no RugCheck, so it will count when it closes, and the review that counts it should say the bot could not have bought it.
- Over the whole record `--baseline` reads: every eligible cycle 29,972 on 58 tokens, -4.01%; cycles the rules passed 136 on 17, +0.06% (was +0.30% on 134); first passing cycle 73 on 17, 37% wins, -1.50% (was -1.28% on 72). Opened from 18 Nov on: every cycle -3.62% (15,490 on 34), first passing -8.97% (29 on 10 tokens, 5 wins). The bot's own trades opened since 18 Nov: 10 closed, 3 winners, -4.62%.
- The 6-hour change: still 4 of the 6 real entries under +30%, no winner, -12.28%; the other group 6, 3 winners, +0.49%. The baseline's first signals opened after 22:30 on 17 Nov, printed beside it as asked: under +30%, 12 on 7 tokens, no winner, -11.88% (Rings 13:30 at +16.7% is the new one); +30% or more, 17 on 7 tokens, 5 winners, -6.92%. Not acted on; the number stays at 30.
- The 1-day floor's forward check: 9 of 10. New: PUNANI `2TngN...` 11:25, 7 hours old, a pool of $127k, 15,844 trades in the hour, stopped ten minutes later at -18.30% (-15.6% on price). The ordinary kind: found by `profiles_latest`, never on an uncovered pool. The nine: 4 winners, +0.26% a trade (it was +2.58% on eight), the worst -24.35%, none lost from the record; the bot's own trades over the same days are 11 at -5.80%. As it stands the test is met at the tenth entry unless that entry loses more than 60%. The review that reads it must go by the wording of the 14:30 entry of 17 Nov and say the three cautions with it: the replay has no RugCheck, the same days' real trades lost at any age, and the two stops of 17 Nov that filled at -28% and -24% on price are why the floor is there. A fourth from today: five of the nine are stops, and they average -18.8%.
- The 300-trade floor's blocked band (wide, 150 to 299 trades, 3 to 30 days old): 3 of 5 closed, 1 winner. New: JESTER `VAYMV...` 07:00 on 212 trades, 6-hour exit, -5.30% (inside the universe, so the floor is what blocked it); RAMBO `KMifr...` 07:40 on 230 trades, +6.46% (outside the universe; it sold half at +22.8% and the rest at -4.6% one cycle into the collapse above, and the same token bought five minutes later is the -33.88% stop: a winner by one cycle). greg `4Ye6Y...` 13:50 on 163 trades (a $43k pool) is open at -4.2%. Reopening needs 3 winners in the 5, so both of the last two.
- `min_volume_accel` at 1.0: no new added trade. Six added on five tokens, -6.87%, against the seven real trades of the same days at -6.20%. Not met as it stands; the 22:30 review today reads it at the close.
- The cooldown: Rings 13:30 in `--no-cooldown` ended on its stop, -17.30%. Nine cases for keeping it, one against.
- Unchanged, no new real trade: the trail (5 of 10; the 10% trail better on 1), tokens 1 to 3 days old (4 of 5 stops, one past -20%; 6 of 15 trades at -4.55% against 14 older at -3.95%), the pool-size test (11 of 15 trades, 7 stops at -15.1% on price).
- `python3 -m bot.replay`: 31 closed on 17 tokens, 12 wins, -0.67%, as at 06:30, with NVDA open.

**The cap's neighbours, and pools that went.**

- No token other than ANT `DYDSu...` was blocked. Median ratio inside the universe 4.2; the highest was FIONA `B34nX...` at 57.
- FIONA `B34nX...`: pool $103k and a ratio of 33 at 14:30, rejected on all 97 cycles (`h1_weak` 40, `h24_dumped` 34, `h1_overheated` 13, `h6_down` 10). Its pool at 20:50 today is the reading the table asks for.
- Leonida `9rbKk...`, the token the bot bought at 1.5 days old on 19 Nov (stop, -26.00%): its pool read $50k at 10:15 and $2.6k at 10:20, at 3.4 days old. It was inside the universe at 10:15 (rejected on `h1_weak`; before that on `h24_dumped`, with buy pressure of 0.70 to 0.85, so nowhere near a buy). Its pool had read $45k to $53k since 06:35, in and out of the universe across the $50k floor. After ANT `ANTBT...` on 20 Nov, today has the second and third pools to lose over half in one cycle while their token was inside the universe: RAMBO at 09:25 ($135k to $43k on a price fall of 89%, which is what a pool does when the price goes, with no sign of liquidity taken out) and Leonida, the first to lose nearly all of it. A note for the pool-size test, which reads at 15 trades.
- Uncovered pools: `data/debug/hidden_pool_tokens.json` names eleven. New: 蚂蚁 `GXD5D...` (an hour old, $104k to $120k, 14 cycles from 11:50, $0 at 13:00), XV `gEmvn...` (one cycle at 11:50, $0 at 11:55) and ANT `wzGUP...` (a fifth ANT of this kind, 3.6 hours old, a pool of about $141k to $143k, 9 cycles from 13:50, still followed; it would turn a day old at about 11:00 on 22 Nov). All `u:too_young`. Still none between 1 and 30 days old. `hidden_pool_checked` read 1 or more on 79 of the 97 cycles and 4 on one; no `pool lookup` or `hidden sample` error.
- Pools that go to $0 in one cycle: 21 in 8 hours (about 63 a day), 21 addresses under 14 names ("win" six times), pools of $103k to $227k; 20 found by GeckoTerminal's most-traded-by-volume list (pages 3 to 8) and one by `gecko:tx6` (STBL, $210k). ANT `DYDSu...` is the only one that had got as far as the universe's last test. Four more read under half without going to zero: Leonida and RAMBO (above), USOI `J7AKj...` ($543k to $1k at 09:35; 17 hours old, a market cap of $61M, 2,700 to 3,400 buys against 120 sells an hour, never inside the universe) and XV `AUuJP...` ($30k to $2k).
- Discovery: the 20 tokens inside the universe came from `profiles_latest` 5, GeckoTerminal before pages were labelled 4, `boosts_top` 3, `gecko:trend2` 2, `gecko:tx6` 2, and one each from `gecko:tx4`, `gecko:vol7`, a trending meta and `takeovers_latest`. None of the conditions for reopening the pages is met.

**Changed. No rule: rulebook v9 stays. No code change. In this file: the "Open tests" table is brought up to date.**

- Why no rule change. v9 has six closed trades and none since the last review. No test reached its count: the 6-hour change 4 of 6, the 3-day floor 4 of 5 stops, the 1-day floor's forward check 9 of 10, the trail 5 of 10, the pool-size test 11 of 15, the blocked band 3 of 5, the rules against no rule 8 of 15 on 2 tokens, and the volume test's window closes tonight.
- Why the 12-hour rule was not used. It permits a relaxation; it does not make one right. The table above is the evidence: on this record a looser entry buys more of what has been losing, and in these 12 hours it would have bought Huss into a stop or JESTER into a 6-hour exit. The hours were quiet because trading was thin, and the one thing the rules did pass on a token the bot could buy (Rings 13:30, kept out by the cooldown) was a stop. Twelve hours without a trade cost nothing; the entries a relaxation adds cost about 0.06 SOL a stop with equity 0.22 SOL above the gate's line. That last figure is not the reason (the rules give no licence to steer the drawdown), but it is what a wrong guess would cost.
- Why no universe change after RAMBO and Leonida. Both were kept out by tests that already exist, and one day's two tokens are not a count. They are recorded so that the pool-size test and any later look at `min_liq_to_mcap` start with them.

**For the next review (22:30 UTC on 21 Nov).**

- First: cycles, errors (count the 429s for the whole day against 5), equity against 3.90 and 3.75 SOL, and the "Open tests" table.
- `min_volume_accel` 1.0: read it at the close. Six added at -6.87% against seven real at -6.20% now; met only if the added trades average better. Whatever it says, write the verdict and strike or carry the row.
- FIONA `B34nX...`: its pool at 20:50 (the cap's test for 120). ANT `wzGUP...`: its pool, and its ratio.
- The 1-day floor's forward check: the tenth entry decides it. Read the 14:30 entry of 17 Nov for the wording before acting, and say the cautions.
- The rules against no rule: 8 of 15 on 2 tokens; NVDA when it closes. The blocked band: where greg `4Ye6Y...` ends. The 6-hour change: 4 of 6; print the baseline row beside it. The next stop on a token 1 to 3 days old: its price at the stop cycle against -20%.
- If there is again no signal for 12 hours, rerun the relaxation table before deciding; do not relax on the clock alone.
- Follow tokens by address, not by name.

**Would prove this review wrong.**

- Not relaxing is wrong if the volume test closes tonight with its added trades ahead of the real ones (then 1.0 is a candidate by its own test), or if the "rules against no rule" test ends with the first signals 3 points or more ahead of every eligible cycle on 8 or more tokens (then the rules were picking well and fewer of them was the cost). It is not proved wrong by a quiet day.
- Reading the relaxation table as evidence is wrong to the extent the replay is: no RugCheck, a few days of one market, and every variant tried on it is fitted to it. It shows which way each threshold leans, not what it would earn.
- Calling the three 429s "not repeating" is wrong if 21 Nov ends with more than 5, or a page fails on two cycles in a row. Then the discovery test is met and `top_volume_pages` goes to 4.
- Counting RAMBO 07:40 as the blocked band's winner is generous: it was outside the universe and one cycle from a -34% stop. If the band reaches 3 winners only with it, the review that reads it should say so before reopening anything.
- Waiting on the 6-hour change, the trail, the 3-day floor, the 1-day floor's forward check, the cap, the pool-size test and the rules against no rule is wrong by the tests in the table, which are unchanged.

### v9, 2026-11-21 06:30 UTC review: no rule change, no code change (Rings is v9's second winner, +12.90%; one cycle skipped at 02:45; no test reached its count)

**Drawdown first: equity is 3.9719 SOL, -20.56%, nothing open.** Above the 22% line (3.90 SOL) and 0.222 SOL above the proof gate's 25% line (3.75 SOL). Max drawdown on closed trades is unchanged at 23.12%. Two winners in a row moved the figure; nothing was done to steer it.

**Health.** 2,240 cycles since launch, 580 on v9, 96 since the last review (22:35 to 06:30). Last 6 hours: 71 cycles, median gap 5.0 minutes, longest 10.0.

- One cycle did not run: 02:45 on 21 Nov (02:40 to 02:50). Nothing was held (Rings had been sold at 02:05). It is the first skipped cycle since 16 Nov, so not "regular" and no message to Ajeeb. One extra cycle (00:17:55, between 00:15 and 00:20; nothing held). The newest cycle was 1.8 minutes old when the review started, so no `.kick`.
- Errors on 2 of the 96 cycles, both GeckoTerminal 429s: the volume list's page 5 at 00:50 and the trade-count list's page 4 at 05:15. Each page was read on the next cycle. The run records show 1 to 5 of these a day on every day from 13 to 19 Nov and none on 20 Nov. The discovery test says "429s start repeating"; I read that as a page failing on cycles in a row or a daily count that climbs, and neither is here. Say so if a later review reads it differently.
- `api_calls` 42 to 51 (median 47; the line is 55), `allowed_pool_used` 2, universe 14 to 17 tokens a cycle, `u:too_young` 9 to 15 (median 12), watchlist 191 to 233. No `safety:*`, `skip:*`, `suspect_price` or `u:volume_to_liquidity` rows.
- RugCheck was called once and the answer parsed: Rings `score_normalised` 1, no risks, LP locked 35.4%. The saved sample still matches what `bot/rugcheck.py` reads (`score_normalised`, `risks[].level`, `lpLockedPct`).
- `batch_miss` 14 to 20 a cycle (median 18), over the 15 single lookups on 85 of the 96. Never-seen tokens on the watchlist: 10 to 14 (median 12). `batch_miss` less the never-seen tokens: 2 to 9, median 7, as at 22:30. The line to act is 13. Seven tokens that had data before went cycles without a price (LUFFY, 旺旺, RUGGED, AI twice, FML, PGUY): every one was already under the watchlist's floor (pools of $0 to $10k), none came back, and with at most 9 known tokens missing the 15 lookups cannot have run out. Dead pools waiting for the 6-hour prune, not starved lookups.
- No bug found, so no change to `bot/`. 47 tests pass.
- The day: 21 Nov started at 3.9213 SOL, has used 1 of its 10 new trades and stands at +1.29%.
- What I read: the "Open tests" table and the entries of 22:30 and 14:30 on 20 Nov in full, as step 8 asks, plus the lines that set the trail test (22:30, 16 Nov) and the discovery test (22:30, 17 Nov). Not the whole file (371 KB). This entry is kept short for that reason.

**Strategy: v9 has 6 closed trades, 2 winners, -6.50% a trade, -0.1621 SOL. Six trades are not a hint.** v8 and v9 as one series: 11 closed, 3 wins, -5.80% a trade, -0.2704 SOL. All versions: 36 closed, 10 wins on eight tokens, -6.22% a trade, -1.0281 SOL. SOL $65.4 to $69.3.

| # | Token | Opened (UTC, 21 Nov) | Age | Trades in the hour before | 1-hour change at entry | 6-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|---|
| 36 | Rings (v9) | 01:50 | 10.28 days | 1,031 | +10.1% | +161.0% | +21.4% | half at the first target (+21.4% on price), the rest on the 5% trail (+12.2% on price) | +12.90% |

- Rings, trade 36 (`65iH8...`, found by `gecko:trend2`, the third real trade on it: a stop and a trailing exit on 16 Nov). A meteora pool against SOL of $118k; LP locked 35.4%, the first winner of five bought with under 50% locked (at 50% or more: 9 wins of 31).
- How the rules came to buy it. From 00:55 to 01:45 it was turned down on eleven cycles: buy pressure of 0.87 to 1.10 on eight, `m5_dropping` on two, `h1_overheated` on one. At 01:50 buy pressure read 1.21 against a floor of 1.2 and volume 1.28 times its six-hour average against 1.2. It passed two tests by a hair, inside a run of +161% in six hours. Like FLOAT, not a "moderate rise".
- After the buy: +8.0%, then +21.4% at 02:00 (half sold), then 7.6% under that high at 02:05 (the rest sold, 2.6 points under the trail level, cycle on time). Fifteen minutes in all. The price went on to +42% of the entry at 02:40 and was back at +8% by 03:55. A 10% trail would have sold at 02:50 for +19.44% against +13.23% in the replay.
- One signal since 22:30 (Rings), 4.5 hours after FLOAT and 4.7 hours before this review. The 12-hour rule is not met and no threshold was relaxed.
- Funnel, 1,522 universe-token checks: `h1_weak` 1,015 (67%), a token in its cooldown 149, `h6_down` 147, `txns_h1` 75, `h1_overheated` 49, `buy_pressure` 34, `volume_accel` 22, `m5_dropping` 15, `h24_dumped` 13, the held token 2, signal 1. Eighteen tokens were inside the universe; their median 1-hour change was -0.8% and 27% of readings were at +2% or better (36% at 22:30). A quiet night, not a blocked funnel.
- Exit reasons, all versions: 23 stops, -17.90% a trade, -1.8429 SOL, the price at the stop cycle averaging -15.6% (no new stop). Ten trailing exits made +0.8834 SOL (+20.32% a trade), the three 6-hour exits cost 0.0686.
- Left on the table: the average trade was up 16.39% at its best and realised -6.22%. The five trailing exits since the trail went to 5% gave back 10.4, 8.6, 11.1, 14.7 and 8.5 points from their best.
- Median splits in the report (36 trades, hints): 6-hour change at entry, low half -15.34%, high half +2.89%; volume against its six-hour average, -12.00% and +0.24%. All 10 winners were bought at +30% or more over six hours.

**The open counts. None reached its end.**

- The 6-hour change: still 4 of the 6 real entries under +30%, no winner, -12.28%. Rings was bought at +161% and joins the other group: 6, 3 winners, +0.49%. The gap is 12.8 points; the test needs two more entries under +30%. On all real trades: under +30%, 17 on 11 tokens, no winner, -15.28%; +30% or more, 19 on 14 tokens, 10 winners, +1.88%. The baseline's first signals opened after 22:30 on 17 Nov, printed beside it as asked: under +30%, 11 on 6 tokens, no winner, -11.39%; +30% or more, 17 on 7 tokens, 5 winners, -6.92%. Both groups still lose there. Not acted on; the number stays at 30.
- The rules against no rule: 7 of 15 first signals, on 2 tokens of the 8 it needs. FLOAT 21:20 +20.54%, 21:50 -21.37%, 22:25 -18.47%, 22:35 -16.90%; Rings 01:50 +13.23%, 02:10 +15.35%, 03:05 -12.06%. Mean -2.81%, against -3.76% by cycle (2,296 on 21 tokens) and -5.19% per token for every eligible cycle of the same days. With the 22:30 entry's caution (only cycles opened six hours before the end of the record): 4 first signals at -9.05% against -2.61% by cycle and -4.35% per token. The bot took only the first signal on each token and both won; four of the five repeat signals, which the open position or the cooldown kept the bot out of, were stops. Two tokens decide nothing.
- Over the whole record `--baseline` reads: every eligible cycle 28,520 on 57 tokens, -4.12%; cycles the rules passed 134 on 17, +0.30% (was +1.01% on 123); first passing cycle 72 on 17, 38% wins, -1.28% (was -0.79% on 66). The last row fell again with two real winners in it. Opened from 18 Nov on: every cycle -3.82% (14,038 on 33), first passing -8.68% (28 on 10 tokens, 5 wins). The bot's own trades opened since 18 Nov: 10 closed, 3 winners, -4.62%.
- `min_volume_accel` at 1.0: no new added trade. Six added on five tokens, -6.87%, against the seven real trades of the same days at -6.20%. As it stands the test is not met (the added trades are worse). The 22:30 review today reads it at the close.
- Trailing exits: Rings is the fifth of 10 (LEOSTAR, Leonida, JESTER, FLOAT, Rings). FLOAT ended under the 10% trail at 22:35 on 20 Nov at +19.06% against +20.54%. Rings is the first the 10% trail does better on, by 6.2 points. Count: 10% better on 1 of 5; the 5% trail ahead by 9.7 points a trade (20.1% against 10.4%), which is LEOSTAR's collapse, and by 1.5 points without it. The test needs 10% better on 5 of 10 or by over 2 points a trade.
- The cooldown: FLOAT 22:25 in `--no-cooldown` ended on its stop, -18.47%; Rings 02:10 made +15.35% and Rings 03:05 was stopped at -12.06%. Eight cases for keeping it, one against (Rings 02:10).
- Unchanged: the 300-trade floor's blocked band (1 of 5, no winner), the 1-day floor's forward check (8 of 10; the bot's own trades over the same days are now 11 at -5.80%), tokens 1 to 3 days old (4 of 5 stops; 6 of 15 trades at -4.55% against 14 on older tokens over the same days at -3.95%, -0.2410 SOL), the pool-size test (11 of 15 trades, 7 stops at -15.1% on price). RugCheck refusals: none new.
- `python3 -m bot.replay`: 31 closed on 17 tokens, 12 wins, -0.67% (was -1.14% on 30). With the cap removed it makes the same trades.

**The cap, and the tokens around it.**

- No token blocked. Median ratio inside the universe 4.4; the highest was FIONA `B34nX...` at 72.
- FIONA `B34nX...`: pool $87k at 06:30 (it was $106k at 23:25 and $69k at 04:25), ratio 54, price down 30% since 23:25 after falling 55%. Turned down on all 96 cycles (`h1_weak` 53, `h6_down` 25, `h1_overheated` 17, `m5_dropping` 1). Its pool at 20:50 today is the reading the table asks for.
- ANT `DYDSu...` (uncovered pool, 227 cycles, `u:too_young` on all): ratio 189 to 335 (321 now), pool $108k to $144k, 5,500 to 6,100 trades in every hour, buy pressure 1.04 to 1.11. It turns a day old at about 10:05 today; if the pool is there, `u:volume_to_liquidity` is expected and it is the cap's second blocked token.
- ANT `ANTBT...`: pool $345k to $442k, ratio 17 to 24, `h1_weak` on all 96 cycles, 80 to 700 trades an hour. Nothing to report.
- Uncovered pools: `data/debug/hidden_pool_tokens.json` names eight. New: 蚂蚁 `AogHm...` (an hour old, $110k to $129k, 17 cycles from 23:40, $0 at 01:00) and hSOL `he1iu...` (935 days old, a $1.4M raydium pool, `watch_too_old` on 4 cycles). Still none between 1 and 30 days old. `hidden_pool_checked` read 1 or more on all 96 cycles; no `pool lookup` or `hidden sample` error.
- Pools that go to $0 in one cycle: 20 in 8 hours (about 60 a day), twenty addresses under twelve names (PENNY four times, BABYDOG and Gestalt three each), pools of $66k to $225k, every one found by GeckoTerminal's most-traded-by-volume list (pages 2 to 8). None had been inside the universe. Seven more readings fell under half without going to zero, on six pools: five small `profiles_latest` pools (DCTY `7DQQe...` twice) and AODT (`gecko:tx6`, $78k to $1k). None was inside the universe.

**Changed. No rule: rulebook v9 stays. No code change. In this file: the "Open tests" table is brought up to date.**

- Why no rule change. v9 has six closed trades. No test reached its count: the 6-hour change 4 of 6, the 3-day floor 4 of 5 stops, the 1-day floor's forward check 8 of 10, the trail 5 of 10, the pool-size test 11 of 15, the rules against no rule 7 of 15 on 2 tokens, and the volume test's window closes tonight. The last signal was 4.7 hours before the review, so the 12-hour rule gives no ground for a relaxation.
- Why two winners change nothing. Both were bought at over +100% in six hours on readings that cleared a floor by a hair, both are in the group the record already favoured, and neither moves the count that test is waiting on (entries under +30%). The 6-hour split is now 0 winners of 17 against 10 of 19 on the bot's own trades, which is the strongest pattern on the record, and it is still not acted on: the test of 17 Nov fixed its own count so that it could not be read early on a good night, and the baseline's version of the same split has both sides losing.
- Why the trail stays at 5%. Rings is the first case for the 10% trail in five. One of five is the count, not the verdict.

**For the next review (22:30 UTC on 21 Nov).**

- First: cycles (was 02:45 a single skipped cycle or the first of more), errors (count the 429s for the whole day), equity against 3.90 and 3.75 SOL, and the "Open tests" table.
- `min_volume_accel` 1.0: read it at the close. Six added at -6.87% against seven real at -6.20% now; met only if the added trades average better.
- ANT `DYDSu...` from about 10:05: blocked by the cap or not, and its pool. FIONA `B34nX...`: its pool at 20:50.
- The rules against no rule: 7 of 15 on 2 tokens. It needs 8 tokens; do not read it on FLOAT and Rings alone.
- The 6-hour change: 4 of 6; print the baseline row beside it. The next stop on a token 1 to 3 days old: its price at the stop cycle against -20%.
- Follow tokens by address, not by name.

**Would prove this review wrong.**

- Calling the two 429s "not repeating" is wrong if 21 Nov ends with more than 5 (the most on any day so far), or a page fails on two cycles in a row. Then the discovery test is met and `top_volume_pages` goes to 4.
- Calling 02:45 a single skipped cycle is wrong if the next review finds two or more gaps over 7 minutes in its 8 hours. Then tell Ajeeb, with the typical gap.
- Reading the unpriced known tokens as dead pools is wrong if one of them, or any token that has had data, is priced again after cycles without a price while `batch_miss` less the never-seen tokens was at 13 or more.
- Not acting on the 6-hour split is wrong by the test in the table, which is unchanged: two more real entries under +30% decide it.
- Waiting on the trail, the 3-day floor, the 1-day floor's forward check, the cap, the pool-size test and the rules against no rule is wrong by the tests in the table, which are unchanged.

### v9, 2026-11-20 22:30 UTC review: no rule change, no code change (FLOAT is v9's first winner, +20.16%; equity back over the 22% line; no test reached its count)

**Drawdown first: equity is 3.9213 SOL, -21.57%, nothing open.** It is back above the 22% line (3.90 SOL) and 0.171 SOL above the proof gate's 25% line (3.75 SOL). The low on closed trades is unchanged (3.8438 SOL, max drawdown 23.12%); on the mark it was 3.8378 SOL at 21:30 with FLOAT held. One winner moved the figure; nothing was done to steer it.

**Health.** 2,144 cycles since launch, 484 on v9, 97 since the last review (14:35 to 22:30). Last 6 hours: 74 cycles, median gap 5.0 minutes, longest 5.2. No cycle was skipped, so no message to Ajeeb. One extra cycle (18:44:30, 47 seconds before the 18:45 cycle; both triggers fired; nothing was held). The newest cycle was 2.5 minutes old when the review started, so no `.kick`. No error in any of the 97 cycles. `api_calls` 43 to 51 (median 46; the line is 55), `allowed_pool_used` 1 or 2, universe 15 to 17 tokens a cycle, `u:too_young` 7 to 15 (median 11), watchlist 179 to 202. RugCheck was called once and the answer parsed: FLOAT `score_normalised` 1, no risks, LP locked 82.9%. The saved sample still matches what `bot/rugcheck.py` reads (`score_normalised`, `risks[].level`, `lpLockedPct`). No `safety:*`, `skip:*` or `suspect_price` rows. No bug found, so no change to `bot/`. 47 tests pass.

- `batch_miss` 16 to 23 a cycle (median 19; it was 14), over the 15 single lookups on all 97 cycles. Never-seen tokens on the watchlist: 11 to 15 (median 12, all from `profiles_latest`). `batch_miss` less the never-seen tokens: 4 to 9 (median 7; it was 0 to 5, median 3). The line is 15, act at 13. It has more than doubled in eight hours and is 4 short of the point to act. Every token that has ever had data was still priced on the newest cycle (184 of 184), because known tokens are looked up first, so nothing with a live pool went unpriced.
- The day: 20 Nov started at 4.0128 SOL, has used 3 of its 10 new trades and stands at -2.28% against the 10% limit.
- What I read: the "Open tests" table and the entries of 14:30 and 06:30 on 20 Nov in full, as step 8 asks. The file is 355 KB.

**Strategy: v9 has 5 closed trades, 1 winner, -10.39% a trade, -0.2127 SOL. Five trades are not a hint.** v8 and v9 as one series: 10 closed, 2 wins, -7.67% a trade, -0.3210 SOL. All versions: 35 closed, 9 wins on eight tokens, -6.77% a trade, -1.0787 SOL. SOL $67.3 to $71.4.

| # | Token | Opened (UTC, 20 Nov) | Age | Trades in the hour before | 1-hour change at entry | 6-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|---|
| 35 | FLOAT (v9) | 21:20 | 22.96 days | 3,157 | +2.2% | +112.0% | +34.9% | half at the first target (+31.0% on price), the rest on the 5% trail (+23.5% on price) | +20.16% |

- FLOAT, trade 35 (`Bv1a7...`, the fourth trade on it and its first winner: two stops on 13 and 14 Nov, a 6-hour exit on 17 Nov). A raydium pool against SOL of $330k, the deepest pool the bot has bought (the median entry pool is $96k); LP locked 82.9%; buy pressure 1.61; volume 4.42 times its six-hour average; up 151% on the day.
- How the rules came to buy it. From 20:30 to 21:10 every cycle read `h1_overheated` (1-hour change +33% to +72%) and 21:15 read `m5_dropping` (-9.1% in five minutes). At 21:20 the price was 10.6% under its 20:55 high and the 1-hour change read +2.15%, 0.15 over the floor, because the price an hour earlier had been a short spike. So the rules did not pick a "moderate rise": they bought a pullback inside a run of +112% in six hours, and only because of where the one-hour window happened to start. Worth knowing before this trade is counted as the rules working.
- After the buy: +4.6%, +0.6%, then +10.9% to +13.7% for twenty minutes, +31.0% at 21:55 in one cycle (half sold there, 11 points over the 20% target because the price jumped it between cycles), +34.9% at 22:05, -4.0% from the high at 22:10 (held, the trail is 5%), -8.4% from the high at 22:15 (sold, 3.6% under the trail level, cycle on time).
- One signal since 14:30 (FLOAT), 8.4 hours after the one before (Huss 12:55). The 12-hour rule is not met and no threshold was relaxed.
- Funnel, 1,535 universe-token checks: `h1_weak` 914 (60%), `h6_down` 166, `txns_h1` 147, a token in its cooldown 103, `h1_overheated` 56, `volume_accel` 56, `h24_dumped` 50, `buy_pressure` 21, `m5_dropping` 11, the held token 10, signal 1. Twenty-one different tokens were inside the universe; their median 1-hour change was -0.3% and 36% of readings were at +2% or better.
- Exit reasons, all versions: 23 stops, all lost, -17.90% a trade, -1.8429 SOL, the price at the stop cycle averaging -15.6% (no new stop). Nine trailing exits made +0.8328 SOL (+21.14% a trade), the three 6-hour exits cost 0.0686. From v8 on: 10 trades, 7 stops at -15.1% on price (the pool-size test reads it at 15).
- Left on the table: the average trade was up 16.25% at its best and realised -6.77%. FLOAT gave back 14.7 points from its best. The nine trailing exits average 22.2: 30.9 on the five sold under the 10% trail and 11.2 on the four since it went to 5% (10.4, 8.6, 11.1, 14.7). Different trades, so a hint; the trail's own test is the count below.
- Median splits in the report (35 trades, hints): 6-hour change at entry, low half -15.34%, high half +2.30%; volume against its six-hour average, -13.39% and +0.24%. Every one of the 9 winners was bought at +30% or more over six hours.
- LP locked: FLOAT 82.9%, won. Under 50%: 0 wins of 4. At 50% or more: 9 wins of 31.

**The open counts. None reached its end.**

- The 6-hour change: still 4 of the 6 real entries under +30%, no winner, -12.28%. FLOAT was bought at +112%, so it joins the other group: 5, 2 winners, -1.99% (HOGE, JESTER, Leonida, Huss, FLOAT). The gap is 10.3 points (it was 4.8); the test needs 5 at its end and two more entries under +30%. On all real trades: under +30%, 17 on 11 tokens, no winner, -15.28%; +30% or more, 18 on 14 tokens, 9 winners, +1.27%. The row to print beside it, the baseline's first signals opened after 22:30 on 17 Nov: under +30%, 11 on 6 tokens, no winner, -11.39%; +30% or more, 11 on 7 tokens, 3 winners, -7.04%. A gap of 4.4 points there, and both groups lose. Not acted on; the number stays at 30.
- The rules against no rule (set at 14:30): 1 of 15 first signals, on 1 token of the 8 it needs: FLOAT 21:20, +20.54% in the replay. A caution for whoever reads it at 15, not a change to the test: `--baseline` leaves out positions still open, so among cycles opened in the record's last six hours only the fast exits (stops and trails) are counted. Over the cycles opened since 14:30 that have closed it reads +2.31% by cycle (739 on 21 tokens; FLOAT's 88 cycles average +31.8%) and -4.02% per token. Read the comparison row only on cycles opened six hours or more before the end of the record, and per token.
- Over the whole record `--baseline` reads: every eligible cycle 26,947 on 57 tokens, -3.98% (was -4.23%); cycles the rules passed 123 on 17, +1.01% (was +1.31% on 117); first passing cycle 66 on 17, 38% wins, -0.79% (was -0.39% on 62). The last row fell again, with FLOAT in it: the other three new rows are first signals on Huss (13:20, 14:05 and 14:25, opened before the last review, all stopped by 14:55 at -15% to -17%), one token in the hour and a half after its real stop. Opened from 18 Nov on: every cycle -3.47% (12,465 on 33), first passing -9.22% (22 on 10 tokens, 3 wins). The bot's own trades opened since 18 Nov: 9 closed, 2 winners, -6.56%.
- `min_volume_accel` at 1.0 (window closes 22:30 on 21 Nov): two more added trades, both stops: SHIT `Fn95N...` 14:55 -12.96% (volume at 1.06 times) and Leonida `9rbKk...` 20:30 -15.74% (1.00). Six added on five tokens, -6.87% a trade (it was four at -3.13%), against the six real trades of the same days at -9.39%. Read it at the close; as it stands it would add trades that lose 7% each.
- The 300-trade floor's blocked band (wide, 150 to 299 trades): FLOAT 14:00 on 288 trades ended on its stop, -14.76%. 1 of 5 closed, no winner; reopening needs 3 winners in the 5. The same token was the real winner seven hours later on 3,157 trades.
- The cooldown: Huss 13:20 in `--no-cooldown` ended on its stop, -16.64% (best +11.9%). Six cases for keeping it, none against. FLOAT passed the rules again at 22:25, ten minutes after the trail sold it; that replay entry is open at -5.9% on price. Record how it ends.
- Trailing exits: FLOAT is the fourth of 10. With a 10% trail the second half was still held at 22:30 (trail level $0.004346, price $0.004432), marked level with the 5% trail's result (+20.6% against +20.5% in the replay). Not finished: record where the 10% trail sells it.
- The 1-day floor's forward check: 8 of 10, unchanged (no replay entry under a day old since SWJ 13:15). The bot's own trades over the same days: 10 at -7.67%.
- Tokens 1 to 3 days old: no new trade. 4 of 5 stops (one past -20% on price); 6 of 15 trades (2 wins, -4.55%) against 13 on older tokens over the same days (3 wins, -5.24%, -0.2916 SOL). The next stop in the band still decides the 3-day floor. In the band and inside the universe now: SHIT (2.95 days), Leonida (2.88), SWJ `gHZhq...` (1.31, pool $46k, under the floor), ANT `ANTBT...` (1.23), FIONA `B34nX...` (1.07).
- `python3 -m bot.replay` reproduces FLOAT at +20.54% against +20.16% in the journal (0.4 points: three fills, and the fixed fee weighs more on the bot's 0.38 SOL than on the replay's 0.5): 30 closed on 17 tokens, 11 wins, -1.14% (it was -1.88% on 29). With the cap removed it makes the same trades.
- RugCheck refusals: none new (three so far).

**The cap, and the tokens around it.**

- No token blocked (`u:volume_to_liquidity` 0 on all 97 cycles). Median ratio inside the universe 4.1.
- FIONA `B34nX...` (found by `profiles_latest`, pumpswap against SOL, pool $86k to $112k) turned a day old at 20:50 and is the first token inside the universe between 100 and 150 times: 97 to 109 on its first hour, at 100 or more on 4 cycles (20:55, 21:25, 21:30, 21:40), never an hour in a row, 76 at 22:30 as yesterday's volume leaves the 24-hour window. It is not the ANT kind: buys and sells are level, the price moves 10% a cycle, and it fell 30% in the hour after 21:00. Rejected on `h6_down` or `h1_weak` on all 21 cycles. The test for a cap of 120 wants "a token at 100 to 150 that passes for an hour and its pool gone within a day": the first half is not met. Watch its pool to 20:50 on 21 Nov all the same.
- ANT `DYDSu...` (followed on an uncovered pool, 131 cycles, `u:too_young` on all): the ratio went from 67 to 191. It passed 100 at 16:20 (pool $144k to $111k, price +1.4%) and 150 at 19:55 ($142k to $110k, price +0.8%): liquidity taken out each time, as with the three before it. It turns a day old at about 10:05 on 21 Nov; if the pool is still there, `u:volume_to_liquidity` is expected and it is the cap's second blocked token.
- ANT `ANTBT...` (raydium against USDC) turned a day old at 17:00 and has been inside the universe on 68 cycles. Two cycles later, at 17:10, its pool read $313k after $1.46M with the price down 0.3%: four fifths of the liquidity taken out in one cycle of a token the universe had just let in. Ratio 53 at most, 24 now. `h1_weak` 54, `h6_down` 10, `volume_accel` 3, `buy_pressure` 1; never a signal. Had it been held, the liquidity rule would have sold it that cycle at about the same price. Noted because on the snapshots since 17 Nov it is the only pool to lose over half in one cycle while its token was inside the universe (today's rules).
- Tokens followed on an uncovered pool: `data/debug/hidden_pool_tokens.json` names six. New: DCTY `BijBW...`, an hour old, $110k to $126k, 14 cycles from 20:50 to 21:55, $0 at 22:00, `u:too_young` throughout. None between 1 and 30 days old. `hidden_pool_checked` read 1 or more on all 97 cycles and 4 on seventeen; no `pool lookup` or `hidden sample` error.
- Pools that go to $0 in one cycle (walked from the 98 versions of `data/state/watchlist.json` since 14:30): 14 in 8 hours, about 42 a day (it was 60). Fourteen addresses under twelve names (DCTY and HANDLE twice), pools of $80k to $205k, every one found by GeckoTerminal's most-traded-by-volume list (pages 2 and 4 to 8). None had passed the universe. Six more read under half without going to zero: ANT `ANTBT...` (above), LOOSY `HF2RB...` ($108k to $34k at 18:25; the replay's under-a-day winner of 11:20), and four small `profiles_latest` pools.
- Discovery: the 21 tokens inside the universe came from `profiles_latest` 6, GeckoTerminal before pages were labelled 4 (FLOAT among them), `boosts_top` 3, `gecko:trend2` 2, `gecko:tx6` 2, and one each from a trending meta, `gecko:tx4`, `gecko:vol7` and `takeovers_latest`. No 429. None of the conditions for reopening the pages is met.

**Changed. No rule: rulebook v9 stays. No code change. In this file: the "Open tests" table is brought up to date.**

- Why no rule change. v9 has five closed trades. No test reached its count: the 6-hour change 4 of 6, the 3-day floor 4 of 5 stops, the 1-day floor's forward check 8 of 10, the trail 4 of 10, the pool-size test 10 of 15, the rules against no rule 1 of 15, and the volume test's window closes tomorrow. The last signal was 70 minutes before the review, so the 12-hour rule gives no ground for a relaxation.
- Why the winner changes nothing. One trade, on a token that had lost three times, bought on a reading that passed the 1-hour floor by 0.15 points. It is in the group the record already favoured (a strong six hours) and it does not move the count of the test on that group, which is waiting for entries on the other side. The numbers that matter are the same as at 14:30: no version has shown an edge, and the first passing cycle of the entry rules on the whole record is at -0.79%.
- Why `max_single_lookups` was not raised. The line to act is 13 and the figure peaked at 9. Raising it is a discovery change and would use this review's one section on a number that has not reached its line. If it gets there, raise it to 20 (5 more calls a cycle at most; `api_calls` peaks at 51 against a line of 55, so check that first).

**For the next review.**

- First: cycles, errors, equity against 3.90 and 3.75 SOL, and the "Open tests" table.
- `batch_miss` less the never-seen tokens: 4 to 9 now. At 13, act as written above.
- ANT `DYDSu...` at about 10:05 on 21 Nov: is it blocked by the cap, and is its pool there. FIONA `B34nX...`: its pool at 20:50 on 21 Nov. ANT `ANTBT...`: its pool, and anything the entry rules say.
- Where FLOAT ends under the 10% trail (the fourth of 10) and in `--no-cooldown` (22:25).
- `min_volume_accel` 1.0: the 22:30 review on 21 Nov reads it at the close. Six added at -6.87% now.
- The rules against no rule: 1 of 15. Read the comparison row with the caution above.
- The 6-hour change: 4 of 6; print the baseline row beside it. The next stop on a token 1 to 3 days old: its price at the stop cycle against -20%. The 1-day floor's forward check: 8 of 10, with the three cautions of the 14:30 entry.
- Follow tokens by address, not by name.

**Would prove this review wrong.**

- Reading FLOAT as one trade and not as the rules working is wrong if the "rules against no rule" test ends with the first signals 3 points or more ahead of every eligible cycle of the same days, on 8 or more tokens. Then 18 to 20 Nov were three bad days, as the 14:30 entry allowed.
- Not raising `max_single_lookups` is wrong if a token that has had data before goes a cycle without a price while the lookups are spent on never-seen tokens (the code looks up known tokens first, so this needs the figure to pass 15), or if the figure reaches 13 and the next review does not act.
- The caution on the comparison row is wrong if it is used to move the test's count or its 3-point line. It says which cycles to compare, nothing else.
- Waiting on the 6-hour change, the 3-day floor, the 1-day floor's forward check, the trail, the cap and the volume test is wrong by the tests in the table, which are unchanged.
- The health verdict is wrong if the gap between cycles grows past 15 minutes or skipped cycles become regular.

### v9, 2026-11-20 14:30 UTC review: no rule change, no code change (drawdown past the 22% line; the week-of-data tests are read: the 12% stop stays; since 18 Nov the entry rules pick worse moments than no rule)

**Drawdown first, as the last two entries asked: equity is 3.8438 SOL, -23.12%, under the 22% line (3.90 SOL), and nothing is open.** HOGE and Huss were both stopped since 06:30. The proof gate's line is 25%, 3.75 SOL: 0.094 SOL away. A stop now costs about 0.062 SOL (a position is 10% of equity), so one more does not cross it and two with no winner between them do. My reading of the gate: it judges one frozen version on its own trades, and no version is frozen, so crossing 25% closes nothing by itself. It is still a quarter of the paper stake gone in a week with no edge shown. The rules give no licence to steer the number with sizes or stops, and this review did not.

**Health.** 2,047 cycles since launch, 387 on v9, 98 since the last review (06:30 to 14:30). Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 5.2. No cycle was skipped, so no message to Ajeeb. One extra cycle (10:30:44, 35 seconds after the cycle that stopped HOGE; nothing was held by then and it changed nothing). The newest cycle was 2.0 minutes old when the review started, so no `.kick`. No error in any of the 98 cycles. `api_calls` 41 to 51 (median 46; the line is 55), `allowed_pool_used` 1, universe 14 to 16 tokens a cycle, `u:too_young` 10 to 16 (median 12), watchlist 184 to 220. RugCheck was called once and the answer parsed: Huss `score_normalised` 1, no risks, LP locked 91.7%. The saved sample still matches what `bot/rugcheck.py` reads (`score_normalised`, `risks[].level`, `lpLockedPct`). No `safety:*`, `skip:*` or `suspect_price` rows. No bug found, so no change to `bot/`. 47 tests pass.

- `batch_miss` 11 to 18 a cycle (median 14), over the 15 single lookups on 21 of the 98. Never-seen tokens on the watchlist: 10 to 13 (median 11, all from `profiles_latest`). `batch_miss` less the never-seen tokens: 0 to 5 (median 3; it was 4 to 6), the line is 15, act at 13.
- The day: 20 Nov started at 4.0128 SOL, has used 2 of its 10 new trades and stands at -4.21% against the 10% limit.
- What I read: the entries of 06:30 on 20 Nov, 22:30 on 19 Nov and 22:30 on 17 Nov in full, and the "Would prove this review wrong" list of every entry back to 13 Nov. Not the whole file: it is 325 KB. That is the third review to say so, so this one adds the "Open tests" table above and step 8 of "How to review". The table was built from those lists; where it and an entry differ, the entry is right.

**Strategy: v9 has 4 closed trades, all stops (-18.02% a trade, -0.2902 SOL). Four trades are not a hint.** v8 and v9 as one series: 9 closed, 1 win, -10.77% a trade, -0.3985 SOL. All versions: 34 closed, 8 wins on seven tokens, -7.56% a trade, -1.1562 SOL, max drawdown 23.12%. SOL $70.7 to $72.8.

| # | Token | Opened (UTC, 20 Nov) | Age | Trades in the hour before | 1-hour change at entry | 6-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|---|
| 33 | HOGE (v9) | 06:25 | 4.98 days | 371 | +9.9% | +14.5% | +18.4% | stop, price at -13.0% | -15.04% |
| 34 | Huss (v9) | 12:55 | 3.81 days | 833 | +7.0% | +33.4% | 0.0% | stop, price at -13.7% | -16.39% |

- HOGE, trade 33 (`FVzqG...`, now 1 win and 3 stops on this token). +17.3% at 07:30 and +18.4% at its best, 1.6 points short of the first target; between +3% and +15% for the next two and a half hours while trades in the hour fell from 408 to 61; then -4.7% at 10:15, -11.9% at 10:20 on $9.3k traded in five minutes, and -13.0% at 10:30, 1.0 point past the stop with the cycle on time. Afterwards: -21.1% at 12:05, -1.2% at 12:55, -12% at 14:25. The stop was neither clearly right nor clearly wrong. It is the ninth loser that was up 10% or more first.
- Huss, trade 34 (`CUg7A...`, found by `gecko:trend2`, a pumpswap pool against SOL of $52.5k, $2.5k over the universe's floor; LP locked 91.7%; up 317% on the day). At 12:45 the price was 8.3% above the later entry with the 1-hour change at +21%. It fell 8% in the next cycle, and the bot bought on the cycle after that, when the 5-minute change read -1.4% (the floor is -3) and the 1-hour change +7.0%. -6.4% on the next cycle and -13.7% at 13:10, fifteen minutes after the buy, 1.7 points past the stop. Ten minutes after the stop it was at -4.0%, at +2.6% by 13:25, and it has moved between -14.5% and +7.4% of the entry since. A $50k pool moves 6% on $9k of trades, so for this token a 12% stop is inside an hour's noise. NIO (01:05), Leonida (15:15 on 19 Nov) and now Huss were all back within a few points of the entry soon after their stops. That is the question the exit table below answers.
- One signal since 06:30 (Huss), 1.6 hours before the review; the one before was HOGE at 06:25. The 12-hour rule is not met and no threshold was relaxed.
- Funnel, 1,487 universe-token checks: `h1_weak` 781 (53%), `txns_h1` 253, a token in its cooldown 143, `h6_down` 141, the held token 50, `buy_pressure` 32, `h1_overheated` 30, `h24_dumped` 25, `volume_accel` 16, `m5_dropping` 15, signal 1. Seventeen different tokens were inside the universe; their median 1-hour change was +0.3% and 39% of readings were at +2% or better.
- Stops: all 23 lost, average -17.90%, total -1.8429 SOL, the price at the stop cycle averaging -15.6%. By age at entry: 3 days or more, 16 stops at -14.3% on price; 1 to 3 days, four at -16.4%; under a day, three at -21.6%. From v8 on: 7 stops at -15.1% (9 of the 15 trades that test reads). Both of today's filled within 2 points of the level with the cycle on time, so the cycles are not the problem. The eight trailing exits made +0.7553 SOL, the three 6-hour exits cost 0.0686.
- Left on the table: the average trade was up 15.7% at its best and realised -7.56%.
- LP locked: HOGE 84.2% and Huss 91.7%, both lost. Under 50%: 0 wins of 4. At 50% or more: 8 wins of 30.

**The record is a week old, so the tests that asked for "a week of data" were read. Four are decided; none changes a rule.** One scratch measurement did it, by the method of 06:30 on 16 Nov: a position opened at every eligible cycle and run through each exit variant, the same entries compared, a position whose token left the record marked at its last price, only entries opened 13 hours or more before the end of the record.

| Exit variant | Bot's universe (v9): 23,946 entries on 52 tokens | Per token | Wide, ages 3 to 30 days: 50,354 on 69 | Per token |
|---|---|---|---|---|
| live (12% stop, 5% trail, 6 hours) | -4.34% | -5.55% | -3.59% | -3.17% |
| stop 8% | -4.23% | -4.77% | -3.65% | -3.18% |
| stop 16% | -4.08% | -6.34% | -3.32% | -3.03% |
| stop 20% | -3.95% | -7.04% | -3.09% | -2.96% |
| stop 30% | -3.87% | -8.17% | -2.97% | -3.15% |
| hold at most 2 hours | -3.49% | -4.29% | -3.13% | -2.66% |
| hold at most 1 hour | -3.18% | -3.63% | -2.91% | -2.38% |
| first target 15% | -4.25% | -5.37% | -3.57% | -2.86% |
| trail 10% | -4.48% | -5.67% | -3.76% | -3.35% |
| stop moved to the entry after +10% | -4.43% | -5.51% | -3.77% | -3.15% |

- The 12% stop (the test of 06:30 on 16 Nov: wrong "if the exit table, redone on a week of data, shows a 20% stop ahead by 2 points or more on both records and on the per-token average as well"). A 20% stop is ahead by 0.39 and 0.50 points, and on the bot's universe the per-token average is 1.5 points worse with it. Of the entries stopped at 12%, 32% and 37% end better with a 20% stop; by token, 13 do better and 27 worse on the bot's universe, 29 and 26 wide. On tokens 1 to 3 days old the wider stop loses more (-4.81% against -3.83%). Not met by a wide margin. The stop stays at 12%, and Huss, NIO and Leonida coming back after their stops is the less common case, as it was for GTA on 17 Nov.
- The break-even stop (the test of 06:30 on 17 Nov: ahead by a point on both records and on the first signals). It is behind on both records (by 0.09 and 0.18) and within 0.3 either way on the first signals. Dropped. HOGE today would have been saved by it; nine cases like HOGE do not outweigh the positions it sells at the entry that then go on.
- `m5_change_min_pct` at -5 (the test of 06:30 on 18 Nov: five or more added trades on four or more tokens). In a week it adds one trade (Max, 22:45 on 17 Nov, +21.8%) and moves three others by one cycle. Not met; closed.
- "The entry section still needs a different idea if after a week the first signals at 300 or more, with WASTED and BLOB left out, are still level with a buy at any moment on the wide record" (06:30 on 16 Nov). They are: -2.47% on 106 first signals and 24 tokens (-6.83% per token) against -3.59% (-3.17% per token). Level. The 06:30 entry today drew that conclusion from the floor's own tests; this is the third reading that says it.
- Every variant still lands between -2.4% and -8.2%, around the 3% a round trip costs. Shorter holds lose less only because less happens in an hour. Exits move the losses around; they are not where an edge is.

**The finding of this review: the entry rules' lead over "no rule" was made on 13 to 15 Nov. Since 18 Nov the cycles they pick have done worse than all cycles, on both records.** `--baseline` with today's rules, split by the day the position was opened:

| Opened | Bot's universe: every eligible cycle | Cycles the rules passed | First passing cycle of each run | Wide, 3 to 30 days: every cycle | Passed | First passing |
|---|---|---|---|---|---|---|
| 13 to 15 Nov | -4.61% (7,610 on 30 tokens) | +8.58% (55 on 5) | +10.21% (20 on 5, 14 wins) | -3.37% (15,055 on 38) | +5.53% (82 on 12) | +2.58% (37 on 12) |
| 16 and 17 Nov | -4.20% (6,872 on 27) | -2.93% (28 on 11) | -2.24% (24 on 11, 8 wins) | -3.61% (16,415 on 39) | +4.85% (147 on 12) | +3.07% (62 on 12) |
| 18 to 20 Nov | -3.99% (11,103 on 28) | -6.97% (34 on 9) | -9.70% (18 on 9, 2 wins) | -3.02% (21,066 on 47) | -11.99% (85 on 13) | -12.53% (33 on 13, 3 wins) |

- Over the whole record `--baseline` reads: every eligible cycle 25,585 on 52 tokens, -4.23% (was -4.47%); cycles the rules passed 117 on 17, +1.31% (was +1.87% on 109); first passing cycle 62 on 17, 39% wins, -0.39% (was +0.28% on 58). The last row is under zero for the first time and has fallen at eight of the nine reviews since it was first read. The whole-week lead of 5.5 points is the first three days: five tokens, WASTED twelve times, and the days the 300-trade floor was chosen on.
- The bot's own trades opened since 18 Nov say the same: 8 closed, 1 winner (JESTER), -9.90% a trade.
- The 15 Nov entry set this up: wrong "if `--baseline` on a week of data still shows passing cycles no better than all cycles and the rules are still unchanged: at that point the entry section needs a different idea, not another threshold". By the letter the week's passing cycles are better, so it is not met. By the split, the lead on the bot's universe was 13 to 15 points on 13 to 15 Nov and 1 to 2 points on 16 and 17 Nov, and since 18 Nov the picks are 3 to 6 points worse than all cycles; on the wide record they were ahead until 17 Nov and are 9 points worse since. Three days on 9 and 13 tokens is a hint. It is also the same days the four v9 trades came from, so it is not independent of the trades.
- I then asked the yardstick about the premise itself, one cut, chosen because the rules are built on it: a buy at any eligible cycle, by the 1-hour change at that cycle (whole record).

| 1-hour change at the buy | under -10% | -10 to -2% | -2 to +2% | +2 to +10% | +10 to +25% | over +25% |
|---|---|---|---|---|---|---|
| Bot's universe, by cycle | -2.6% | -3.9% | -4.1% | -4.8% | -6.3% | -4.4% |
| Bot's universe, per token | -6.3% | -7.5% | -7.0% | -5.9% | -7.4% | -7.3% |
| Wide 3 to 30 days, by cycle | -0.9% | -3.3% | -3.7% | -3.9% | -5.2% | +4.0% |
| Wide 3 to 30 days, per token | -1.5% | -3.0% | -4.7% | -5.6% | -5.7% | -4.6% |

- The band the rules buy in (+2% to +25%) is the worse part of the table on three of the four rows: -5.2% against -3.8% for the other cycles on the bot's universe, -4.2% against -2.9% wide. On 15 Nov, with two and a half days, the same cut showed nothing; with a week it leans against buying the last hour's rise. It does not say buy the fall: the best band still loses 1% to 6%, no band covers the costs on both records, and the bot's own trades split the other way (bought under +11.2%, -10.99%; above, -4.13%).
- The same yardstick on the 6-hour candidate, read now so the count's verdict is not the only number when it comes: cycles with the 6-hour change at +30% or more and the 1-hour change inside the entry band lose 3.0% on the bot's universe (-6.6% per token) and 5.0% wide (-8.7% per token), against 6.6% (-6.0% per token) and 4.6% (-5.6% per token) for the same band at 0 to +30%. Better on one row of four. No cell of the 6-hour by 1-hour grid is above zero per token on both records, in the whole week or in either half of it.
- What follows. No threshold in the entry section is the obvious fix, and the entry rules have now gone three days picking worse than chance. That is not yet a finding and there is no tested idea to put in their place, so nothing changes today. It is written as a test with a count ("the rules as a whole" in the table above), and the bar a new entry idea has to clear is fixed now, before one is found: on the any-moment yardstick its cycles beat all cycles by 3 points or more (a round trip's cost) by cycle and per token, on both records, in both halves of the record, on 20 tokens or more.

**The open counts.**

- The 6-hour change: 4 of the 6 real entries under +30%, no winner, -12.28% (BAWSAQ, DIGS, NIO, HOGE). At +30% or more over the same days: 4, 1 winner, -7.52% (HOGE, JESTER, Leonida, Huss). The gap is 4.8 points and the test needs 5 at its end. On all real trades: under +30%, 17 on 11 tokens, no winner, -15.28%; +30% or more, 17 on 13 tokens, 8 winners, +0.15%. The row the last entry asked to be printed beside it, the baseline's first signals opened after 22:30 on 17 Nov: under +30%, 9 on 5 tokens, no winner, -10.41%; +30% or more, 9 on 6 tokens, 2 winners, -9.00%. Level. Not acted on; the number stays at 30.
- The 1-day floor's forward check: 8 of 10. Three new replay entries on tokens under a day old, all of the ordinary kind (found by `profiles_latest`, never on an uncovered pool): FIONA `B34nX...` 08:55 +12.71%, LOOSY `HF2RB...` 11:20 +21.77%, SWJ `gHZhq...` 13:15 -16.51%. The eight: 4 winners, +2.58% a trade, the worst -24.35%, none lost from the record. The bot's own trades over the same days: 9 at -10.77%. Two entries to go, and as it stands the test would be met. If it is, the 14:30 entry of 17 Nov says the band can go back in, and the review that reads it should say three things with it: the replay has no RugCheck, the same days' real trades lost at any age, and the two stops of 17 Nov that filled at -28% and -24% on price are why the floor is there.
- Tokens 1 to 3 days old: no new trade. 4 of 5 stops (one past -20% on price); 6 of 15 trades (2 wins, -4.55%, -0.1201 SOL) against 12 on older tokens over the same days (2 wins, -7.36%, -0.3691 SOL). The next stop in the band still decides the 3-day floor.
- `min_volume_accel` at 1.0 (window closes 22:30 on 21 Nov): DIGS 05:35 closed at the 6-hour limit, -5.64%. Four added trades on four tokens (HOGE -15.80%, Leonida +23.31%, FLOAT -14.38%, DIGS -5.64%), -3.13% a trade, against the five real trades of the same days at -15.30%. Read it at the close, for what it is: four trades that lose 3% each.
- The cooldown: NIO 03:50 in `--no-cooldown` ended at the 6-hour limit, -4.51%. Five cases for keeping it, none against. Huss passed the rules again at 13:20, ten minutes after its stop; that replay entry is open at +2.2% (best +11.9%). Record how it ends.
- The 300-trade floor's blocked band (wide, 150 to 299 trades): FLOAT 14:00 today on 288 trades, open at -9.3%. 0 of 5 closed.
- Trailing exits: none new (3 of 10). RugCheck refusals: none new (three so far).
- `python3 -m bot.replay` reproduces HOGE and Huss within 0.2 points of the journal: 29 closed on 17 tokens, 10 wins, -1.88% (it was -0.87% on 27); without the two entries RugCheck refused, 27 closed, 9 wins, -2.23%.
- The cap (`universe.max_volume_h24_to_liquidity` 150): no token blocked (`u:volume_to_liquidity` 0 on all 98 cycles), none inside the universe between 100 and 150 times. The highest ratios were ANTS (`ejrz9...`) 38, SHIT 35, Leonida 32, mihao 22; the median is 6.6. With the cap removed the replay makes the same trades.
- A 5-minute change of +10% or more (not carried, 06:30 today): a buy at every eligible cycle loses 5.69% with it (341 cycles on 39 tokens) against 4.21% without. 1.5 points; the line was 3 across 40 tokens.

**Tokens followed on an uncovered pool: `data/debug/hidden_pool_tokens.json` names five, and one answers the last entry's question.**

- ANTHROPIC `Pren1...`: a raydium pool against USDC of $395k to $427k behind an empty batch pool, 266 days old, `watch_too_old` on 4 cycles between 07:45 and 08:40. This is the token the run record could not name at 23:10 on 19 Nov: judged, read as too old and dropped on the same cycle, found again when its page came round. The last entry's reading of the code is confirmed. Four lookups in eight hours is far under the line (30 cycles in a day) for remembering such a token, so no code change.
- It also settles a point the 22:30 entry of 19 Nov left open: the batch call hides a live pool behind a dead one for old tokens too, not only in a token's first day. So "a hidden token becomes visible by itself at one day old" was too strong. What the record can say: of the five tokens uncovered in eight hours, four were under a day old and one was 266 days; none was between 1 and 30 days, which is the only range where it could change a trade. Keep the count by age.
- ANT `A9MDA...`: followed until 07:50 (14 cycles in the file, 96 in the day's snapshots). Its ratio went from 136 to 176 in one cycle at 06:50, when the pool went from $150k to $117k with the price up 1.3% (liquidity taken out, the step this kind has shown before), and stood at 182 with a pool of $125k and the price up 60% since midnight when the pool read $0 at 07:55. It was 12.7 hours old and never reached the age floor. The third of its kind, the first seen from its first hours to its end, and the cap would have blocked it had it lived to a day.
- 牛逼 `73HcK...` (09:05 to 09:25, $120k to $126k, 11,700 to 14,700 trades an hour) and 蚂蚁 `93Dxv...` (10:25 to 10:35, $128k to $132k, 13,000 to 14,800): both about an hour old, both at $0 on the next cycle. `u:too_young` throughout.
- ANT `DYDSu...` (a fourth ANT of this kind, found 11:45 by `gecko:vol8`): pumpswap against SOL, $114k to $148k, 5,800 to 6,200 trades in every hour, 1.08 to 1.11 buys per sell, 24-hour volume at 67 times its pool and rising 10 to 25 an hour. `u:too_young` on all 34 cycles; it turns a day old at about 10:10 on 21 Nov if its pool is still there.
- `hidden_pool_checked` read 1 or more on 86 of the 98 cycles and 4 on ten; `api_calls` peaked at 51. No `pool lookup` or `hidden sample` error.
- ANT `ANTBT...` (the $1.4M raydium pool against USDC) turns a day old at about 17:00 today; not yet inside the universe.
- Pools that go to $0 in one cycle (walked from the 98 versions of `data/state/watchlist.json` since 06:30): 20 in 8 hours, about 60 a day (it was 54). Twenty addresses under fifteen names (DCTY three times, apocry, PATRICK and 蚂蚁 twice each), pools of $74k to $187k, every one found by GeckoTerminal's most-traded-by-volume list (pages 3 to 8). None had passed the universe, none came back. One more pool read under half without going to zero (MANDY, $70k to $3k); it was not inside the universe.
- Discovery: the 17 tokens inside the universe came from `boosts_top` 4, GeckoTerminal before pages were labelled 4, `profiles_latest` 3, `gecko:trend2` 2 (Rings, Huss), and one each from a trending meta, `gecko:tx4` (HOGE), `gecko:tx6` (ANTS) and `gecko:vol7` (NVDA). No 429. None of the conditions for reopening the pages is met.

**Changed. No rule: rulebook v9 stays. No code change. In this file: the "Open tests" table and step 8 of "How to review".**

- Why no rule change. v9 has four closed trades. The tests that came due today (the stop, the break-even stop, the 5-minute floor, the week-old check on the 300-trade floor) all say leave it. The counts that could change a rule have not reached their ends: the 6-hour change 4 of 6, the 3-day floor 4 of 5 stops, the 1-day floor's forward check 8 of 10, the trail 3 of 10, and the volume test's window closes tomorrow. The last signal was 1.6 hours before the review, so the 12-hour rule gives no ground for a relaxation, and a relaxation would add entries of a kind that has lost for three days.
- Why not act on the finding. The honest name for the last three days is "the entry rules are doing worse than chance", and the honest size of it is 18 first signals on 9 tokens. Tightening a threshold on that would be the fourth entry fix shaped on a handful of losers, and there is no replacement idea that passes the yardstick. Cutting the position size or the number of trades to slow the loss would only steer the drawdown figure. The cost of waiting is real paper money, about 0.06 SOL a stop, and it is accepted here knowingly.

**For the next review.**

- First: cycles, errors, equity against 3.75 SOL (say so at the top if it is under), and the "Open tests" table: move every count a new trade moves.
- The 1-day floor's forward check is at 8 of 10 and would be met as it stands. Read the next two entries with the three cautions above, and name each as ordinary or uncovered.
- `min_volume_accel` 1.0: the window closes at 22:30 on 21 Nov. The 6-hour change: 4 of 6; print the baseline row beside it.
- The rules against no rule: the first signals in `--baseline` opened after 14:30 today, beside every eligible cycle of the same days. 0 of 15.
- The next stop on a token 1 to 3 days old: its price at the stop cycle against -20%.
- ANT `DYDSu...`: its ratio, when its pool goes, and what the file shows if it reaches a day old (about 10:10 on 21 Nov). ANT `ANTBT...` from 17:00 today. Any uncovered token between 1 and 30 days old: name it and say what the universe said.
- Where Huss 13:20 (`--no-cooldown`) and FLOAT 14:00 (the blocked band) end.
- Follow tokens by address, not by name.

**Would prove this review wrong.**

- Reading 18 to 20 Nov as a hint and changing nothing is wrong either way by the new test: of the first 15 first signals in `--baseline` opened after 14:30 on 20 Nov (8 or more tokens), if they average worse than every eligible cycle of the same days, the entry rules are worse than no rule on six days running and the entry section stops being tuned by thresholds until an idea clears the bar set above. If they average better by 3 points or more, the three days were three bad days and this entry made too much of them.
- Closing the stop question is wrong if a later exit table, on two weeks of data, shows a 20% stop ahead by 2 points on both records and per token. On one week it is ahead by half a point and behind per token.
- The bar for a new entry idea is too high if nothing clears it by 27 Nov while some idea clears it on every count but one. Then say which count and why it should not bind; do not lower the bar on the day an idea is found.
- The "Open tests" table is wrong wherever it differs from the entry that set a test. If a later review finds such a line, correct the table and say which entry it misread.
- Waiting on the 6-hour change, the 3-day floor, the 1-day floor's forward check, the trail and the cap is wrong by the tests in the table, which are unchanged.
- The health verdict is wrong if the gap between cycles grows past 15 minutes or skipped cycles become regular.

### v9, 2026-11-20 06:30 UTC review: no rule change (plumbing: every token judged on an uncovered pool is now named; NIO stopped; the 300-trade floor's second test closes at 2 winners in 10)

**Health.** 1,950 cycles since launch, 290 on v9, 97 since the last review (22:35 to 06:30). Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 5.3. No cycle was skipped, so no message to Ajeeb. One extra cycle (02:41:21, 68 seconds after the one before; both triggers fired; nothing was held). The newest cycle was 1.6 minutes old when the review started, so no `.kick`. No error in any of the 97 cycles. `api_calls` 46 to 53 (median 49), `allowed_pool_used` 1 or 2, universe 15 or 16 tokens a cycle, `u:too_young` 11 to 21 (median 14), watchlist 215 to 247 (cap 300; 220 now). RugCheck was called for both signals and both answers parsed: NIO `score_normalised` 1, no risks, LP locked 61.4%; HOGE 1, no risks, 84.2%. The saved sample still matches what `bot/rugcheck.py` reads (`score_normalised`, `risks[].level`, `lpLockedPct`). No `safety:*`, `skip:*` or `suspect_price` rows. No bug found in a decision path. One diagnostic added (below).

- `batch_miss` 14 to 19 a cycle (median 16), over the 15 single lookups on 59 of the 97 cycles. Never-seen tokens on the watchlist: 9 to 14 (median 11; all ten on it now are from `profiles_latest`). `batch_miss` less the never-seen tokens: 4 to 6 (median 5; it was 4 to 10, median 7), the line is 15, act at 13.
- The hidden-pool code's first full eight hours: no `pool lookup` error, never more than 4 lookups a cycle (4 on five cycles). `hidden_pool_checked` read 1 or more on 91 of the 97 cycles, every cycle from 23:05, because a remembered pool is looked up on each cycle; the last entry's "about one cycle an hour" was about first lookups and was loosely put. `api_calls` reached 53 twice (23:50 and 00:30, both cycles with 4 lookups); the last entry said it should stay under 54 and that the fix comes out if it passes 55. One short of the first line.
- The day's limits: 20 Nov started at 4.0128 SOL (NIO open and marked), has used 1 of its 10 new trades and has realised -1.47% against the 10% limit.
- I read the entries back to 14:30 on 17 Nov in full and, of the older ones, the test lists of 06:30 and 22:30 on 16 Nov. The file is 300 KB and does not fit in one session with the data.

**Strategy: v9 has 2 closed trades, both stops (-20.33% a trade, -0.1665 SOL), and 1 open. Two trades are not a hint.** v8 and v9 read as one series (the cap has changed no trade): 7 closed, 1 win, -9.35% a trade, -0.2748 SOL. All versions: 32 closed, 8 wins on seven tokens, -7.05% a trade, -1.0325 SOL. Equity 3.9569 SOL at 06:30 (-20.86%) with HOGE marked at -1.2% on price: a new low, on closed trades (3.9675 SOL, max drawdown 20.65%) and on the mark. The 22% line (3.90 SOL) was not reached. It is 0.068 SOL under the realised balance, less than one average stop (0.082 SOL), so a stop on HOGE at the average (-18%) would cross it and one that fills at the level (about -15% after costs) would not. The proof gate's line is 25%, 3.75 SOL: 0.218 SOL away, under three average stops with no winner between them. The rules give no licence to steer that with sizes or stops, and this review did not. SOL $71.9 to $73.2.

| # | Token | Opened (UTC) | Age | Trades in the hour before | 1-hour change at entry | 6-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|---|
| 32 | NIO (v9) | 19 Nov 23:45 | 29.3 days | 816 | +22.2% | +22.4% | 0.0% | stop, price at -12.1% | -14.66% |
| 33 | HOGE (v9) | 20 Nov 06:25 | 4.98 days | 371 | +9.9% | +14.5% | 0.0% | open at -1.2% on price (06:30) | |

- NIO, trade 32 (address `7SL2V...`, the same as trade 18, the 6-hour exit of 16 Nov; pool $128k, LP locked 61.4%). For the hour before the buy the price sat 18% to 24% under the later entry with about 200 trades an hour. At 23:40 it was 8.9% higher, and at 23:45 another 13.7% higher on $35.6k traded in those five minutes: trades in the hour went from 190 to 319 to 816 in two cycles, the 5-minute change read +18.9%, the 1-hour change +22.2%, buy pressure 1.21 against the 1.2 needed. The bot bought the top of that burst. The price never read above the entry: -2.2% on the next cycle, about -4% for half an hour, and -12.07% at 01:05, 0.07 points past the stop with the cycle on time. Ten minutes after the stop it was at -3.7%, at +0.5% by 01:35 and at +8.2% at 01:50. A wider stop would have held this one; one trade does not reopen the stop (the test for that is in the 06:30 entry of 16 Nov and wants a week of data).
- It is the "one burst" entry the reviews keep describing, on a token flat over six hours. It is the tenth trade of the 300-trade floor's second test, the third under +30% for the 6-hour test, and it counts in the "3 days or more" row.
- HOGE, trade 33 (address `FVzqG...`, the fourth trade on it: +17.03% on 16 Nov, then two stops; its cooldown ended at 03:05 on 19 Nov). A pumpswap pool against USDC of $128k, LP locked 84.2%, buy pressure 1.38, volume 1.67 times its six-hour average. The price went from $0.00099 to $0.00109 in one cycle at 05:50 and then moved between -0.4% and +5.0% of the later entry for half an hour while the trade count climbed past 300 (06:05) and buy pressure past 1.2 (06:25). Bought 4.7% under the 06:15 price. An open trade counts for nothing yet. When it closes it is the fourth entry under +30% for the 6-hour test and counts with the older tokens.
- Two signals since the last review (NIO 23:45, HOGE 06:25), both became trades, 7.3 and 6.7 hours after the signal before. The 12-hour rule is not met and no threshold was relaxed.
- Funnel, 1,519 universe-token checks: `h1_weak` 975 (64%), `h6_down` 199, a token in its cooldown 133, `txns_h1` 125, `h24_dumped` 25, `buy_pressure` 19, the held token 16, `h1_overheated` 12, `m5_dropping` 12, signal 2, `volume_accel` 1. Sixteen different tokens were inside the universe; their median 1-hour change was -0.8% and 30% of readings were at +2% or better.
- Stops: all 21 lost, average -18.11%, total -1.7192 SOL, the price at the stop cycle averaging -15.8%. By age at entry: 3 days or more, 14 stops at -14.4% on price; 1 to 3 days, four at -16.4%; under a day, three at -21.6%. On v8 and v9 the stop cycle averages -15.8% on 5 stops (it was -16.7% on 4; the test of 14:30 on 17 Nov reads it at 15 trades and there are 7). The eight trailing exits made +0.7553 SOL, the three 6-hour exits cost 0.0686.
- Left on the table: the average trade was up 16.1% at its best and realised -7.05%. NIO adds nothing to that: it was never up.
- LP locked: NIO 61.4%, lost. Under 50%: 0 wins of 4, unchanged. At 50% or more: 8 wins of 28.

**The 300-trade floor's second test is complete: 2 winners in 10. Its two tests disagree, so nothing changes, and the count is closed.**

- The 06:30 entry of 16 Nov called the floor wrong "if v5's first 10 closed trades have 2 winners or fewer: the same rules without it made 2 of 6, so that would be no improvement on the trades it keeps". Read since on tokens 3 days or older, the ten are Max -20.33%, Rings +23.97%, paws -16.63%, NIO -7.26%, FLOAT -3.95%, DIGS -14.96%, Leonida +19.80%, HOGE -18.47%, DIGS -4.40%, NIO -14.66%: 2 winners, -5.69% a trade, -0.2454 SOL. By the letter that test is met.
- The floor's other test, the forward check on what it blocks, closed on 18 Nov at 2 winners of 10 against a line of 3: in the floor's favour. Carried on since, the blocked band (entries on 150 to 299 trades, wide replay, tokens 3 to 30 days old) stands at 15 closed, 5 wins, -6.24% a trade; no new entry since Rings at 13:55 on 19 Nov.
- Put side by side: the trades the floor keeps lose 5.69% each and the trades it blocks lose 6.24% each. Level. The floor has not made the kept trades better and has not kept the bot out of worse ones; over the same days it removed 15 entries and left 10. The 14:30 entry of 19 Nov wrote the verdict before the tenth trade came in: two tests that disagree are no ground for a change. Putting the floor back to 150 would add trades that lose as much as the ones the bot already makes.
- What stands is the third line of that 16 Nov list: the entry section "still needs a different idea". Trade count is not it. Do not carry this count further. The one item left open on the floor is the 19 Nov check on the next five entries in the blocked band (0 of 5 so far).

**The 6-hour change at entry (the entry section's candidate, `entry.h6_change_min_pct` 0 to 30): 3 of the 6 the test needs, no winner.** NIO was bought at +22.4% and lost.

- Closed entries opened after 22:30 on 17 Nov: under +30%, 3 (BAWSAQ -15.03%, DIGS -4.40%, NIO -14.66%), no winner, -11.36%; +30% or more, 3 (HOGE, JESTER, Leonida), 1 winner, -4.57%. The gap is 6.8 points; the test needs 5 at its end. HOGE (trade 33, +14.5%) is open in the first group.
- On all real trades: under +30%, 16 on 10 tokens, no winner, -15.29%; +30% or more, 16 on 12 tokens, 8 winners, +1.19%. On trades made with today's entry rules on tokens a day old or more: 8, no winner, -12.15%, against 8, 4 winners, +1.63%.
- One thing against it that the count does not show, written down now and not after the sixth trade. The same split on the entry rules' first signals in `--baseline` opened after 22:30 on 17 Nov (which adds the signals the cooldown and RugCheck kept the bot out of): under +30%, 8 on 5 tokens (HOGE twice, BAWSAQ, DIGS three times, NVDA, NIO), no winner, -9.85%; +30% or more, 6 on 4 tokens (HOGE, JESTER, Leonida twice, Rings twice), 2 winners, -9.24%. Level. Since the pattern was named the high group has had its winners (JESTER, Rings at 16:15) and three stops past -23%. So the forward gap on real trades is one trade, JESTER. The test stands as written and I have not moved its number or its count; the entry that closes it should print this row beside the result and say which way it points then.
- Not acted on. The number stays at 30.

**A second look the report invites, tested and not carried: a buy on a 5-minute change of +10% or more.** NIO was bought with the 5-minute change at +18.9%.

- Real trades with a 5-minute change of +10% or more at entry: 3 (paws +18.4%, HOGE of 18 Nov +13.8%, NIO), all stops, -16.59% a trade. The other 29: 8 winners, -6.07%.
- On the record: the entry rules' first signals with it, 5 on 5 tokens, 1 winner (WOHAIHAO), -11.01%; without, 53 on 16 tokens, +1.35%. A buy at every eligible cycle: 322 cycles on 37 tokens at -5.72% with it, 23,736 on 50 at -4.45% without.
- The yardstick the earlier reviews agreed to go by is the last row, and it moves by 1.3 points across many tokens. Five signals do the rest. It is the same kind of hint as the 6-hour change and a weaker one, the entry section already has a candidate, and a cap on the 5-minute change would need a new key. Not named as a candidate. Written down so that a later review does not find it afresh and think it new.

**The token followed on an uncovered pool: ANT `A9MDA...`, and one the record could not name.**

- ANT `A9MDA...` has been judged on its pumpswap pool against SOL (`G7UA8...`) on all 91 cycles since 23:05: pool $117k to $150k, 5,300 to 6,030 trades in every hour, 1.08 to 1.11 buys per sell, the price up 58% in 7.4 hours in small steps. Its 24-hour volume went from $5.5M to $20.1M, from 47 to 135 times the pool; it passed 100 at 02:50 and, at $2M more an hour, passes 150 within an hour or so of this review. Between 02:45 and 02:50 the pool went from $150k to $117k (-22%) with the price up 2.3%: liquidity taken out, the same step the second ANT showed three times. `u:too_young` on every cycle. It is 11.3 hours old at 06:30 and turns a day old at about 19:10 today. It is the third token of this kind and the first the record holds from its first hours.
- On 8 of those cycles `hidden_pool_used` read 2 while one watchlist entry carried `alt_pool`: 23:10, 23:50, 00:30 and 01:10; 23:20, 00:00 and 00:40; and 03:10. Two series 40 minutes apart, which is the time GeckoTerminal's 16 pages take to come round at two a cycle: a token on two pages, or two tokens, looked up, judged and gone each time. Read from the code, one path fits: its oldest pool is over the watchlist's 35 days, so the cycle that uncovers it reads `watch_too_old` and the housekeeping drops it (`low_since` is cleared when the uncovered pool passes, and the watchlist was at 247 of 300). It is then found again as new the next time its page comes round. Harmless to trading; it cost 8 lookups in 8 hours and was one of the 4 on both cycles where `api_calls` read 53.
- The last entry said: if this count is again larger than the entries carrying `alt_pool`, name the token. It was, so that is this review's code change. See "Changed".
- Eight more tokens were looked up and had nothing live behind the empty pool (DCTY `13SYY...` and `AK6fW...`, VTC `BCVbA...`, FIONA `FKavc...`, CATMARIO `6E7Vt...`, RUGGED `Mz47d...`, AI `1VFf9...` and `DT5jE...`). The two AI addresses are worth a line: both read $127k and $123k at 23:55 and $0 at 00:00, were dropped from the watchlist six hours later, and were listed again by `gecko:vol7` at 06:30. As new entries they qualified for a lookup, and it showed no live pool. So for these two the $0 was an emptied pool, and GeckoTerminal's volume list was still carrying them 6.5 hours later.
- The second ANT (`8J2VU...`): not on the watchlist (dropped six hours after its pool read $0 at 18:45) and not found again by any feed. Not back, as far as the bot can see.

**The cap (v9, `universe.max_volume_h24_to_liquidity` 150).** No token blocked since the second ANT's last cycle at 18:40 on 19 Nov (`u:volume_to_liquidity` 0 on all 97 cycles). No token inside the universe between 100 and 150 times; the highest ordinary ratios were ANTS (`ejrz9...`) 39, SHIT 35, Leonida 24, mihao 23, and the median is 6.1. With the cap removed the replay makes the same trades. The test "of the first five different tokens it blocks, three or more are still inside the universe's other limits 24 hours after their first blocked cycle": 0 of 1 (the first token's 24-hour mark is 06:40 today, and its pool read $0 at 18:45 on 19 Nov and has not been seen since).

**What the last reviews asked, answered.**

- `min_volume_accel` at 1.0 (the test of 22:30 on 18 Nov; the window closes at 22:30 on 21 Nov): still three added trades on three tokens, -2.3% a trade (HOGE 11:35 -15.8%, Leonida 12:35 +23.3%, FLOAT 18:10 -14.4%). A fourth, DIGS at 05:35 today (`9QT8K...`, volume at 1.17 times), is open at -9.3%. The live trades over the same days are 3 (DIGS, Leonida, NIO) at -15.02%. On the whole record the setting gives 31 closed, 13 wins, +0.19% against 27, 10 wins, -0.87%. Read it at the close.
- The 1-day floor's forward check: 5 of 10, unchanged. No entry on a token under a day old since SHIT at 15:20 on 18 Nov. The hidden kind is in the record from 23:05 (ANT `A9MDA...`) and passed no entry test on any cycle.
- Tokens 1 to 3 days old: no new trade. 4 of 5 stops (one past -20% on price), 6 of 15 trades (2 wins, -4.55%, -0.1201 SOL) against 10 on older tokens over the same days (2 wins, -5.69%, -0.2454 SOL). The next stop in the band still decides the 3-day floor. In the band and inside the universe now: JESTER (2.66 days), SHIT (2.29), Leonida `9rbKk...` (2.21).
- Trailing exits: none new (3 of 10).
- The cooldown: NIO passed the entry rules again at 03:50, 2.75 hours after its stop (1-hour change +17.8%, 1,392 trades in the hour), and the cooldown kept the bot out. In the replay with no cooldown that entry is open at -11.9% (best +7.2%). Four cases for keeping it so far, none against; record how this one ends.
- The other modest relaxations since 16:30 on 19 Nov (no rule is met; this is the record): buy pressure at 1.1 buys HOGE at 06:10 instead of 06:25, 3.8% higher (open at -7.6%). `h1_change_min_pct` 1 or 0, `h6_change_min_pct` -10, `h1_change_max_pct` 35, `m5_change_min_pct` -5, `h24_change_min_pct` -40, `min_liquidity_usd` 40k, `max_age_days` 35 and the cooldown at 6 hours add nothing new.
- `python3 -m bot.replay` reproduces NIO within 0.2 points of the journal: 27 closed on 16 tokens, 10 wins, -0.87% (it was -0.35% on 26); without the two entries RugCheck refused (NVDA 14:35, Rings 16:15), 25 closed, 9 wins, -1.16%. `--baseline`: every eligible cycle 24,058 on 51 tokens, -4.47% (was -4.29%); cycles the entry rules passed 109 on 16, +1.87% (was +2.02% on 108); the first passing cycle of each run 58 on 16, 41% wins, +0.28% (was +0.54% on 57). The last row has fallen at seven of the eight reviews since it was first read. The entry rules still pick better moments than no rule, by 4.8 points, and after costs that is break-even at best on this record.
- RugCheck refusals: none new (three so far).
- ANT `ANTBT...` (raydium pool against USDC, $1.45M to $1.75M, the price at $91 to $96): 26,951 trades in its first hour and 142 in the last, 7 times its pool. It turns a day old at about 17:00 today and at this trade count fails `txns_h1` if nothing else.
- Pools that go to $0 in one cycle (walked from the 99 versions of `data/state/watchlist.json` since 22:25): 18 in 8 hours, about 54 a day (it was 54). Eighteen addresses under twelve names (AI four times, RUGGED three, DCTY twice, FIONA, AMD, SUPER ANT, COOKIE, BABYDOG, Koop, GTAVI, apocry, OMNI), pools of $53k to $208k and one that read $8.2M (a GTAVI address), 17 found by GeckoTerminal's most-traded-by-volume list (page 2 and pages 5 to 8) and one by page 6 of the trade-count list. None had passed the universe, none came back. Six more pools read under half on the next cycle without going to zero (VTC `JAWjx...` from $792k to $2.6k, UODF from $818k to $1.4k, a GTA6 address, BUNCOIN, LOOSY, SC); none was inside the universe.
- Discovery: the 16 tokens inside the universe came from `boosts_top` 4, GeckoTerminal before pages were labelled 4, `profiles_latest` 3, and one each from a trending meta, `gecko:trend2` (Rings), `gecko:tx4` (HOGE), `gecko:tx6` (ANTS) and `gecko:vol7` (NVDA). No 429 in the 97 cycles, the watchlist peaked at 247. None of the conditions for reopening the pages is met.

**Changed. No rule: rulebook v9 stays. One diagnostic in `bot/run.py`, which changes no decision and makes no API call, and its test.**

1. `bot/run.py`, `refine_pools` now returns the tokens judged on a pool found by its third case, not only how many. The funnel counts (`hidden_pool_checked`, `hidden_pool_used`) are as before.
2. `bot/run.py`, step 5c (the number is free again since the last entry took the old 5c out). For every such token the bot keeps one record in `data/debug/hidden_pool_tokens.json`, keyed by address: symbol, the pool it was judged on (`pair`, `dex`, `quote`), the first reading (`first_ts`, `first_liq_usd`, `first_age_days`), the latest (`last_ts`, `liq_usd`, `age_days`), the number of cycles it was judged this way, and under `verdicts` how often each answer came back: `watch_too_old`, `u:too_young`, `u:volume_to_liquidity`, `universe_ok` and so on, the watchlist test first and then the universe test, as the screen applies them. At most 40 tokens (`HIDDEN_SAMPLES`); those already in the file go on being updated. It sits inside a `try` and logs `hidden sample: ...` if it fails.
3. `tests/test_bot.py`: one test added, a scripted market where GeckoTerminal lists three tokens with a live pool behind an empty one: a quiet one that stays on the watchlist, one younger than the universe allows, and one whose dead pool is older than the watchlist allows (judged, dropped on the same cycle, and looked up again when its page comes round). It checks the three records and their verdicts, that the first reading is kept while the latest moves, that no API call is added, that a token found after the file is full is still judged on its live pool but not added, and that an unreadable file is logged and stops nothing. It fails on the old code and with each of these taken out: the diagnostic, the limit of 40, the watchlist verdict, the cycle count, the kept first reading, the `try`. 47 tests pass.
4. No version bump (plumbing). No change to the rulebook, the README or the workflow.

- Why not also stop the repeated lookups of a too-old token: the cause is read from the code, not yet seen in the data. One review with the file will show it. The fix, if it is confirmed and the count is high, is in "Would prove this review wrong".
- Why no rule change. v9 has two closed trades. The one test that reached its count today (the 300-trade floor's second) disagrees with the floor's first, and the two bands it compares are level. The others have not reached theirs: the 6-hour change stands at 3 of 6, the 1-to-3-day band at 4 of 5 stops and 6 of 15 trades, the 1-day floor's forward check at 5 of 10, the trail at 3 of 10, the cap at 1 of 5 blocked tokens, and the volume test's window closes tomorrow. The last signal was five minutes before the review, so the 12-hour rule gives no ground for a relaxation. The record is 32 trades, 8 winners, -7.05% a trade, no edge shown, and the account is at its low.

**After the review's cut at 06:30: the first live cycle of the new code.** Pushed at 06:44 UTC and picked up by the 06:45 cycle: v9, no errors, `api_calls` 47 (47 and 46 on the two cycles before), `batch_miss` 13, `universe_ok` 14, `hidden_pool_checked` 2, `hidden_pool_used` 1, no signal. `data/debug/hidden_pool_tokens.json` exists and holds one record: ANT `A9MDA...`, pumpswap against SOL, pool `G7UA8...`, $150k, 0.48 days old, `verdicts` `u:too_young` 1. HOGE was read and carried on as usual (+0.0% on price at 06:45, equity 3.9615 SOL).

**For the next review.**

- First: cycles, errors, and `data/debug/hidden_pool_tokens.json`. Read every entry: the address, the pool, the ages, the verdict counts. The token dropped each time it is uncovered should show `watch_too_old` and an age over 35 days. `api_calls` should stay under 54; a `hidden sample` error that repeats is this diagnostic failing.
- HOGE, trade 33 (`FVzqG...`): record the exit. Fourth entry under +30% for the 6-hour test, "3 days or more" row. If it trails out: the trail level, the fill, and what `--set exit.trailing_stop_pct=10` gives (it would be the fourth of 10).
- Drawdown: 20.65% on closed trades, 20.86% on the mark, against the gate's 25%. If it passes 22% (equity under 3.90 SOL), say so at the top of the entry.
- ANT `A9MDA...`: when its ratio passes 150 (expected within an hour or so of 06:30), what the file shows at the cycle it turns a day old (about 19:10 today; `u:volume_to_liquidity` is expected and would make it the cap's second blocked token), whether the batch call returns its traded pool from then on (`alt_pool` is dropped when it does), and when its pool goes.
- The 6-hour change: 3 of 6 under +30%, no winner; the gap between the groups is 6.8 points on real trades and 0.6 on the baseline's first signals. Print both.
- `min_volume_accel` 1.0: the window closes at 22:30 on 21 Nov; three added trades at -2.3% and DIGS 05:35 open.
- The next stop on a token 1 to 3 days old: its price at the stop cycle against -20%. It decides the 3-day floor.
- Where NIO 03:50 ends in `--no-cooldown`. The 1-day floor's forward check: 5 of 10. The trail: 3 of 10. The blocked band of the 300-trade floor: 0 of 5 new entries.
- `batch_miss` less the never-seen tokens: 4 to 6 now, the line is 15, act at 13. GeckoTerminal 429s: none in these eight hours.
- Pools that go to $0: the count per day (54 now). The cap: every token it blocks, and any token between 100 and 150 times.
- Follow tokens by address, not by name. Everything under "For the next review" in the earlier entries still stands, except the 300-trade floor's second test, which this entry closes.

**Would prove this review wrong.**

- The reading of the unnamed token is wrong if `data/debug/hidden_pool_tokens.json` shows a token that is not on the watchlist afterwards with any verdict other than `watch_too_old`. Then there is a path out of the watchlist I did not see in the code: find it before trusting `hidden_pool_used` again.
- The diagnostic was not worth its code if by 26 Nov the file has named nothing but ANT `A9MDA...`. It then goes out with the hidden-pool fix or stays with it, by the last entry's test for that fix.
- Not stopping the repeated lookups is wrong if one too-old token shows more than 30 cycles in a day in that file, or if `api_calls` reaches 55. Then remember such a token for a day (a small list in `data/state/meta.json`) so it is not looked up again, and do not revert the fix for a cost that is only this.
- Closing the 300-trade floor's count is wrong if the next five entries in the blocked band (wide replay, 150 to 299 trades, 3 to 30 days old) hold three or more winners and none ends on the liquidity rule, as the 14:30 entry of 19 Nov set out. Then reopen the forward check; do not change the floor on the spot.
- Waiting on the 6-hour change is wrong by the test of 22:30 on 17 Nov, unchanged: 0 winners of 3 so far, three entries to go. Printing the baseline row beside it is wrong if it is used to argue the count away: the test decides, the row says how much weight the result can bear.
- Not carrying the 5-minute change as a candidate is wrong if, on a week more of data, a buy at every eligible cycle with a 5-minute change of +10% or more does 3 points or more worse than the rest across 40 or more tokens. It is 1.3 points on 37 today.
- Waiting on the 3-day floor is wrong by the test of 14:30 on 17 Nov: one more stop in the band past -20% on price and the floor goes up; a day's trades in the band costing more than 5% of equity does the same.
- Leaving the rules alone is wrong by the tests the earlier entries set, which are unchanged: the cap (06:30 on 19 Nov), the 5% trail (22:30 on 16 Nov), the 1-day floor's forward check (14:30 on 17 Nov), `min_volume_accel` (22:30 on 18 Nov).
- The health verdict is wrong if the gap between cycles grows past 15 minutes or skipped cycles become regular.

### v9, 2026-11-19 22:30 UTC review: no rule change (plumbing fix: a token whose batch pool is a dead one is now judged on the live pool a full lookup shows; Leonida stopped at -23.6% against a 12% level)

**Health.** 1,853 cycles since launch, 193 on v9, 97 since the last review (14:35 to 22:30). Last 6 hours: 74 cycles, median gap 5.0 minutes, longest 5.2. No cycle was skipped, so no message to Ajeeb. One extra cycle (21:50:12, 50 seconds after the one before; both triggers fired; nothing was held). The newest cycle was 1.7 minutes old when the review started, so no `.kick`. Errors on 3 of the 97 cycles, all GeckoTerminal 429: page 3 of the trade-count list at 18:40, page 4 at 18:45, trending page 1 at 19:35. Two cycles running is new, but it was two different pages and the next 9 cycles were clean. `api_calls` 47 to 49 (median 48), `allowed_pool_used` 1 or 2, universe 16 or 17 tokens a cycle, `u:too_young` 11 to 16 (median 13), watchlist 187 to 247 (cap 300; 247 now). RugCheck was called twice and both answers parsed (NVDA and Rings, below); the saved sample still matches what `bot/rugcheck.py` reads (`score_normalised`, `risks[].level`, `lpLockedPct`). No `skip:*` or `suspect_price` rows. One real bug found and fixed (below).

- `batch_miss` 16 to 22 a cycle (median 18), over the 15 single lookups on every one of the 97 cycles (it was 16 of 98). Never-seen tokens on the watchlist: 10 to 14 (median 12; eleven of the twelve on it now are from `profiles_latest`). `batch_miss` less the never-seen tokens: 4 to 10 (median 7; it was 2 to 9, median 3), the line is 15. Tokens that have had data are looked up first, so none went unpriced, but the margin has halved in a day. If the top of that range reaches 13, raise `discovery.max_single_lookups` before a held token's neighbours start going unread.
- The day's limits: the day started at 4.1523 SOL, has used 2 of its 10 new trades and has realised -3.03% against the 10% limit.
- I read the entries back to 22:30 on 17 Nov in full and, of the older ones, the test lists for the 1-day floor (14:30 on 17 Nov) and the 3-hour floor (12:30 on 16 Nov). The file is 270 KB and does not fit in one session with the data.

**Strategy: v9 has 1 closed trade, a loss. One trade is not a hint.** v8 and v9 read as one series (the cap has changed no trade): 6 closed, 1 win, -8.47% a trade, -0.2157 SOL. All versions: 31 closed, 8 wins on seven tokens, -6.81% a trade, -0.9734 SOL. Equity 4.0266 SOL (-19.47%), nothing open. Max drawdown 19.47% on closed trades, a new low by 0.04 points; the lowest marked equity on record (4.0129 SOL on 18 Nov) was not passed. The 22% line (3.90 SOL) was not reached. The proof gate's line is 25%, 3.75 SOL: 0.277 SOL away, about three average stops (0.083 SOL each) with no winner between them. SOL $72.2 to $75.2.

| # | Token | Opened (UTC, 19 Nov) | Age | Trades in the hour before | 1-hour change at entry | 6-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|---|
| 31 | Leonida (v9) | 14:15 | 1.54 days | 2,067 | +16.0% | +95.1% | +19.3% | stop, price at -23.6% | -26.00% |

- Leonida, trade 31 (address `9rbKk...`, pool $129k, LP locked 100%). It read +19.3% at 14:45, 0.7 points short of the first target, +4.5% ten minutes later, +3.1% at 15:10 and -23.6% at 15:15: a fall of 25.9% in one cycle, with the cycle on time (5.0 minutes). The pool went from $131k to $113k on that cycle (-14.2%), which is what net selling of roughly $9k does to a pool that size, and the 5-minute figures read $7.6k traded with 237 buys against 50 sells: a few large sales and many small buyers. Both bad-print guards rightly let it through (the move had the volume a real one needs). The price was back at -6.0% twenty minutes after the stop and at -2.1% by 17:05. So the stop filled 11.6 points past its level and sold near the low. This is not late cycles; it is one price every five minutes on a token where a few sales can move the price by a quarter.
- It is the fourth stop on a token 1 to 3 days old and the first of them past -20% on price (-14.5%, -15.4%, -12.1%, -23.6%). The test of 14:30 on 17 Nov says the floor goes to 3 days if the first five such stops include two past -20%. It reads 1 of 4. **The next stop in that band decides it**: past -20% on price and `universe.min_age_days` goes from 1 to 3 at that review; inside -20% and that part of the test is passed. The test's other two arms: the day's trades in the band cost 2.6% of the day's starting equity (the line is 5%); the band has 6 of the 15 closed trades it asks for (2 wins, -4.55% a trade, -0.1201 SOL) against 9 trades on older tokens over the same days (2 wins, -4.69%, -0.1864 SOL). Level, so far.
- The same entry asked whether the gap past the stop is about age at all: "v8's first 15 closed trades still show a stop cycle averaging worse than -16% on price". After 6 trades and 4 stops (v8 and v9) it is -16.7%. Too few to read; noted because it now sits on the wrong side.
- Stops: all 20 lost, average -18.28%, total -1.6602 SOL, the price at the stop cycle averaging -16.0%. By age at entry: 3 days or more, 13 stops at -14.6% on price; 1 to 3 days, four at -16.4%; under a day, three at -21.6%. The eight trailing exits made +0.7553 SOL, the three 6-hour exits cost 0.0686.
- Left on the table: the average trade was up 16.6% at its best and realised -6.81%. Leonida is the eighth loser that was up 10% or more first, and the closest miss of the target so far. I ran the first target at 15% again, as the 22:30 entry of 16 Nov did: on the replay's 26 entry-rule trades it gives +1.83% a trade against -0.35% (13 winners against 10), and on a buy at every eligible cycle it moves the mean from -4.29% to -4.20%. The second number is the one earlier reviews agreed to go by (22,600 cycles on 51 tokens against 26 trades the rules were shaped on) and it has not moved. Not acted on; the exit section stays as v7 left it.
- LP locked: Leonida 100.0%, lost. Under 50%: 0 wins of 4, unchanged. At 50% or more: 8 wins of 27.
- Funnel, 1,557 universe-token checks: `h1_weak` 846 (54%), a token in its cooldown 186, `txns_h1` 137, `h6_down` 136, `h1_overheated` 93, `buy_pressure` 71, `h24_dumped` 54, `m5_dropping` 21, the held token 8, signal 3, `volume_accel` 1, `liquidity_falling` 1. Seventeen different tokens were inside the universe; their median 1-hour change was -0.4% and 38% of readings were at +2% or better.

**Three signals since 14:30 and RugCheck refused all three, correctly by the rule.**

- NVDA at 14:35 (in the last entry): `score_normalised` 81, four `danger` risks. In the replay, which has no RugCheck, that entry ends at the 6-hour limit, -6.25%.
- Rings at 16:15 and again at 16:30 (address `65iH8...`, the token of trades 11 and 16): `score_normalised` 51 against the 30 allowed, one risk at level `danger` ("Large Amount of LP Unlocked"), LP locked 2.7%. RugCheck was called at 16:15 and the 16:30 signal was refused from the cache. The same token read LP locked 26.2% when the bot bought it on 16 Nov at 01:45 and 78.8% at 17:00 that day, so the lock on this pool comes and goes; the screen judged what it saw. In the replay the 16:15 entry makes +11.88% (best +21.0%, half sold at the target and the rest trailed out within ten minutes) and a buy at 16:30 is a stop at -20.8% on price twenty minutes later. One refused winner, one refused loser, and a pool whose LP can be withdrawn is what the screen is there to refuse. The safety section is not for loosening.
- So the last signal that could become a trade was Leonida at 14:15 (8.3 hours before this review) and the last signal of any kind was Rings at 16:30 (6.0 hours). The 12-hour rule is not met on either count and no threshold was relaxed.
- Reading the replay from here on: leave out NVDA 14:35 and Rings 16:15, which the bot could not make. `python3 -m bot.replay` gives 26 closed on 16 tokens, 10 wins, -0.35% (it was +0.49% on 23); without those two, 24 closed, 9 wins, -0.61%. It reproduces Leonida within 0.2 points of the journal.

**The finding of this review: the batch call does hide live pools behind dead ones. `data/debug/no_liquidity_pairs.json` has five entries and one shows it plainly.**

| Token | Found by | Batch call's pool | Every pool the full lookup knows | Reading |
|---|---|---|---|---|
| ANT `A9MDA...` (22:30, 3.4 hours old) | `gecko:vol5` | meteoradbc, no liquidity figure, 1 trade in 24 hours | **pumpswap against SOL, $145k, 19,050 trades, $4.9M in 24 hours**; meteora $0; the meteoradbc pool $0 | hidden: a live pool the bot never saw |
| DCTY `AK6fW...` (16:30, 1.5 hours old) | `gecko:vol7` | meteoradbc, no liquidity figure | pumpswap against SOL, $0 after 9,796 trades and $3.6M; meteora $0; meteoradbc $0 | the same shape, already emptied when looked at, 45 minutes after it was found |
| DCTY `13SYY...` | `gecko:vol5` | pumpswap, $0 | the same pool, $0 | emptied; GeckoTerminal's list was behind |
| VTC `BCVbA...` | `gecko:vol8` | pumpswap, $1.4k | the same pool; a pump.fun pool at $0 | emptied |
| Apocrycoin `JeUwZ...` | `gecko:vol5` | pumpswap, $0.01 | the same pool, $0 | emptied |

- Two of the five are tokens launched on a Meteora bonding-curve pool (`meteoradbc`) whose trading then moved to a pumpswap pool. All their pools have the same age. DexScreener's batch call (one pool per token) answers with the launch pool, which has a price, no liquidity and one trade. The full pool lookup knows the traded pool.
- That explains both earlier ANTs (`ELR9i...` on 17 Nov, `8J2VU...` on 19 Nov), which read $0 for four hours and $120k from the cycle their age read 1.00 day: a launch pool with no trade in 24 hours most likely drops out of the batch answer when its last trade is a day old, and the traded pool takes its place. That is an inference from two tokens that both switched at 1.00 day; the repo cannot show DexScreener's rule.
- What it has cost: no trade under v8 or v9, as far as the record shows, because the hidden stretch is the token's first day and the floor is 1 day. It did mean that under v6 and v7 (floor 3 hours) the bot was blind to this kind of token, that the snapshots hold no reading of them before they are a day old (so `--set universe.min_age_days=0.125` has never seen them either), and that such a token arrives in the universe with a day of volume on its first visible cycle.
- The last entry wrote down what to do in this case before the data came: "that is a real bug: give a token GeckoTerminal lists a full pool lookup in `refine_pools` when its batch pool is under the floor, judge it on the deepest allowed pool". Done, see "Changed".

**The cap's first blocked token is gone (v9, `universe.max_volume_h24_to_liquidity` 150).**

- The second ANT (`8J2VU...`) was blocked on 50 more cycles (146 in all since 06:40) at 258 to 328 times its pool, and read $0 from 18:45: 17.4 hours after it first passed the universe's other limits, 12.1 hours after the cap went live. Its last reading was $131k at 18:40 with 5,934 trades in the hour and the price up 111% since 01:20. Nothing in the 211 readings fell under 0.77 of the cycle before until the last one.
- With the cap removed the replay makes the same trades, so the cap still has not changed a trade: the token's buy pressure never reached 1.2. What the cap did was stop relying on that.
- Honest limit: after this review's own finding a $0 reading is not proof of an emptied pool. For this token the batch call had been returning the traded pool for 17 hours, the first ANT ended the same way 4.7 hours after turning a day old, and it has not come back in 3.8 hours; emptied is the likely reading and the new code would show it if it is not (a token is only looked up when its pool has been empty since it was found, so this one will not be; see the open question under "Would prove this review wrong").
- The schedule reading of 14:30 fails its own test. The pool lost a fifth a third time at 17:25 (-21.7% with the price up 2.5%), 4.75 hours after the second step, not 6, and 18:35 to 18:40 showed nothing. Liquidity was taken out three times; it was not on a clock.
- The cap's test "of the first five different tokens it blocks, three or more are still inside the universe's other limits 24 hours after their first blocked cycle": 0 of 1. No token inside the universe between 100 and 150 times; the highest ordinary ratios were ANTS (`ejrz9...`) 37, SHIT 31, mihao 21, Leonida 19, and the median is 6.3.
- Seven addresses named ANT or ANTS are on the watchlist now. One (`ANTBT...`, found 18:05 by `gecko:tx6`) has a $1.6M raydium pool against USDC and was 5.5 hours old at 22:30; it turns a day old at about 17:00 on 20 Nov, at 6 times its pool so far. Follow it by address.

**What the last reviews asked, answered.**

- The 6-hour change (candidate `entry.h6_change_min_pct` 0 to 30): still 2 of the 6 the test needs, because Leonida was bought at +95.1%. Closed entries opened after 22:30 on 17 Nov: under +30%, 2, no winner, -9.71%; +30% or more, 3 (HOGE, JESTER, Leonida), 1 winner, -4.57%. The gap between the groups is 5.1 points, down from 15.9 before Leonida; the test needs 5 at its end. On all real trades: under +30%, 15 on 10 tokens, no winner, -15.34%; +30% or more, 16 on 12 tokens, 8 winners, +1.19%. The two refused entries are not counted (NVDA at +2.1% lost, Rings at +134% won). Not acted on; the number stays at 30.
- `min_volume_accel` at 1.0 (the test of 22:30 on 18 Nov; the window closes at 22:30 on 21 Nov): three added trades on three tokens now, HOGE 11:35 (stop, -15.8%), Leonida 12:35 (+23.3%) and FLOAT 18:10 (stop, -14.4%), -2.3% a trade. It also buys DIGS two hours later (-5.3% against -4.3%) and, being in Leonida's cooldown at 14:15, skips trade 31. The live trades over the same days are 2 at -15.2%. By the letter the count is reached and the added trades are "better", a day before the window closes. Read it at the close, and read it for what it is: three trades that lose 2.3% each beat two that lost more. On the whole record the setting gives 30 closed, 13 wins, +0.68% against 26, 10 wins, -0.35%. A hint, the same size as on 18 Nov.
- The 300-trade floor's second test: 2 winners in 9, unchanged (Leonida is under 3 days old). One trade to go.
- What the floor blocks (entries on 150 to 299 trades, wide replay, 3 to 30 days old): no new entry since Rings at 13:55. 0 of the 5 the last entry asked to be counted.
- The 1-day floor's forward check: 5 of 10, unchanged; no entry on a token under a day old since SHIT at 15:20 on 18 Nov. From the next cycle the record of young tokens changes (the fix makes the hidden kind visible), so entries 6 to 10 are drawn from a wider set than entries 1 to 5 were. Say which kind each one is.
- Trailing exits: none new (3 of 10). The other modest relaxations since 14:15 (`h1_change_min_pct` 1 or 0, `h6_change_min_pct` -10, `h1_change_max_pct` 35, `m5_change_min_pct` -5, `h24_change_min_pct` -40, `min_liquidity_usd` 40k) add nothing new. Buy pressure at 1.1 buys Leonida at 14:35 instead of 14:15 and is stopped at -27.9% on price. `--no-cooldown` adds Rings at 16:30 (refused by RugCheck in life), a stop.
- `--baseline`: every eligible cycle 22,612 on 51 tokens, -4.29% (was -4.66%); cycles the entry rules passed 108 on 16, +2.02% (was +4.56% on 98); the first passing cycle of each run 57 on 16, 42% wins, +0.54% (was +2.02% on 52). The last row has fallen at six of the seven reviews since it was first read and is now within a rounding of zero. The entry rules still pick better moments than no rule (by 4.8 points), and after costs that is break-even at best on this record.
- Pools that go to $0 in one cycle (walked from the 98 versions of `data/state/watchlist.json` since 14:30): 18 in 8 hours, about 54 a day (it was 66). Eighteen addresses under nine names (KFC five times, CATMARIO four, DCTY and ANT twice each, ZEST, OMNI, Sparrow, AI, BUTTHOLE), pools of $31k to $158k, 16 found by GeckoTerminal's most-traded-by-volume list (pages 2 to 8) and 2 by the trade-count list. Seventeen had never passed the universe. The eighteenth is the second ANT. None came back. Seven more pools read under half on the next cycle without going to zero; none was inside the universe. Each of the 18 had read $30k or more on the batch call first, so these are not the hidden kind; of the 72 GeckoTerminal-found tokens on the watchlist in these hours, 6 read $0 from their first reading, and those are the ones the fix now looks up.
- Discovery: the 17 tokens inside the universe came from `boosts_top` 4, GeckoTerminal before pages were labelled 4, `profiles_latest` 3, `gecko:tx6` 2, and one each from a trending meta, `gecko:trend2`, `gecko:tx4` (HOGE) and `gecko:vol7` (NVDA). None of the conditions for reopening the pages is met.

**Changed. No rule: rulebook v9 stays. One fix in `bot/run.py`, which changes which pool some tokens are judged on, and its tests.**

1. `bot/run.py`, `refine_pools`, a third case next to the two it already handled. A token that GeckoTerminal lists on the current cycle (so it reports a pool over its $30k reserve floor now), whose batch pool has been under the watchlist floor ever since the token was found, gets one full pool lookup. If the lookup shows a pool quoted in SOL, USDC or USDT with at least the watchlist's minimum liquidity, the token is judged on that pool, exactly as a token with an exotic-quoted batch pool already was: its age is that of its oldest pool, a position opened on it is priced on that pool, and every universe, entry and safety test applies as before. The pool is remembered in the watchlist entry (`alt_pool`) and looked up again on every cycle until the batch call returns a deep enough pool itself or the lookup no longer shows one. If the lookup shows no such pool, the token is not looked up again for 30 minutes (`pools_checked`). At most 4 of these lookups a cycle (`HIDDEN_LOOKUPS`), remembered pools first. A token that has ever had a real reading from the batch call is never looked up this way: that is the ordinary emptied pool.
2. The run funnel has two new counts: `hidden_pool_checked` (lookups made) and `hidden_pool_used` (tokens judged on a pool found this way on that cycle).
3. Step 5c, the diagnostic added at 14:30, is taken out with its test. It answered its question in eight hours, and with the fix in place it would only ever record the emptied kind. `data/debug/no_liquidity_pairs.json` stays as the record of what it found.
4. `tests/test_bot.py`: the diagnostic's test is replaced by two. One scripted market where GeckoTerminal lists five tokens: one with a live pool behind an empty one that passes the entry rules (bought, on the live pool, and sold on `liquidity_drop` when that pool is drained), one quiet (followed every cycle, a failed lookup logged and survived, the flag dropped when the batch call returns the pool itself), one whose dead pool is older than the universe allows (not made young by its live pool), one with nothing behind the empty pool (asked once, and once more after 30 minutes), one emptied after a real reading (never asked). The other checks the cap of 4 and the conditions one by one. Both fail on the old code, and the first or second fails with each of these taken out: the "had a real reading" rule, the cap, the 30-minute wait, the remembered pool, the oldest-pool age. 46 tests pass.
5. README: one sentence in the honesty rules. No version bump (plumbing). No change to the rulebook or the workflow.

- What it can change in trading: nothing for a token under a day old (the floor still applies). A token a day old or more whose batch pool is still a dead one becomes visible and can be bought if it passes everything, RugCheck included; so far no such token is on the record. The tokens this is known to uncover are the machine-traded kind (two ANTs, DCTY), and what stands between those and a buy is the 1-day floor, then the volume cap, then the entry rules and RugCheck. That order of defence is unchanged.
- What it costs: of the 98 watchlist versions since 14:30, 3 to 7 GeckoTerminal-found tokens at a time had a batch pool empty since they were found (9 different ones in 8 hours), so first lookups are about one an hour and the steady cost is one call a cycle per live hidden pool. `api_calls` was 47 to 49; with the cap it cannot pass 53 from this (the line earlier entries set is 55).
- Why no rule change. v9 has one closed trade. No test set by an earlier entry has reached its count: the 6-hour change stands at 2 of 6, the 1-to-3-day band at 4 of 5 stops (one past -20%) and 6 of 15 trades, the 1-day floor's forward check at 5 of 10, the trail at 3 of 10, the 300-trade floor's second test at 9 of 10, the cap at 1 of 5 blocked tokens. The last signal was 6 hours before the review, so the 12-hour rule gives no ground for a relaxation. The record is 31 trades, 8 winners, -6.81% a trade, and no edge shown; the bot is 0.28 SOL from the proof gate's drawdown line and the rules give no licence to steer that with sizes or stops.

**After the review's cut at 22:30: the first live cycles of the fix.**

- Pushed at 22:44 UTC and picked up by the 22:45 cycle. Seven cycles to 23:15: v9, no errors, `batch_miss` 19, `universe_ok` 16, no signal, nothing open. `api_calls` 48 on the first four (GeckoTerminal was on pages that listed no such token), then 49, 51 and 52.
- 23:05: `hidden_pool_checked` 1, `hidden_pool_used` 1. It is ANT `A9MDA...`, the token of the table above: judged on its pumpswap pool against SOL (`G7UA8...`) from that cycle on and in every snapshot since. At 23:15: pool $119k, 4.1 hours old, $6.0M of 24-hour volume (50 times the pool and rising with every hour it lives), 5,939 trades in the hour, 1.10 buys per sell, 1-hour change +11.4%. `u:too_young` on each cycle, as it should be. Its trade count and buy pressure are the two earlier ANTs' to the decimal.
- 23:10: 3 lookups, 2 used. One is the ANT again. The other is not on the watchlist afterwards and the run record does not name it. The one path that fits is a token whose uncovered pool is fine but whose oldest pool is over the watchlist's 35 days: it is judged, read as `watch_too_old` and dropped on the same cycle, like the 70 or so too-old tokens the feeds bring back every cycle. Harmless, but the funnel counts cannot say which token it was. DCTY `13SYY...` was looked up and has nothing behind its empty pool.
- 23:15: 4 lookups (the cap), 1 used. DCTY `AK6fW...`, VTC `BCVbA...` and a FIONA address found on that cycle (`FKavc...`) have nothing live; each is marked and will not be asked again for 30 minutes.
- So in its first half hour the fix found the one token the diagnostic said it would, plus one it cannot name, and it reached its cap of 4 once. `api_calls` at 52 is 3 under the line of 55.

**For the next review.**

- First: cycles, errors, and the first cycles of the new code. `hidden_pool_checked` should appear on about one cycle an hour and never exceed 4; `hidden_pool_used` shows each token judged on an uncovered pool. Name each one by address: its DEX, the pool's size, its age, what the universe said (`u:too_young` is expected), and what its pool did next. `api_calls` should stay under 54. A `pool lookup` error that repeats is the fix failing.
- ANT `A9MDA...` (followed on its pumpswap pool since 23:05): when its pool goes, whether the lookup or the batch call shows it at the cycle it turns a day old (about 19:05 on 20 Nov), and whether the cap then blocks it (50 times its pool at 4 hours old). If `hidden_pool_used` is again larger than the number of watchlist entries carrying `alt_pool`, write the uncovered token's address to `data/journal/events.jsonl` from `refine_pools` so it can be named.
- The next stop on a token 1 to 3 days old: its price at the stop cycle against -20%. It decides the 3-day floor (above).
- The 6-hour change: 2 of 6 under +30%, no winner; the gap between the groups is 5.1 points.
- `min_volume_accel` 1.0: the window closes at 22:30 on 21 Nov; three added trades at -2.3% so far.
- The 300-trade floor's second test: 2 winners in 9, one trade to go on a token 3 days or older. The 1-day floor's forward check: 5 of 10. The trail: 3 of 10.
- Drawdown: 19.47% on closed trades against the gate's 25%. If it passes 22% (equity under 3.90 SOL), say so at the top of the entry.
- `batch_miss` less the never-seen tokens: 4 to 10 now, the line is 15; act at 13 (above). GeckoTerminal 429s: three in eight hours, two of them on cycles running.
- Pools that go to $0: the count per day (54 now). The cap: every token it blocks, and any token between 100 and 150 times.
- RugCheck refusals: each one, with what the replay says the trade would have done. Three so far (NVDA lost, Rings won at 16:15 and lost at 16:30).
- Follow tokens by address, not by name. Everything under "For the next review" in the earlier entries still stands, except the items about step 5c and the second ANT's schedule, which this entry closes.

**Would prove this review wrong.**

- The fix is wrong, and should be reverted to the code of 14:44, if a `pool lookup` error appears on more than a handful of cycles a day, if `api_calls` passes 55, or if a token is bought on an uncovered pool that the batch call was right to call empty (the position would close on `liquidity_drop` or a write-off within a cycle or two of the buy with the pool's first reading already under the floor).
- It was not worth its code if by 26 Nov `hidden_pool_used` has never appeared, or has only ever appeared for tokens that were gone within the hour. Then say so and decide whether four lookups a cycle are better spent elsewhere.
- The inference that a hidden token becomes visible by itself at one day old is wrong if the fix uncovers a token a day old or more. Then the bot was blind to tradable tokens, not only to young ones, and every count of "tokens inside the universe" before today was short; write down how many and what they did.
- Reading the second ANT's $0 as an emptied pool is wrong if that address shows a pool of $30k or more again. The fix would not see it (the token has had real readings), so check `data/state/watchlist.json` for `8J2VU...` at the next review; if it is back, extend case 3 to a token whose pool goes from over the floor to exactly $0 while GeckoTerminal still lists it.
- Not lowering the first target after Leonida is wrong by the test the 22:30 entry of 16 Nov used, unchanged: a first target at 15% has to move the mean of a buy at every eligible cycle by more than 0.3 points. It moves it by 0.09.
- Waiting on the 3-day floor is wrong by the test of 14:30 on 17 Nov: one more stop in the band past -20% on price and the floor goes up; a day's trades in the band costing more than 5% of equity does the same.
- Waiting on the 6-hour change is wrong by the test of 22:30 on 17 Nov, unchanged: 0 winners of 2 so far, four entries to go.
- Leaving the rules alone is wrong by the tests the earlier entries set, which are unchanged: the cap (06:30 today), the 5% trail (22:30 on 16 Nov), the 1-day floor's forward check (14:30 on 17 Nov), `min_volume_accel` (22:30 on 18 Nov).
- The health verdict is wrong if the gap between cycles grows past 15 minutes or skipped cycles become regular.

### v9, 2026-11-19 14:30 UTC review: no rule change (plumbing: a diagnostic for tokens whose pool reads $0 while GeckoTerminal lists it; both ANT pools were invisible until the cycle they turned a day old)

**Health.** 1,756 cycles since launch, 96 on v9 (from 06:40), 98 since the last review. Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 5.3. No cycle was skipped, so no message to Ajeeb. One extra cycle (13:40:58, 45 seconds after the one before; both triggers fired; nothing was held). The newest cycle was 1.9 minutes old when the review started, so no `.kick`. Errors on 2 of the 98 cycles, neither repeated: at 12:50 GeckoTerminal 429 on trending page 2 together with DexScreener 429 on five full pool lookups (the lookups for tokens whose batch pool is quoted in a token the rulebook does not trade; this is the first DexScreener 429 on the record; nothing was held and the next cycle was clean), and at 13:50 GeckoTerminal 429 on page 1 of the trade-count list. `api_calls` 44 to 47 (median 46), `allowed_pool_used` 1 or 2, universe 14 to 17 tokens a cycle (median 15), `u:too_young` 11 to 19 (median 14), watchlist 172 to 215 (cap 300; 188 now). RugCheck ran for the one signal and the answer parsed: Leonida `score_normalised` 1, no risks, LP locked 100.0%. The saved sample still matches what `bot/rugcheck.py` reads (`score_normalised`, `risks[].level`, `lpLockedPct`). No `safety:*`, `skip:*` or `suspect_price` rows. No bug found in a decision path. One diagnostic added (below).

- `batch_miss` 12 to 20 a cycle (median 14), over the 15 single lookups on 16 of the 98 cycles. Never-seen tokens on the watchlist: 10 or 11 (nine of the eleven on it now are from `profiles_latest`). `batch_miss` less the never-seen tokens: 2 to 9 (median 3), the line is 15.
- The day's limits: the day started at 4.1523 SOL, has used 2 of its 10 new trades and has realised -0.44% against the 10% limit.
- The first v9 cycles did what the last entry said they should: `u:volume_to_liquidity` read 1 on all 96 (the second ANT each time), no other count moved, no new error.
- I read the entries back to 14:30 on 17 Nov in full and, of the older ones, only the "Would prove this review wrong" lists (the file is 250 KB, more than one session can read with the data).

**Strategy: v9 has no closed trade and 1 open. v8 ended at 5 closed, 1 win, -4.96% a trade (-0.1083 SOL). Nothing here is a hint yet.** All versions: 30 closed, 8 wins on seven tokens, -6.17% a trade, -0.8660 SOL. Equity 4.1568 SOL at 14:30 (-16.86%) with Leonida marked at +7.2% on price. Max drawdown 19.43% on closed trades, unchanged; the lowest marked equity since the last review was 4.1277 SOL, above the record low of 4.0129. The 22% line was not reached. SOL $74.3 to $75.0.

| # | Token | Opened (UTC, 19 Nov) | Age | Trades in the hour before | 1-hour change at entry | 6-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|---|
| 30 | DIGS (v8) | 05:20 | 21.7 days | 748 | +11.1% | +7.8% | +11.9% | 6-hour limit, price at -1.4% | -4.40% |
| 31 | Leonida (v9) | 14:15 | 1.54 days | 2,067 | +16.0% | +95.1% | +7.2% | open at +7.2% on price (14:30) | |

- DIGS, trade 30 (address `9QT8K...`). Best +11.9% at 06:50, back at -0.4% forty minutes later, between -2.0% and +7.8% for the next four hours (+7.8% at 10:50, half an hour before the limit) and sold at 11:20 with the price 1.4% under the entry: the loss is the costs plus that. It never came within 8 points of the first target or within 6 of the stop. It is the third 6-hour exit (the three cost 0.0686 SOL together) and the seventh loser that was up 10% or more first.
- Leonida, trade 31, is the first v9 trade and it is not the Leonida of trades 3, 10 and 25 (`BWJfB...`). This address is `9rbKk...`, launched about 01:15 on 18 Nov, never traded by the bot. The replay knows it three times: with the 3-hour floor it was bought at 13:15 on 18 Nov at 12 hours old and stopped (-15.7%, the fourth entry of the 1-day floor's forward check); with buy pressure at 1.1 it was bought at 02:20 today and stopped (-14.8%); with `min_volume_accel` at 1.0 it was bought at 12:35 today and made +23.3% (best +42.0%). The bot bought after that run: the price at 12:10 was 54% under the later entry and rose 118% in the two hours to the buy. The 1-hour change read +50% to +79% from 12:55 to 13:35, stayed over the cap until 14:05, was held back at 14:10 by `volume_accel` at 1.195 against the 1.2 needed, and read +16.0% at 14:15 with buy pressure 1.50 and `volume_accel` at 1.203. Pool $129k. This is the "fell into the band from above the cap" shape again (JESTER won with it, bul and Rings lost). It counts in the 1-to-3-day row and in the +30%-or-more group of the 6-hour test. The highest volume-to-pool ratio it showed in the six hours before the entry was 25, so the cap did not touch it and the v8 and v9 trades stay one series.
- The signal ended a gap of 8.9 hours (DIGS 05:20 to Leonida 14:15). The 12-hour rule was not met at any point, so no threshold was relaxed.
- Funnel, 1,485 universe-token checks: `h1_weak` 978 (66%), `h6_down` 194, `txns_h1` 84, `buy_pressure` 66, the held token 61, a token in its cooldown 40, `h1_overheated` 30, `h24_dumped` 24, `volume_accel` 6, `m5_dropping` 1, signal 1. Seventeen different tokens were inside the universe; their median 1-hour change was -0.4% and 30% of readings were at +2% or better.
- Stops: no new one. All 19 lost, average -17.87%, total -1.5527 SOL, the price at the stop cycle averaging -15.6%. The eight trailing exits made +0.7553 SOL.
- Left on the table: the average trade was up 16.5% at its best and realised -6.17%.
- LP locked: DIGS 99.9%, lost. Under 50%: 0 wins of 4, unchanged. At 50% or more: 8 wins of 26.

**The finding of this review: both ANT pools read $0 from the cycle they were found until the cycle their age read 1.00 day, and the repo cannot say why.**

- The second ANT (`8J2VU...`) was put on the watchlist at 21:20 on 18 Nov by page 1 of GeckoTerminal's trade-count list, which only passes on a pool with a reserve of $30k or more. `data/state/watchlist.json` then shows it with a pool of $0 on 48 cycles in a row. At 01:20 on 19 Nov it reads $123k, with an age of 1.00 day and $47.6M of 24-hour volume, and it is in every snapshot from that cycle on. It has no snapshot row before 01:20.
- The first ANT (`ELR9i...`) did the same on 17 Nov: found by the same page at 13:00, $0 on 47 cycles, $121k at 16:55 with an age of 1.00 day. The two were found 3.9 and 4.0 hours before they appeared.
- The last two entries wrote that each ANT "turned a day old" and passed the universe from then on. That is true and it missed this: the bot had no reading of either pool before that cycle. The `u:too_young` test never saw them.
- It is not the bot's age rule. `bot/run.py` writes the watchlist's `liq` from the DexScreener view before any test is applied, and nothing in that path looks at age. So for four hours DexScreener's batch call answered for these tokens with a pool that had a price and no liquidity, and from the cycle the traded pool was 24 hours old it answered with that pool. Two readings fit and the data cannot separate them: the batch call (one pool per token, as the 13 Nov entries found) returned a different, empty pool of the same token until the traded pool was a day old; or DexScreener gave no liquidity figure for the traded pool during its first day.
- How common: in the 215 versions of the watchlist from 21:00 on 18 Nov to 14:35 today, the second ANT is the only token that read $0 for three cycles or more and $30k or more afterwards. Of the 104 GeckoTerminal-found tokens on the watchlist in those hours, 17 read $0 at their first reading in that window, the second ANT among them.
- What it touches. (1) The count of pools "that go to $0 and never come back" reads a $0 as an emptied pool. For the tokens counted that still fits (each read $30k or more first, then $0, and none has returned), and the second ANT was never one of them, so the 17 Nov test is not met by the letter. But a $0 reading is now known not to mean an empty pool in every case. (2) A pool of this kind shows up with a full day of volume on the first cycle the 1-day floor allows a buy. The only thing that kept it out of the universe today is the cap added at 06:30.
- Not fixed, because there is nothing established to fix: I cannot call the APIs from a review and two tokens of one kind are the whole case. What I can do is make the next case measurable. See "Changed".

**The cap's first eight hours (v9, `universe.max_volume_h24_to_liquidity` 150).**

- It has blocked one token on 96 cycles: the second ANT, at 250 to 357 times its pool. With the cap removed the replay makes the same trades (the token's buy pressure stayed at 1.07 to 1.10 against the 1.2 needed), so the cap has changed no trade so far.
- Its pool is still there after 13.2 hours inside the universe's other limits: $120k to $156k, 5,650 to 6,080 trades in every hour, the price up 72% since 01:20 in small steps.
- New: the pool lost $36k (23%) between 06:35 and 06:40 and $34k (22%) between 12:35 and 12:40, with the price up 0.3% and 2.8% on those two cycles. A sale that size moves the price; this did not, so it is liquidity taken out of the pool, twice, six hours apart to the cycle, each time back to $120k. Nothing else in the 161 readings moves the pool by 10% in a cycle. If it is a schedule, the next steps are at 18:35 to 18:40 and 00:35 to 00:40.
- The test "never read under half from one cycle to the next" stands (the lowest is 0.77 of the cycle before). The 24-hour mark for the first blocked token is 06:40 on 20 Nov.
- No token inside the universe between 100 and 150 times. The highest ordinary ratio since 06:30 was 34 (ANTS, `ejrz9...`, another token), then SHIT 29 and Leonida 25; the median is 7.0.
- A third address named ANT (`Cx5hb...`) was found at 11:35 with a $75k pool and read $0 at 12:10.

**What the last reviews asked, answered.**

- The 6-hour change (candidate `entry.h6_change_min_pct` 0 to 30): 2 of the 6 the test needs. DIGS was bought at +7.8% and lost. Closed entries opened after 22:30 on 17 Nov: under +30%, 2 (BAWSAQ -15.03%, DIGS -4.40%), no winner, -9.71%; +30% or more, 2 (HOGE, JESTER), 1 winner, +6.15%; Leonida at +95.1% is open in the second group. On all real trades: under +30%, 15 on 10 tokens, no winner, -15.34%; +30% or more, 15 on 11 tokens, 8 winners, +3.00%. The pattern has held on both new trades under +30% and the test is two thirds short of its count. Not acted on; the number stays at 30.
- The 300-trade floor's second test (2 winners or fewer in the first 10 closed trades on tokens 3 days or older): 2 winners in 9 after DIGS. One trade to go. If it loses, that test reads "no improvement on the trades the floor keeps" while the forward check closed in the floor's favour on 18 Nov; two tests that disagree are no ground for a change, and the entry that records the tenth trade should say so.
- What the floor blocks, carried on past the closed check (entries on 150 to 299 trades, wide replay, tokens 3 to 30 days old, opened after 06:45 on 16 Nov): 15 closed, 5 wins, -6.24% a trade; the bot's own trades on tokens 3 days or older over the same days are 9, 2 wins, -4.69%. The five since the check closed at 10: NIO +0.8%, FOOD -15.3%, XCAT -59.5%, BUTTHOLE +18.1% (10:00 today, 272 trades; outside the bot's universe, its pool is not quoted in SOL or a stablecoin), Rings +58.5%. XCAT is the entry the last review listed as open at +3.1%: its pool went from $68k to $42k in one cycle at 07:15 with the price 58% lower, and the replay sold on the liquidity rule. It was outside the bot's universe (24-hour volume under $100k) as well as under the floor.
- Rings at 13:55 today (`65iH8...`, the token of trades 11 and 16, 159 trades in the hour) is the one the live universe would have bought with the floor at 150: +19.9% at entry, +76% in the one cycle to 14:15, half sold there, +58.5% for the trade. From 14:00 to 14:10 it passed every live test except the floor, with 247, 276 and 287 trades; at 14:15 its 1-hour change read +121%. The floor kept the bot out of the largest winner the replay has, by 13 trades, and out of XCAT. One of each; the band as a whole still loses more a trade than the trades the floor keeps.
- `min_volume_accel` at 1.0 (the test of 22:30 on 18 Nov: three or more added trades on three or more tokens within three days, averaging better than the live trades): two added so far on two tokens, HOGE 11:35 (stop, -15.8%) and Leonida 12:35 (+23.3%), +3.8% a trade. It also buys DIGS at 07:20 instead of 05:20 (-5.3% against -4.3%) and misses the live Leonida entry, which falls in the cooldown. The window closes at 22:30 on 21 Nov.
- The other modest relaxations since 05:20 (no rule is met; this is the record): buy pressure at 1.1, `h1_change_min_pct` 1 or 0, `h6_change_min_pct` -10, `h1_change_max_pct` 35, `m5_change_min_pct` -5, `h24_change_min_pct` -40, `min_liquidity_usd` 40k, `max_age_days` 35 and the cooldown at 6 hours add nothing new. `--no-cooldown` adds nothing.
- The 1-day floor's forward check: 5 of 10, unchanged. No entry on a token under a day old since SHIT at 15:20 on 18 Nov.
- Tokens 1 to 3 days old since v6: 5 of 15 closed, 2 wins, -0.26% a trade, unchanged; Leonida is the sixth, open. Stops in the band: 3 of 5.
- Trailing exits: none new (3 of 10).
- `python3 -m bot.replay` reproduces DIGS within 0.2 points of the journal and Leonida's entry: 23 closed on 14 tokens, 9 wins, +0.49% (it was +0.70% on 22). `--baseline`: every eligible cycle 21,117 on 50 tokens, -4.66% (was -4.59%); cycles the entry rules passed 98 on 14, +4.56%; the first passing cycle of each run 52 on 14, 44% wins, +2.02% (was +2.39% on 49). The last row has fallen again.
- Pools that go to $0 in one cycle (walked from the 99 versions of `data/state/watchlist.json` since 06:30): 22 in 8 hours, about 66 a day (it was 60). Twenty-two addresses under ten names (PIPI six times, DCTY four, APOCRYCOIN three, Sparrow and a token with a blank name twice each, GTA6, CRIME, DCTC, BABYDOG, ANT), pools of $56k to $159k, 21 found by GeckoTerminal's most-traded-by-volume list (pages 2 to 8) and one by page 5 of the trade-count list, gone 5 to 65 minutes after being found. None had passed the universe, none gave a signal: 153 so far, none ever tradable. Five more pools read under half on the next cycle without going to zero (XTO from $718k to $2k, C/ACC, a GTA address from $77k to $1.7k, VI from $79k to $6.5k, a PIPI address); none was inside the universe.
- Discovery: the 17 tokens inside the universe came from `boosts_top` 4, GeckoTerminal before pages were labelled 4, `profiles_latest` 3, `gecko:tx6` 2, and one each from a trending meta, `gecko:trend2`, `gecko:tx4` (HOGE) and `gecko:vol7` (NVDA). `api_calls` never passed 47, 429 errors on two cycles, and the watchlist peaked at 215. None of the conditions for reopening the pages is met.

**Changed. No rule: rulebook v9 stays. One diagnostic in `bot/run.py`, which changes no decision, and its test.**

1. `bot/run.py`, step 5c. When GeckoTerminal lists a token again on the current cycle (so it reports a pool over its $30k reserve floor right now) while the pool DexScreener's batch call returns for that token has read under the watchlist floor on every cycle since the token was found, at least 30 minutes ago, the bot makes one full pool lookup and writes what it gets to `data/debug/no_liquidity_pairs.json`: the batch call's pool (pair, DEX, quote, liquidity, age, trades in the hour, 24-hour volume), how many pools the batch call returned for the token, and every pool the full lookup knows. Each token once, eight tokens at most, at most one extra API call on a cycle. It is built like the quote-token diagnostic of 13 Nov, sits inside a `try`, and logs `no-liquidity sample: ...` if the lookup fails.
2. Why these conditions. "Listed again by GeckoTerminal on this cycle" makes both sources speak at the same time, so a stale list is not mistaken for a hidden pool. "Under the floor since it was found" leaves out the ordinary emptied pool, which reads $100k first and $0 after. "At least 30 minutes" leaves out the first reading, where GeckoTerminal's list can simply be a few minutes behind. The second ANT would have met all three at its first relisting, about 22:00 on 18 Nov, provided it was still on that page of GeckoTerminal's list (the page is read every 40 minutes).
3. `tests/test_bot.py`: one test added, a scripted market where GeckoTerminal keeps listing two tokens, one whose batch pool is empty from the start though a $120k pool exists, and one that had a pool and lost it. It checks that only the first is recorded, once, not before 30 minutes, with one extra call, that a failing lookup is logged and stops nothing, and that nothing is bought. It fails on the old code and on each of the three conditions taken out. 45 tests pass.
4. No version bump (plumbing). No change to the rulebook, the README or the workflow.

- Why no rule change. v9 has no closed trade. No test set by an earlier entry has reached its count: the 6-hour change stands at 2 of 6, the 1-day floor's forward check at 5 of 10, the 1-to-3-day band at 5 of 15 trades and 3 of 5 stops, the trail at 3 of 10, the 300-trade floor's second test at 9 of 10, the volume test at 2 of 3. There was a signal 8.9 hours after the one before and another is open now, so the 12-hour rule gives no ground for a relaxation. The record is 30 trades, 8 winners, -6.17% a trade, no edge shown, and it has been through four versions in six days; the useful thing a review can do for it now is leave the rules alone until the counts come in.

**After the review's cut at 14:30: the first live cycles of the new code, and the first signal RugCheck has turned down.**

- Pushed at 14:44 UTC and picked up by the 14:45 cycle. 14:45 and 14:50: v9, no errors, `api_calls` 47 on both (47 on the two cycles before), `batch_miss` 20 and 21, `universe_ok` 17, `u:volume_to_liquidity` 1, no signal. No token met the diagnostic's conditions, so `data/debug/no_liquidity_pairs.json` does not exist yet. Leonida was read and carried on as usual (+13.5% on price at 14:50).
- At 14:35, before the push, the entry rules passed NVDA (`NVDAV...`, an Orca pool against USDC of $129k, 10.7 days old, on the watchlist since 17 Nov from `gecko:vol7`) and the safety check refused it: `safety:rugcheck_score` 1, the first `safety:*` row in 1,757 cycles. RugCheck's answer parsed: `score_normalised` 81 against the 30 allowed, LP locked 0%, four risks at level `danger` (mint authority still enabled, permanent control enabled, freeze authority still enabled, low liquidity) and one `warn`. No trade, as the rule says. The token trades at $153 to $157, so it is a tokenised Nvidia share, and the signal came five minutes after the New York open (14:30 UTC): +2.5% in one cycle, trades in the hour from 286 to 512. An issuer that can mint and freeze is what the screen is there to refuse, whatever the asset behind it, and the safety section is not for loosening.
- Two things follow for reading the record. The replay has no RugCheck, so `python3 -m bot.replay` will show an NVDA entry at 14:35 that the bot did not make, and `--baseline` will count it as a first signal: leave it out when comparing the replay with the journal. And for the 12-hour rule this was a signal by the letter (the entry and universe filters passed it), but it could never become a trade; the answer is cached for 6 hours, so any NVDA signal until 20:35 is refused without a call. A review that counts hours without a signal should say whether it counted this one.

**For the next review.**

- First: cycles, errors, and `data/debug/no_liquidity_pairs.json`. If it exists, read each entry: does `pools` hold a pool of $30k or more that `batch_pool` is not? What are that pool's age and the batch pool's? Check that `api_calls` stayed under 50 and that no `no-liquidity sample` error repeats.
- The second ANT (`8J2VU...`): whether its pool lost about a fifth again at 18:35 to 18:40 and 00:35 to 00:40, what the pool is at 06:40 on 20 Nov (the 24-hour mark for the cap's first blocked token), and whether it ever read under half from one cycle to the next.
- Leonida, trade 31 (`9rbKk...`): record the exit. It is the sixth trade of the 1-to-3-day band, in the +30%-or-more group of the 6-hour test, and the first v9 trade. If it trails out: the trail level, the fill, and what `--set exit.trailing_stop_pct=10` gives (it would be the fourth of 10).
- The 6-hour change: 2 of 6 under +30%, no winner. Keep the two groups apart; do not move the number.
- The 300-trade floor's second test: 2 winners in 9, one trade to go on a token 3 days or older.
- `min_volume_accel` 1.0: two added trades on two tokens since 22:30 on 18 Nov; the window closes at 22:30 on 21 Nov.
- The 1-day floor's forward check: 5 of 10. The trail: 3 of 10.
- Drawdown: 19.43% on closed trades against the gate's 25%. If it passes 22%, say so at the top of the entry.
- Pools that go to $0: the count per day (66 now) and whether any had passed the universe (none of 153). `batch_miss` less the never-seen tokens: 2 to 9 now, the line is 15.
- Any token inside the universe between 100 and 150 times its pool, and every token the cap blocks.
- NVDA (`NVDAV...`): how many `safety:rugcheck_score` rows it produced, and whether any other token is refused. If tokenised shares keep passing the entry rules at the New York open, that is a pattern to write down, not a reason to touch the safety section.
- Follow tokens by address, not by name. Everything under "For the next review" in the earlier entries still stands.

**Would prove this review wrong.**

- The diagnostic was not worth its code if a week from now (26 Nov) `data/debug/no_liquidity_pairs.json` is missing or holds no entry where the full lookup shows a pool of $30k or more that the batch call did not return. Then take step 5c out and write that the ANT readings were DexScreener's own figures. It costs too much if `api_calls` passes 55 or a `no-liquidity sample` error appears on more than a handful of cycles a day.
- If it does show such a pool, the bot has been blind to live pools behind dead ones, and that is a real bug: give a token GeckoTerminal lists a full pool lookup in `refine_pools` when its batch pool is under the floor, judge it on the deepest allowed pool, and redo the count of pools "that go to $0" on the corrected readings before trusting it again.
- Reading the two steps in the second ANT's pool as liquidity taken out on a schedule is wrong if neither 18:35 to 18:40 nor 00:35 to 00:40 shows a fall of 15% or more in the pool with the price steady (one cycle either side allowed).
- Waiting on the 6-hour change is wrong by the test of 22:30 on 17 Nov, unchanged: 0 winners of 2 so far, four entries to go.
- Not treating Rings at 13:55 as a case against the 300-trade floor is wrong if the next five entries on 150 to 299 trades (wide replay, 3 to 30 days old) hold three or more winners and none ends on the liquidity rule. That would make 6 of the last 10, and the floor's forward check should then be reopened, not the floor changed on the spot.
- Leaving the rules alone is wrong by the tests the earlier entries set, which are unchanged: the cap (06:30 today), the 5% trail (22:30 on 16 Nov), tokens 1 to 3 days old (12:30 on 16 Nov, narrowed at 14:30 on 17 Nov), the 1-day floor (14:30 on 17 Nov), `min_volume_accel` (22:30 on 18 Nov).
- The health verdict is wrong if the gap between cycles grows past 15 minutes or skipped cycles become regular.

### v9, 2026-11-19 06:30 UTC review: a token whose 24-hour volume is more than 150 times its pool is outside the universe (a second ANT met the test set on 17 Nov)

**Health.** 1,659 cycles since launch, 484 on v8, 99 since the last review. Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 5.2. No cycle was skipped, so no message to Ajeeb. Two extra cycles (23:30:24 and 04:25:58, 36 and 47 seconds after the one before; both triggers fired; nothing was held either time). The newest cycle was 1.9 minutes old when the review started, so no `.kick`. No error in any of the 99 cycles. `api_calls` 44 to 49 (median 46), `allowed_pool_used` 2 or 3, universe 14 to 18 tokens a cycle (median 16), `u:too_young` 12 to 24 (median 18), watchlist 213 to 245 (cap 300; 215 now). RugCheck ran for the one signal and the answer parsed: DIGS `score_normalised` 1, no risks, LP locked 99.9%. The saved sample still matches what `bot/rugcheck.py` reads (`score_normalised`, `risks[].level`, `lpLockedPct`). No `safety:*`, `skip:*` or `suspect_price` rows. No bug found.

- `batch_miss` 11 to 17 a cycle (median 13), over the 15 single lookups on 3 of the 99 cycles. Never-seen tokens on the watchlist: 8 to 10 (median 9). `batch_miss` less the never-seen tokens: 1 to 9 (median 3), the line is 15.
- The day's limits: the day started at 4.1523 SOL and has used 1 of its 10 new trades.
- I did not read the log entries older than 16 Nov 12:30 in full this time (the file is too long for one session); the tests they set are carried in the later entries' "For the next review" lists, which I did read.

**Strategy: v8 ends at 4 closed trades, 1 win, -5.10% a trade (-0.0900 SOL), and 1 open. Four trades are not a hint.** No trade closed since the last review. All versions: 29 closed, 8 wins on seven tokens, -6.23% a trade, -0.8477 SOL. Equity 4.1752 SOL at 06:30 (-16.50%) with DIGS marked at +7.5% on price. Max drawdown 19.43% on closed trades, unchanged; the lowest marked equity since the last review was 4.1244 SOL, above the record low of 4.0129. The 22% line was not reached. SOL $72.6 to $74.7.

| # | Token | Opened (UTC, 19 Nov) | Age | Trades in the hour before | 1-hour change at entry | 6-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|---|
| 30 | DIGS (v8) | 05:20 | 21.7 days | 748 | +11.1% | +7.8% | +7.5% | open at +7.5% on price (06:30) | |

- DIGS, trade 30 (address `9QT8K...`, the same as trade 23, the stop of 17 Nov; its cooldown ended at 04:50 on 18 Nov). Pool $62.7k, buy pressure 1.21 against the 1.2 needed, volume 2.8 times its six-hour average. Lowest reading -5.3%. It is the ninth trade for the 300-trade floor's second test (2 winners in 8) and the second entry in the under-+30% group of the 6-hour test. Open trades count for nothing yet.
- The signal ended a gap of 13.3 hours (JESTER 16:05 to DIGS 05:20). The 12-hour mark passed at 04:05 with no review in session; at this review the last signal is 1.2 hours old, so the 12-hour rule is not met and no threshold was relaxed.
- Funnel, 1,613 universe-token checks: `h1_weak` 959 (59%), `buy_pressure` 147, a token in its cooldown 141, `h6_down` 134, `txns_h1` 105, `h24_dumped` 64, `h1_overheated` 33, `m5_dropping` 15, the held token 14, signal 1. Nineteen different tokens were inside the universe; their median 1-hour change was -0.1% and 36% of readings were at +2% or better.
- Stops, trailing exits, left on the table, LP locked: no closed trade, so the figures in the 22:30 entry below stand to the digit (19 stops, all lost, -17.87%; 8 trailing exits, +0.7553 SOL; average best +16.7% against -6.23% realised).

**The finding of this review: a second machine-traded pool sat inside the universe for five hours, and the test written for that on 17 Nov is met.**

- The 22:30 entry of 17 Nov described ANT (address `ELR9i...`): $47M to $48M of 24-hour volume through a pool of $121k to $131k, 5,500 to 6,000 trades in every hour, the price up in small steps, inside the universe on 58 cycles in a row, then a pool of $0 in one cycle. It wrote: not capping volume against the pool was wrong "if a second token with 24-hour volume over 100 times its pool passes the universe for an hour or more ... Then add the cap to the universe section, at 100 unless that entry's data shows a tradable token above it, and write the test for it."
- The second one is here, and it carries the same name on a new address (`8J2VU...`, found by page 1 of GeckoTerminal's trade-count list at 21:20 on 18 Nov). It turned a day old at 01:20 today and has passed the universe on all 64 cycles since: pool $123k to $155k, 24-hour volume $43.0M to $47.6M (278 to 386 times the pool), 5,500 to 6,050 trades in every hour, the price up 24% over 5.2 hours in small steps. The universe's median is 4.8 times, its 99th percentile 99.
- What kept the bot out is the same accident as on 17 Nov. `buy_pressure` blocked it on 55 cycles (1.06 to 1.11 buys per sell against the 1.2 needed) and `h1_weak` on 9. `volume_accel`, the test after `buy_pressure`, would have failed on every cycle as well (0.59 to 1.07 against 1.2; it rose on each of the last five cycles). It passed the 6-hour, 24-hour, 5-minute and trade-count tests on every cycle. RugCheck was never asked, because it is only asked after a signal. Its pool is still there at 06:30. A buy would put about 0.41 SOL, 10% of equity, into a pool whose only precedent on this record was emptied in one cycle, with the account 19.4% down against a 25% line.
- Why not 100. The 17 Nov entry made 100 conditional on the data, and the data does show tradable tokens above it. Four tokens have ever been over 100 inside the universe: the two ANTs (314 to 400 and 278 to 386) and, on 13 and 14 Nov, inuhao (62 cycles at 101 to 116) and FOOD (15 cycles at 100 to 107). The last two were ordinary tokens on a busy day: a buy at any of those 77 cycles made +10.2% on average (inuhao +10.9%, 41 winners of 62; FOOD +7.3%, 9 of 15), and FOOD was still in the snapshots five days later. A cap at 100 would have shut out both for nothing.
- Why 150. Nothing on the record sits between 116 and 278, so every number from about 120 to 270 gives the same record and the choice cannot be read off it. 150 is a judgment: a third above the highest ordinary reading, about half the lowest reading of either ANT. I did not try several and pick; I say so because the next review cannot check that.
- What it changes on the record: nothing. `python3 -m bot.replay` with v9 gives the same 22 closed trades and the open DIGS as with v8, to the hundredth, at any cap from 50 to 200, with the age floor at 1 day or at 3 hours. The highest ratio at any real entry is 40 (HOGE on 16 Nov, a winner); the next are 28 and 20. `--baseline` is unchanged at 150 (the ANT positions were never closed in it: the first token vanished and the second is too recent). This is a risk limit against a total loss the stop cannot help with. It is not a claim about returns and it will not show up in the expectancy.

**Changed: rulebook v9, universe section only. New key `universe.max_volume_h24_to_liquidity` = 150. A tightening.**

1. `rulebook.json`: the key, `version` 9, `updated`, `notes`.
2. `bot/strategy.py`: `universe_reject` returns `volume_to_liquidity` when 24-hour volume is more than the cap times the pool. It is the last universe test, so the funnel counts under it only tokens that passed everything else (`u:volume_to_liquidity`). A rulebook without the key applies no cap.
3. `bot/replay.py`: `--wide` drops the cap along with the other universe numbers. To see what the cap blocks: `python3 -m bot.replay --set universe.max_volume_h24_to_liquidity=1000000`.
4. Tests: 2 added (the rule at, over and far over the cap, and with no key; a scripted market where a pool turning over at 2.5 times the cap passes every entry rule and is not bought, not sent to RugCheck and still recorded, while a token just under the cap is bought). Both fail on the old code. 44 pass.
5. README: the strategy paragraph.

- What it does to the open tests: nothing. Entry, exit, portfolio, safety, costs and discovery are untouched and no trade on the record is affected, so the tests the earlier entries set carry on across v8 and v9 as one series: the 6-hour change, the 1-day floor's forward check, the 1-to-3-day band, the 5% trail, the 300-trade floor's second test. DIGS (trade 30) was opened under v8, is labelled v8 and is managed as before. The report will show v9 as a new row; read v8 and v9 together.
- This is the fourth version in four days and none has reached 30 trades. I made the change anyway because it was written down before the event with its trigger, the trigger was met by a different address 31 hours later, it only removes tokens, and it leaves every measured trade where it was.

**What the last reviews asked, answered.**

- The 6-hour change (candidate `entry.h6_change_min_pct` 0 to 30): 1 of 6 closed under +30% (BAWSAQ, loss), unchanged; DIGS at +7.8% is open in that group. At +30% or more: 2 closed, 1 winner, +6.15%. Not acted on; the number stays at 30.
- The 1-day floor's forward check (`--set universe.min_age_days=0.125`): 5 of 10, unchanged. No entry on a token under a day old since SHIT at 15:20 on 18 Nov.
- The 300-trade floor's second test: 2 winners in 8; DIGS is the ninth.
- Trailing exits: none new (3 of 10). `suspect_price`: no row.
- SWJ 16:30 with `entry.h6_change_min_pct=-10`: 6-hour limit, -6.5% (best +2.2%). That setting has added three trades in six days for -0.73% a trade against +0.70%.
- What the modest relaxations add since JESTER (no rule is met, so this is the record, not a case): `min_buy_sell_ratio_h1` 1.1 adds a Leonida at 02:20 (1.04 days old, stop, -14.8%) and buys DIGS fifteen minutes earlier at the same price; buy pressure at 1.1 has now added eight trades since 14:30 on 17 Nov, seven of them stops. With `min_txns_h1` 150 on the wide record: THUG 14:15 on 18 Nov, stop, -14.5% (a $37k pool); XCAT 05:10 (151 trades) is open at +3.1%. `min_volume_accel` 1.0, `h1_change_min_pct` 0 or 1, `h1_change_max_pct` 35, `m5_change_min_pct` -5, `h24_change_min_pct` -40, `min_liquidity_usd` 40k and `max_age_days` 35 add nothing new. With `min_volume_accel` 1.0 the bot would have been in DIGS's cooldown at 05:20 and missed today's trade.
- The cooldown: `--no-cooldown` adds HOGE at 23:45 on 18 Nov, 8.7 hours after its stop: another stop, -14.8%. Four cases for keeping it, none against.
- `python3 -m bot.replay` reproduces the DIGS entry: 22 closed on 14 tokens, 9 wins, +0.70%, DIGS open. `--baseline`: every eligible cycle 19,566 on 49 tokens, -4.59% (was -4.33%); cycles the entry rules passed 95 on 14, +4.83%; the first passing cycle of each run 49 on 14, 47% wins, +2.39% (was +2.75% on 48). The one first signal added is HOGE at 23:45, the stop the cooldown kept the bot out of.
- Pools that go to $0 in one cycle (walked from the 99 versions of `data/state/watchlist.json` since 22:30): 20 in 8 hours, about 60 a day (it was 36). Twenty addresses under nine names (DCTY four times, CRIME, NASDUCK and BUNC three each, GTA6 and After twice, KII, BABYDOG, can), pools of $70k to $160k, all found by GeckoTerminal's most-traded-by-volume list (pages 3 to 8). None had passed the universe, none gave a signal: 131 so far, none ever tradable.
- Sixteen more pools read under half on the next cycle without going to zero. One of them had been inside the universe, which is new: VTC on the address `DngzJ...` (1.9 days old) read $517k at 23:35, $128k at 23:40 with the price 93% lower, passed the universe on six cycles in that state (`h1_weak` each time, with a 1-hour change of -93%) and read $2.9k at 00:10. No entry rule could have bought it after a fall like that. Five addresses carried the name VTC in these 8 hours; the one that stayed in the universe for 81 cycles (`3tjPC...`, 5 days old) fell 78% in the hour to 05:10 after six and a half hours of 11,200 to 20,700 trades an hour that were nearly all sells (0.03 to 0.07 buys per sell), and never came near a signal. Its volume was 30 to 69 times its pool over those hours, so the new cap would not have touched it; the 1-hour change and `buy_pressure` did the work.
- Discovery: the 19 tokens inside the universe came from `profiles_latest` 5, GeckoTerminal before pages were labelled 4, `boosts_top` 4, and one each from a trending meta, `gecko:trend2`, `gecko:tx1` (the second ANT), `gecko:tx4` (HOGE), `gecko:tx6` (the VTC above) and `gecko:vol7` (NVDA). `api_calls` never passed 49, no 429, and the watchlist peaked at 245. None of the conditions for reopening the pages is met. Note that the first page of the trade-count list found the ANT pool: cutting the deeper pages would not have kept it out.

**First live cycle (06:40 UTC).** Pushed at 06:39 UTC and picked up by the 06:40 cycle: v9, no errors, `api_calls` 45 and `batch_miss` 12 (both as on the cycle before), `u:volume_to_liquidity` 1, `universe_ok` 15 (16 on the cycle before), `buy_pressure` 1 (2 before: the second ANT was one of them), `h1_weak` 12 and `h6_down` 1 unchanged, no signal. DIGS was read and carried on as usual. v9 trades start from the 06:40 cycle.

**For the next review.**

- First: cycles, errors, and the first v9 cycles: `u:volume_to_liquidity` should read 1 while the second ANT is on the watchlist and a day old or more, and `universe_ok` one lower than it would have been. No other count should move.
- The second ANT (`8J2VU...`): what its pool did. Read it from `git log -- data/state/watchlist.json` and the snapshots. Also list every token the cap blocks (rows that pass the universe with the cap removed and have `vol_h24 / liq_usd` over 150) and what happened to each within 24 hours.
- Any token inside the universe between 100 and 150 times: name it and say what it did. That is the band where the number could be wrong in either direction.
- DIGS, trade 30: record the exit. Under +30% for the 6-hour test (would be 2 of 6), ninth for the 300-trade floor's second test (a win makes 3 of 9 and passes it), "3 days or more" row.
- The 1-day floor's forward check: 5 of 10. The trail: 3 of 10. The 1-to-3-day band: 5 of 15 trades, 3 of 5 stops.
- Drawdown: 19.43% on closed trades against the gate's 25%. If it passes 22%, say so at the top of the entry.
- Pools that go to $0: the count per day (60 now) and whether any had passed the universe (none of 131). `batch_miss` less the never-seen tokens: 1 to 9 now, the line is 15.
- Follow tokens by address, not by name. Everything under "For the next review" in the earlier entries still stands.

**Would prove this review wrong.**

- The cap is wrong, and should come out, if the second ANT's pool is still there and of the same size a week from now (26 Nov) having never read under half from one cycle to the next: then the pattern is a market maker on a real token and the first ANT was one case. It is also wrong if, of the first five different tokens it blocks, three or more are still inside the universe's other limits 24 hours after their first blocked cycle with a pool at least half what it was.
- The number is too low if a token blocked between 150 and 250 times would have given a signal and the replay with the cap removed shows that trade a winner, twice on two tokens. Then raise it to 250. It is too high if a token at 100 to 150 times passes the universe for an hour or more and its pool then reads $0 or under a tenth within a day. Then lower it to 120, the lowest number that still leaves inuhao and FOOD in.
- It was not needed if no token is ever blocked by it again in two weeks: then it cost nothing and did nothing, and that should be said.
- Reading the open tests across v8 and v9 as one series is wrong if any v9 trade is on a token whose ratio was over 150 at any cycle in the six hours before its entry (it cannot be at the entry itself): then the cap changed which trades were made, and the series has to be split there.
- Waiting on the 6-hour change is wrong by the test of 22:30 on 17 Nov, unchanged (0 winners of 1 so far; DIGS open).
- Leaving the entry, exit and portfolio alone is wrong by the tests the earlier entries set, which are unchanged: the 5% trail (22:30 on 16 Nov), tokens 1 to 3 days old (12:30 on 16 Nov, narrowed at 14:30 on 17 Nov), the 1-day floor (14:30 on 17 Nov).
- The health verdict is wrong if the gap between cycles grows past 15 minutes or skipped cycles become regular.

### v8, 2026-11-18 22:30 UTC review: no rule change, no code change (HOGE stopped, JESTER the best trade so far; no test has reached its count)

**Health.** 1,561 cycles since launch, 386 on v8, 97 since the last review. Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 5.3. No cycle was skipped, so no message to Ajeeb. One extra cycle (17:30:19, 56 seconds after the one before; both triggers fired; nothing was held at the time). The newest cycle was 1.9 minutes old when the review started, so no `.kick`. One error in the 97 cycles: GeckoTerminal 429 on page 1 of the volume list at 22:20, not repeated on the two cycles after it. `api_calls` 37 to 49 (median 44), `allowed_pool_used` 2 to 5, universe 14 to 16 tokens a cycle (median 15), `u:too_young` 10 to 25 (median 18), snapshot rows 57 to 69 (cap 120), watchlist 181 to 245 (cap 300; 243 now). RugCheck ran for the one signal and the answer parsed: JESTER `score_normalised` 1, no risks, LP locked 100.0%. The saved sample still matches what `bot/rugcheck.py` reads (`score_normalised`, `risks[].level`, `lpLockedPct`). No `safety:*`, `skip:*` or `suspect_price` rows. No bug found, so no change to `bot/`. 42 tests pass.

- `batch_miss` 7 to 18 a cycle (median 11), over the 15 single lookups on 12 of the 97 cycles. Never-seen tokens on the watchlist: 4 to 9 (median 6; seven of the eight on it now are from `profiles_latest`). `batch_miss` less the never-seen tokens: 2 to 9 (median 5), the line is 15.
- The day's limits: the day started at 4.1668 SOL, has used 3 of its 10 new trades and stands at -0.35% against the 10% limit.
- JESTER's first target was a jump of 25.8% in one cycle (16:40 to 16:45), which is past the line where the bad-print guard asks for volume. $34.0k traded in those five minutes against about $4.9k needed for a pool of $80k, so the reading was acted on in the same cycle, rightly: the next seven readings were all higher.

**Strategy: v8 has 4 closed trades, 1 win, -5.10% a trade (-0.0900 SOL). Four trades are not a hint.** All versions: 29 closed, 8 wins on seven tokens, -6.23% a trade, -0.8477 SOL. Equity 4.1523 SOL (-16.95%), nothing open. Max drawdown 19.43% on closed trades (4.0284 SOL after HOGE's stop at 15:05); the lowest marked equity was 4.0129 SOL at 16:20 (-19.74%). The line the last entry set for saying so at the top is 22% and it was not reached; the proof gate's line is 25%, 3.75 SOL. SOL $72.5 to $74.3.

| # | Token | Opened (UTC, 18 Nov) | Age | Trades in the hour before | 1-hour change at entry | 6-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|---|
| 28 | HOGE | 13:55 | 3.29 days | 4,607 | +19.2% | +251% | +17.4% | stop, price at -16.0% | -18.47% |
| 29 | JESTER | 16:05 | 1.06 days | 612 | +21.4% | +199% | +41.9% | half sold at +34.0%, rest trailed out at +34.0% | +30.76% |

- HOGE, trade 28 (address `FVzqG...`, the same as trades 15 and 26; three trades on it now, one win and two stops). Best +17.4% at 14:30, 2.6 points short of the first target, then -9.4% twenty minutes later. The reading before the stop was -11.8% (15:00, 0.2 points inside the level) and the stop cycle read -16.0%, 4.0 points past it with the cycle on time. Afterwards it was -22.8% at 15:40, back at -0.3% at 15:55, and -18.5% five minutes after that: a token that crosses the whole stop distance in one cycle in both directions. Nothing to learn from the exit. It is the sixth loser that was up 10% or more first.
- JESTER, trade 29 (address `VAYMV...`, from `profiles_latest`, never traded before). It turned a day old at about 14:35 and was bought 1.4 hours later. Its 1-hour change read +36% to +55% for the half hour before (over the cap), +41.9% at 16:00 and +21.4% at 16:05, when the price was flat and an earlier low left the hour. Buy pressure was 1.21 against the 1.2 needed. It sat within 3% of the entry for 35 minutes, read +6.5% at 16:40 and +34.0% at 16:45, where half was sold. Best +41.9% at 17:10; the trail level was +34.8% (best less 5%) and the kept half was sold at +34.0% at 17:25, 0.8 points under it. An hour after the sale the price was at +30.2%, under the sale price, so this was not a sale into noise. It is the largest gain on the record (Rings' +23.97% was).
- JESTER fell into the band from above the cap, the shape the 14:30 entry of 17 Nov tested and dropped because it describes most winners as well as three stops. One more winner with it.
- The 5% trail, third of the 10 the test asks for. With `--set exit.trailing_stop_pct=10` the same entry ends at +23.60% against +31.04% in the replay (the kept half goes at +19.3% at 17:45): 5% is ahead by 7.4 points. Three of three are better with 5% (LEOSTAR by 42 points, Leonida by 3.4, JESTER by 7.4). The second test (3 of the next 5 kept halves sold under +15% with the token above the first target's price an hour later): 0 of 3.
- Stops: all 19 lost, average -17.87%, total -1.5527 SOL. The price at the stop cycle averages -15.6%. By age at entry: 3 days or more, 13 stops, -14.6% on price; 1 to 3 days, three stops at -14.0%; under a day, three at -21.6%. Every one of those cycles was on time, so stops still fill 2 to 4 points past the level because there is one price every five minutes, not because cycles are late. The eight trailing exits made +0.7553 SOL; the two time stops cost 0.0503.
- Left on the table: the average trade was up 16.7% at its best and realised -6.23%. Six losers were up 10% or more first (STANK, Max, GTA, BAWSAQ of 17 Nov, paws, HOGE today). The two ideas this raises (a stop moved to the entry after +10%, a first target at 15%) were tested on 17 Nov at 06:30 and 16 Nov at 22:30 and neither moved a buy at any moment by more than 0.3 points; one more case does not reopen them.
- LP locked: HOGE 62.8%, lost; JESTER 100.0%, won. Under 50%: 0 wins of 4, unchanged. At 50% or more: 8 wins of 25.
- 1 signal in the 8 hours since the last review, 6.4 hours before this one, so the 12-hour rule is not met and no threshold was relaxed. Funnel, 1,442 universe-token checks: `h1_weak` 836 (58%), `h6_down` 167, a token in its cooldown 157, `h1_overheated` 99, `txns_h1` 57, `buy_pressure` 38, `volume_accel` 37, the held token 21, `h24_dumped` 18, `m5_dropping` 11, signal 1. Seventeen different tokens were inside the universe; their median 1-hour change was -0.7% and 35% of readings were at +2% or better.

**The 6-hour change at entry (the entry section's candidate, `entry.h6_change_min_pct` 0 to 30): still 1 of the 6 the test needs.** Both new trades were in the other group: HOGE at +251% lost, JESTER at +199% won. Entries closed after 22:30 on 17 Nov: under +30%, 1 (BAWSAQ, -15.03%); +30% or more, 2, 1 winner, +6.15%. On all real trades: under +30%, 14 on 10 tokens, no winner, -16.12%; +30% or more, 15 on 11 tokens, 8 winners, +3.00%. On trades made with today's entry rules on tokens a day old or more: under +30%, 6, no winner, -13.03%; +30% or more, 7 on 5 tokens, 4 winners, +5.58%. The pattern has not been contradicted and the test has not moved: it counts entries under +30% and there has been no new one. Not acted on, and the number stays at 30.

**What the last reviews asked, answered.**

- The three open replay entries all closed. With `entry.h1_change_min_pct=0`: NVDA 09:20, 6-hour limit, -5.4%. With `entry.min_txns_h1=150` (wide, ages 3 to 30 days): NIO 11:40, 6-hour limit, +0.8% (best +14.1%); FOOD 12:30 (a $39k pool), stop, -15.3%. With `entry.min_volume_accel=1.0`: DIGS 12:55, half sold at the target and the rest trailed out, +20.5% (best +34.8%).
- DIGS at 12:55 is the first closed winner that any of the modest relaxations has added since these tables began on 15 Nov. It is not a case for its row yet. Over the whole record `min_volume_accel` at 1.0 changes three things: it adds AOTF on 14 Nov (+13.2%, a token one day old) and DIGS today, and it buys WASTED on 14 Nov forty minutes earlier for +18.4% instead of +40.6%. The replay goes from 22 closed, +0.70%, to 24 closed, +1.12%: two trades in five and a half days. The rule that would allow acting on it (12 hours with no signal) is not met. If a later review finds it met, this is the row with a closed winner in it; the cases against it are FLOAT 17:45 on 15 Nov (-3.7%) and paws 10:05 on 14 Nov (-12.1%) from the earlier tables, two entries that today's 300-trade floor no longer lets through.
- For the record, the other relaxations since 14:30 (no rule is met, so this is not a case for any): `h6_change_min_pct` -10 adds SWJ 16:30, at -10.9% with its six hours up at the end of the record; `h1_change_min_pct` 0, `min_buy_sell_ratio_h1` 1.1, `h1_change_max_pct` 35, `m5_change_min_pct` -5, `h24_change_min_pct` -40, `min_liquidity_usd` 40k, `max_age_days` 35 and the cooldown at 6 hours add nothing new.
- The 300-trade floor's second test (2 winners or fewer in the first 10 closed trades on tokens 3 days or older): 2 of 8 (Rings, Leonida; HOGE today was the eighth and lost). One winner in the next two passes it. If neither wins, that test calls the floor no improvement on the trades it keeps; its forward check closed in the floor's favour at 14:30, so the two would disagree and the entry for that day has to say so.
- What the 1-day floor blocks, forward (`--set universe.min_age_days=0.125`, entries on tokens under a day old opened after 14:45 on 17 Nov): 5 of the 10 the test needs. New: SHIT 15:20 (16 hours old, 4,902 trades in the hour), half sold at the target and the rest trailed out 50 minutes after the buy, +18.6% (best +25.0%). The five: JALU -19.1%, GTAVI -24.4%, GTA +43.4%, Leonida -15.7%, SHIT +18.6%. Two wins, +0.54% a trade, none worse than -25%, none lost from the record. The bot's own closed trades over the same days: 4, -5.10%. At 5 of 10 the test leans against the floor, on two trades that reached their target within an hour. Read it at 10, not before.
- JESTER belongs next to that: the bot's best trade was made 1.4 hours after the token passed the 1-day floor. It says nothing about the floor either way (the replay with the floor at 3 hours buys JESTER at the same cycle), but it is a second winner in the 1-to-3-day band.
- Tokens 1 to 3 days old since v6: 5 of 15 closed (rockstar, HOGE twice, BAWSAQ, JESTER), 2 wins, -0.26% a trade, -0.0126 SOL. Tokens 3 days or older over the same days: 8 closed, 2 wins, -4.73%, -0.1681 SOL. Stops in the band: 3 of the 5 the test asks for, none past -20% on price. HOGE's trade today was at 3.29 days and counts with the older tokens.
- 24-hour volume over 100 times the pool: no token inside the universe. The highest was VTC at 31 times. No second case, no cap.
- Pools that go to $0 in one cycle (walked from the 98 versions of `data/state/watchlist.json` since 14:30): 12 in 8 hours, about 36 a day (it was 51). Twelve addresses under seven names (Mabel four times, Founder and DCTY twice each, Billy, BABYDOG, OMNI, Koop), pools of $56k to $150k, all found by GeckoTerminal's most-traded-by-volume list (pages 3 to 8) and all gone within 5 to 95 minutes of being found. None had passed the universe, none gave a signal, none came back: 111 so far, none ever tradable. Fourteen more pools read under half on the next cycle without going to zero (CHOO's pool flip again, DacityCoin three times, VTC on two other addresses at $4.6M and $1.1M, and eight small ones); none was inside the universe.
- The cooldown: 157 checks on a token in its cooldown, no blocked buy (`--no-cooldown` adds no entry since 06:00). Three cases for keeping it, none against, unchanged.
- `python3 -m bot.replay` with the v8 rules reproduces HOGE within 0.2 points of the journal and JESTER within 0.3: 22 closed on 14 tokens, 9 wins, +0.70% (it was +0.14% on 20). `--baseline`: every eligible cycle 17,928 on 47 tokens, -4.33% (unchanged); cycles the entry rules passed 94 on 14, +5.04%; the first passing cycle of each run 48 on 14, 48% wins, +2.75% (was +2.59% on 46). The first row is steady. The last rose for the first time since it was first read; the two first signals added are HOGE's stop and JESTER's win.
- Discovery since 14:30: the 17 tokens inside the universe came from `profiles_latest` 5 (JESTER among them), GeckoTerminal before pages were labelled 4, `boosts_top` 4, and one each from a trending meta, `gecko:trend2`, `gecko:tx4` (HOGE) and `gecko:vol7` (NVDA). `api_calls` never passed 49, one 429, and the watchlist peaked at 245. None of the conditions for reopening the pages is met.

**Changed.** Nothing. Rulebook v8 stays; no code change; 42 tests pass. v8 has four closed trades. No test set by an earlier entry has reached its count: the 6-hour change stands at 1 of 6, the 1-day floor's forward check at 5 of 10, the 1-to-3-day band at 5 of 15 trades and 3 of 5 stops, the trail at 3 of 10, the 300-trade floor's second test at 8 of 10. There was a signal 6.4 hours ago, so the 12-hour rule gives no ground for a relaxation. One good trade does not change the reading of the record: 29 trades, 8 winners, -6.23% a trade, no edge shown.

**For the next review.**

- First: cycles, errors, and whether a signal has come. The last was JESTER at 16:05; the 12-hour mark is 04:05 UTC on 19 Nov. If the rule is met, `entry.min_volume_accel` 1.2 to 1.0 is the one relaxation with a closed winner behind it (above), and the cases against it are listed with it. Allowed, not required.
- The 6-hour change: 1 of 6 under +30% (BAWSAQ, loss); at +30% or more, 2 entries, 1 winner. Keep the two groups apart; do not move the number.
- The 1-day floor's forward check: 5 of 10 (+0.54% a trade against the bot's -5.10% on 4). Count lost positions at their last price. At 10 it is read as the 14:30 entry of 17 Nov set out.
- The 300-trade floor's second test: 2 winners in 8, two trades to go on tokens 3 days or older.
- Each new trailing exit: the trail level, the fill, and what `--set exit.trailing_stop_pct=10` gives (3 of 10, all three better with 5%).
- Drawdown: 19.43% on closed trades, 19.74% at the lowest mark, against the gate's 25%. If it passes 22%, say so plainly at the top of the entry; the rules give no licence to change sizes or stops to steer it.
- Where SWJ 16:30 ends (`entry.h6_change_min_pct=-10`).
- Pools that go to $0: the count per day (36 now) and whether any had passed the universe (none of 111). `batch_miss` less the never-seen tokens: 2 to 9 now, the line is 15.
- Follow tokens by address, not by name. Everything under "For the next review" in the earlier entries still stands.

**Would prove this review wrong.**

- Waiting on the 6-hour change was wrong by the test of 22:30 on 17 Nov, unchanged: of the first 6 closed entries under +30% opened after that time, one or none a winner while the entries at +30% or more average at least 5 points better. It is 0 of 1 so far. If it is met, `entry.h6_change_min_pct` goes from 0 to 30 as that review's one change.
- Reading the 1-day floor's forward check as "too early" at 5 of 10 is wrong if at 10 entries the replayed young trades still average better than the bot's own over the same days with no more than one worse than -25%. Then the band goes back in as the 14:30 entry of 17 Nov set out, with a smaller position if Ajeeb wants it.
- Not treating DIGS 12:55 as a case for `min_volume_accel` 1.0 is wrong if, over the next three days, that setting adds three or more trades on three or more tokens and they average better than the live rules' trades over the same days. On today's record it adds two in five and a half days.
- Reading JESTER as one trade and not a turn is wrong if v8's next 10 closed trades include 4 or more winners. Then the rules as they stand are better than this record shows, and the right response is still to leave them alone so the version can reach 30 trades.
- Leaving the rules alone is wrong by the tests the earlier entries set, which are unchanged: the volume cap (22:30 on 17 Nov), the 5% trail (22:30 on 16 Nov), tokens 1 to 3 days old (12:30 on 16 Nov, narrowed at 14:30 on 17 Nov).
- The health verdict is wrong if the gap between cycles grows past 15 minutes or skipped cycles become regular.

### v8, 2026-11-18 14:30 UTC review: no rule change, no code change (two signals since 06:30; a correction about which BAWSAQ was bought)

**Health.** 1,465 cycles since launch, 290 on v8, 98 since the last review. Last 6 hours: 72 cycles, median gap 5.0 minutes, longest 5.2. No cycle was skipped, so no message to Ajeeb. One extra cycle (08:31:36, 78 seconds after the one before; both triggers fired). The newest cycle was 2.0 minutes old when the review started, so no `.kick`. One error in the 98 cycles: GeckoTerminal 429 on page 6 of the volume list at 11:15, not repeated. `api_calls` 39 to 49 (median 42), `allowed_pool_used` 3 to 5, universe 13 to 17 tokens a cycle (median 15), `u:too_young` 10 to 18 (median 13), snapshot rows 59 to 69 (cap 120), watchlist 183 to 252 (cap 300; 187 now). RugCheck ran for both signals and both answers parsed: BAWSAQ `score_normalised` 1, no risks, LP locked 74.2%; HOGE 1, no risks, 62.8%. The saved sample still matches what `bot/rugcheck.py` reads (`score_normalised`, `risks[].level`, `lpLockedPct`). No `safety:*`, `skip:*` or `suspect_price` rows. No bug found, so no change to `bot/`. 42 tests pass.

- `batch_miss` 7 to 17 a cycle (median 10), over the 15 single lookups on 24 of the 98 cycles. Never-seen tokens on the watchlist: 4 to 7 (median 5). `batch_miss` less the never-seen tokens: 2 to 11 (median 5; it was 4 to 8), the line is 15. The top of that range is up by 3; the median is not.
- The day's limits: the day started at 4.1668 SOL, has used 2 of its 10 new trades and has realised -1.5% against the 10% limit.

**Strategy: v8 has 2 closed trades, both losses, and 1 open. Two trades are not a hint.** v8: -16.36% a trade, -0.1381 SOL. All versions: 27 closed, 7 wins on six tokens, -7.15% a trade, -0.8958 SOL. Equity 4.1444 SOL at 14:35 (-17.1%) with HOGE marked at +11.7%. Max drawdown 17.92% in the report; the lowest marked equity was 4.0742 SOL at 14:15 (-18.5%). The proof gate's line is 25%, 3.75 SOL: about 0.35 SOL under the realised balance, which is four or five average stops (0.082 SOL each) with no winner between them. SOL $74.2 to $75.0.

| # | Token | Opened (UTC, 18 Nov) | Age | Trades in the hour before | 1-hour change at entry | 6-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|---|
| 27 | BAWSAQ | 06:40 | 1.38 days | 855 | +11.2% | +25.1% | +4.0% | stop, price at -12.1% | -15.03% |
| 28 | HOGE | 13:55 | 3.29 days | 4,607 | +19.2% | +251% | +17.4% | open at +11.7% (14:35) | |

- **Correction to the 06:30 entry.** It called BAWSAQ "the token that stood 88% under the bot's buy price half an hour after the buy on 17 Nov" and said its cooldown ended at 00:25. That is a different token with the same name. Trade 22 on 17 Nov was the address `D9Eco...` (launched about 20:10 on 16 Nov; it left the snapshots at 17:20 on 17 Nov). Trade 27 today is `4La95...` (launched about 21:30 on 16 Nov; in the snapshots on every cycle since 00:00 on 17 Nov with a pool of $41k to $89k). Seven addresses have carried the name BAWSAQ in two days. The cooldown is kept per address, so `4La95...` never had one, and trade 27 is not "the first trade on a token the bot has already seen lose most of its value". The same holds for names in general: a symbol does not identify a token here (GTA, GTA6, ANT, BUCKZ and Leonida all appear on several addresses below). Use the address when following a token from one review to the next.
- BAWSAQ, trade 27. The price moved between -18% and 0% of the later entry in the hour before the buy. The 1-hour change read -3.2%, +0.5%, -0.7% on the three cycles before and +11.2% at 06:40, because the price an hour earlier (05:40 to 05:45) was at a low. Best +4.0% at 07:00, then six cycles down to -12.1% at 07:30: the stop filled 0.1 points past its level. It was at -3.6% ten minutes later, never above the entry in the hour after, and at -16% by 09:00. Nothing to learn from the exit. It cost 1.5% of the day's starting equity (the 1-to-3-day test's line is 5% in a day).
- HOGE, trade 28 (the same address as trades 15 and 26). At 12:25 it traded at $0.00039, 47% under the price the bot was stopped at on 17 Nov. At 12:30 it read +160% in one cycle and at 12:35 another +94%, with $571k traded in those ten minutes and the pool going from $73k to $170k: a real move by both of the bad-print guards' measures (not held, so neither ran). The 1-hour change read +166% to +389% until the jump left the hour at 13:30 (+34.7%, still over the cap), then -7.7% to -3.2% for four cycles, and +19.2% at 13:55, when the bot bought at $0.00174. It has been between -5.9% and +17.4% since; the first target is +20%. It was 3.29 days old at entry, so it counts in the "3 days or more" row and is the eighth trade for the 300-trade floor's second test.
- Stops: all 18 lost, average -17.84%, total -1.4769 SOL. The price at the stop cycle averages -15.6%. By age at entry: 3 days or more, 12 stops, -14.5% on price; 1 to 3 days, three stops (2.5, 3.4 and 0.1 points past the level); under a day, three at -21.6% on average. Every one of those cycles was on time. Stops on tokens a day old or more still fill 2 to 3 points past the level: the cost of one price every five minutes, not late cycles. The seven trailing exits made +0.6314 SOL; the two time stops cost 0.0503.
- Left on the table: the average trade was up 15.7% at its best and realised -7.15%. The same five losers were up 10% or more first (STANK, Max, GTA, BAWSAQ of 17 Nov, paws). BAWSAQ today peaked at +4.0%. Nothing new for the exit section; no trailing exit since Leonida (2 of 10).
- LP locked: BAWSAQ 74.2%, lost. Under 50%: 0 wins of 4, unchanged. At 50% or more: 7 wins of 23.
- 2 signals in the 8 hours since the last review, the last 35 minutes before this one, so the 12-hour rule is not met and no threshold was relaxed. The gap that ended at 06:40 was 14.3 hours, the second longest on the record. Funnel, 1,468 universe-token checks: `h1_weak` 957 (65%), `h6_down` 148, `txns_h1` 116, `buy_pressure` 71, `h1_overheated` 67, a token in its cooldown 58, the held token 17, `volume_accel` 13, `h24_dumped` 10, `m5_dropping` 9, signal 2. Twenty different tokens were inside the universe; their median 1-hour change was -0.2% and 31% of readings were at +2% or better.

**The 6-hour change at entry (the entry section's candidate, `entry.h6_change_min_pct` 0 to 30): 1 of the 6 the test needs.** BAWSAQ was bought with a 6-hour change of +25.1% and lost. HOGE (+251%) is the first entry in the other group and is open. On all real trades the split now reads: under +30%, 14 trades on 10 tokens, no winner, -16.12%; +30% or more, 13 on 10 tokens, 7 winners, +2.52%. On trades made with today's entry rules on tokens a day old or more: under +30%, 6, no winner, -13.03%; +30% or more, 5, 3 winners, +5.35%. One more loser on the side the pattern predicts. The test was written so that a pattern found by searching would have to hold on trades made after it was named, and one trade is not six. Not acted on, and the number stays at 30.

**What the last reviews asked, answered.**

- The four open replay entries all closed. With `entry.min_buy_sell_ratio_h1=1.1`: DIGS 05:35 stop, -15.5%; BAWSAQ 05:50 stop, -16.6%. With `entry.h1_change_min_pct=0`: BAWSAQ 06:30 stop, -16.4%. With `entry.min_txns_h1=150` (wide, ages 3 to 30 days): DIGS 03:25, 6-hour limit, +5.6% (best +17.6%). The 06:30 entry said not relaxing was wrong if DIGS and BAWSAQ at buy pressure 1.1 both ended as winners; both were full stops. Buy pressure at 1.1 has now added seven trades since 14:30 on 17 Nov: six stops and JOB's +4.0% (two of the stops in place of the live trade on the same token, itself a stop).
- For the record, what the same relaxations show since 06:30 (no rule is met, so this is not a case for any): `h1_change_min_pct` 0 adds NVDA 09:20, open at -3.0%; `min_volume_accel` 1.0 adds DIGS 12:55, open at +11.0%; `min_txns_h1` 150 adds NIO 11:40, open at +2.6%; `h1_change_max_pct` 35 buys HOGE at 13:30 instead of 13:55, a stop ten minutes later, -18.3%; `max_age_days` 35 adds Macca 11:25, stop, -17.6%. The cooldown at 6 hours, buy pressure at 1.1, `h6_change_min_pct` -10, `m5_change_min_pct` -5 and `min_liquidity_usd` 40k add nothing new.
- The 300-trade floor, forward check (entries on 150 to 299 trades, wide replay, tokens 3 to 30 days old, opened after 06:45 UTC on 16 Nov): 10 closed, 2 wins (DIGS on 16 Nov and DIGS 03:25 today). The test called the floor wrong at 3 winners or more in 10; it reads 2. Closed, in the floor's favour. Still open in that band, not counted: NIO 11:40 (204 trades) at +2.6% and FOOD 12:30 (157 trades, a $39k pool) at -3.4%. The floor's other test (2 winners or fewer in the first 10 closed trades on tokens 3 days or older) is unchanged at 2 of 7; HOGE is the eighth.
- The gap did not reach 24 hours (it ended at 14.3), so the count of days under one trade does not start.
- 24-hour volume over 100 times the pool: no token inside the universe. The highest was BLOB at 56 times (over 50 on ten cycles around 08:00 to 08:40); the next is under 50. No second case, no cap.
- Pools that go to $0 in one cycle (walked from the 98 versions of `data/state/watchlist.json` since 06:30): 17 in 8 hours, about 51 a day (it was 57). Seventeen addresses under eight names (GTA five times, GTA6 and BUCKZ three each, ANT twice, Kekius, 大A, DCI, DACT). All are pumpswap pools against SOL of $41k to $144k, 0.5 to 2.4 hours old when first seen, with 7,600 to 14,800 trades in their last hour and $1.9M to $8.4M of reported volume. Sixteen were found by GeckoTerminal's most-traded-by-volume list (13 on pages 4 to 8, 3 on pages 2 and 3), one by page 6 of the trade-count list. None had passed the universe (all under a day old), none gave a signal, none came back: 99 so far, none ever tradable. Sixteen more pools read under half on the next cycle without going to zero: CHOO seven times ($80k and $30k, the batch call answering with a different pool), DCI twice (the same flip; it was inside the universe on one cycle, 07:05, with no signal), four pools that read $1.5k to $2.6k a cycle later (EXEN at $320k, UODF at $1.5M, a second VTC address at $1.4M, TEMPLE3 at $36k; none inside the universe) and three others (KATIA, VI, GTASZN), none inside the universe either.
- What the 1-day floor blocks, forward (`--set universe.min_age_days=0.125`, entries on tokens under a day old opened after 14:45 on 17 Nov): 4 of the 10 the test needs. JALU 04:10 (9 hours old) stop, -19.1%; GTAVI 12:30 (12 hours) stop, price at -22.3%, -24.4%; GTA 12:40 (10 hours) half sold at the target and the rest trailed out 25 minutes after the buy, +43.4% (best +65.7%); a new Leonida address 13:15 (12 hours) stop, -15.7%. One win, -3.97% a trade, none worse than -25% (GTAVI by 0.6 points). The bot's own closed trades over the same days: 2, -16.36%. So at 4 of 10 the test leans against the floor, and the whole lean is one trade that ran 66% in 25 minutes. Read it at 10, not before. All four tokens were still in the snapshots at 14:30; JALU stood 60% under its replay entry.
- The last three of those four entries came within 45 minutes of each other (12:30 to 13:15), starting on the cycle of HOGE's jump, on tokens named after the same game (GTAVI, GTA, Leonida). If the floor were lower the bot would have opened three positions on one theme inside an hour. Noted for the day the under-a-day band is discussed again; `max_open_positions` does not know about themes.
- Tokens 1 to 3 days old since v6: 4 of 15 closed (rockstar, HOGE twice, BAWSAQ), 1 win, -8.01% a trade, -0.1365 SOL. Tokens 3 days or older over the same days: 7 closed, 2 wins, -2.77%, -0.0923 SOL. Stops in the band: 3 of the 5 the test asks for, none past -20% on price.
- The cooldown: 58 checks on a token in its cooldown, no new blocked buy. Three cases for keeping it, none against, unchanged.
- `python3 -m bot.replay` with the v8 rules reproduces BAWSAQ within 0.2 points of the journal and HOGE's entry: 20 closed on 13 tokens, 8 wins, +0.14% (it was +0.93% on 19), HOGE open. `--baseline`: every eligible cycle 16,681 on 45 tokens, -4.33% (was -4.45%); cycles the entry rules passed 85 on 13, +4.22%; the first passing cycle of each run 46 on 13, 48% wins, +2.59% (was +2.98% on 45). The first row is steady. The last has fallen at every review since it was first read off the record the rules were shaped on (+4.41%, +3.42%, +2.98%, +2.59%), which is what "do not expect it" meant.
- Discovery since 06:30: the 20 tokens inside the universe came from `boosts_top` 5, `profiles_latest` 5, GeckoTerminal before pages were labelled 5, and one each from a trending meta, `gecko:trend2`, `gecko:tx4` (HOGE), `gecko:tx6` (DCI, one cycle) and `gecko:vol7` (NVDA). `api_calls` never passed 49, one 429, and the watchlist peaked at 252. None of the conditions for reopening the pages is met.

**Changed.** Nothing. Rulebook v8 stays; no code change; 42 tests pass. v8 has two closed trades. No test set by an earlier entry has been met: the 6-hour change stands at 1 of 6, the 1-day floor's forward check at 4 of 10, the 1-to-3-day band at 4 of 15 trades and 3 of 5 stops, the trail at 2 of 10. The one test that closed today (the 300-trade floor's forward check) closed in favour of the rule as it is. There were two signals in the last 8 hours, so the 12-hour rule gives no ground for a relaxation, and the relaxations it would allow lost again on the entries they added.

**For the next review.**

- First: cycles, errors, and HOGE's exit (trade 28). If it reaches the first target, record the trail level (best less 5%), the fill, and what `--set exit.trailing_stop_pct=10` gives: it would be the third of 10. It counts in the "3 days or more" row, in the +30%-or-more group for the 6-hour change, and as the eighth trade for the 300-trade floor's second test (a win makes 3 and passes it).
- The 6-hour change: 1 of 6 under +30% (BAWSAQ, loss). Keep the two groups apart; do not move the number.
- The 1-day floor's forward check: 4 of 10 (-3.97% a trade against the bot's -16.36% on 2). Count lost positions at their last price.
- Follow tokens by address, not by name (the correction above). When a review names a token it has seen before, check the address in `data/journal/trades.jsonl` or `data/state/portfolio.json` (`last_exit`).
- Drawdown: 17.92% on closed trades against the gate's 25%. If it passes 22%, say so plainly at the top of the entry; the rules give no licence to change sizes or stops to steer it, so the entry should only record it.
- Where the open replay entries end: NVDA 09:20 (`h1_change_min_pct=0`), DIGS 12:55 (`min_volume_accel=1.0`), NIO 11:40 (`min_txns_h1=150`).
- Pools that go to $0: the count per day (51 now) and whether any had passed the universe (none of 99). `batch_miss` less the never-seen tokens: 2 to 11 now, the line is 15.
- Everything under "For the next review" in the earlier entries still stands, except the 300-trade floor's forward check, which this entry closes, and the BAWSAQ item of 06:30, which rested on the wrong token.

**Would prove this review wrong.**

- Waiting on the 6-hour change was wrong by the test of 22:30 on 17 Nov, unchanged: of the first 6 closed entries under +30% opened after that time, one or none a winner while the entries at +30% or more average at least 5 points better. It is 0 of 1 so far. If it is met, `entry.h6_change_min_pct` goes from 0 to 30 as that review's one change. Waiting cost real paper money if the next five entries under +30% all lose as well; that is the price of not acting on a searched pattern, and it is accepted here knowingly.
- Reading the 1-day floor's forward check as "too early" is wrong if at 10 entries the replayed young trades still average better than the bot's own over the same days with no more than one worse than -25%. Then the band goes back in as the 14:30 entry of 17 Nov set out, with a smaller position if Ajeeb wants it.
- The correction about BAWSAQ is wrong if `data/journal/trades.jsonl` shows the same `token` address on trades 22 and 27. It shows `D9EcoQZe...` and `4La95NEV...`.
- Leaving the rules alone is wrong by the tests the earlier entries set, which are unchanged: the volume cap (22:30 on 17 Nov), the 5% trail (22:30 on 16 Nov), tokens 1 to 3 days old (12:30 on 16 Nov, narrowed at 14:30 on 17 Nov).
- The health verdict is wrong if the gap between cycles grows past 15 minutes or skipped cycles become regular.

### v8, 2026-11-18 06:30 UTC review: no rule change, no code change (14 hours without a signal; no relaxation the record supports)

**Health.** 1,367 cycles since launch, 192 on v8, 97 since the last review. Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 5.2. No cycle was skipped, so no message to Ajeeb. One extra cycle (01:11:07, 56 seconds after the one before; both triggers fired). The newest cycle was 1.8 minutes old when the review started, so no `.kick`. No error in any of the 97 cycles. `api_calls` 45 to 50, `allowed_pool_used` 3 or 4, universe 16 or 17 tokens a cycle, `u:too_young` 13 to 21 (median 15), snapshot rows 64 to 71 (cap 120), watchlist 240 to 283 (cap 300; 251 now). RugCheck was not called, because there was no signal; the saved sample still matches what `bot/rugcheck.py` reads (`score_normalised`, `risks[].level`, `lpLockedPct`). No `safety:*`, `skip:*` or `suspect_price` rows. No bug found, so no change to `bot/`. 42 tests pass.

- `batch_miss` 11 to 18 a cycle (median 14), over the 15 single lookups on 23 of the 97 cycles. Never-seen tokens on the watchlist: 6 to 14 (median 7; the six on it now are all from `profiles_latest`). `batch_miss` less the never-seen tokens: 4 to 8 (median 6; it was 0 to 6), the line is 15.
- The day's limits: the day rolled over at 00:00 UTC (0 of 10 new trades used, the 10% loss limit counted from 4.1668 SOL). No signal came between 22:30 and midnight, so the limits of 17 Nov (-8.1%, 8 of 10 trades) were never put to the test.

**Strategy: nothing to judge. No trade was opened or closed since HOGE's stop at 17:45 on 17 Nov.** v8 still has 1 closed trade, a loss. All versions: 26 closed, 7 wins, -6.84% a trade, -0.8332 SOL, equity 4.1668 SOL (-16.66%), max drawdown 16.66%, nothing open. SOL $73.6 to $75.1. The exit, entry-feature and left-on-the-table figures are the ones in the 22:30 entry below, to the digit: stops 17 of 17 lost (-18.00% on average), trailing exits 7 of 7 won, the average trade was up 16.2% at its best and realised -6.84%.

**No signal for 14.2 hours (last: HOGE at 16:20 on 17 Nov, 172 cycles ago). The 12-hour rule is met. Nothing relaxed, because every modest relaxation buys losers on the record.**

- A gap this long has happened once before: 15.1 hours from FLOAT (23:50 on 14 Nov) to Leonida (14:55 on 15 Nov). The next longest are 12.8 and 10.8.
- Funnel since the last signal, 2,751 universe-token checks: `h1_weak` 1,441 (52%), a token in its cooldown 383, `h6_down` 337, `buy_pressure` 239, `txns_h1` 181, `h1_overheated` 62, `h24_dumped` 43, `m5_dropping` 25, `volume_accel` 24, the held token 16, signal 0. The universe was 12 to 17 tokens a cycle (median 16), 21 different tokens in all. Their median 1-hour change was -0.3% and 37% of readings were at +2% or better: a flat night, not a falling one.
- Of the 18 tokens inside the universe since 22:30, 15 are 3 days or older and 12 are tokens the bot has already traded (the six it has not: SWJ, MORI, NVDA, CHILL, JOB, mihao). It is the same small set as on 15 Nov.
- What each relaxation the rule allows would have bought since 16:20 on 17 Nov (`python3 -m bot.replay --set ...` on the bot's universe; "open" is marked at the 06:30 price after costs):

| Change tried | Trades it adds since the last signal |
|---|---|
| `entry.h1_change_min_pct` 2 to 1 | none (to 0: BAWSAQ 06:30 today, open at -3.0%) |
| `entry.h6_change_min_pct` 0 to -5 or -10 | none |
| `entry.min_buy_sell_ratio_h1` 1.2 to 1.1 | NIO 17:45, stop, -18.1%; Max 19:05, stop, -18.0%; JOB 21:10, 6-hour limit, +4.0% (best +17.3%); DIGS 05:35 today, open at -8.9%; BAWSAQ 05:50 today, open at -11.1% |
| `entry.min_volume_accel` 1.2 to 1.0 | none |
| `entry.h1_change_max_pct` 25 to 35 | Max 22:40, stop, -16.7% |
| `entry.m5_change_min_pct` -3 to -5 | Max 22:45, half sold at the target, rest trailed out, +21.8% (best +42.1%) |
| `entry.min_txns_h1` 300 to 250, 200 or 150 | none |
| `entry.h24_change_min_pct` -30 to -40 | none |
| `portfolio.token_cooldown_hours` 12 to 6 | HOGE 02:05 today, stop, -16.5% |
| `universe.min_liquidity_usd` 50k to 40k | CHILL 20:10, 6-hour limit, -5.4% |
| `universe.max_age_days` 30 to 35 | DacityCoin 18:55, 6-hour limit, -13.6%; :3 02:50 today, stop, -20.8% |
| `universe.min_volume_h24_usd` 100k to 50k, `min_liq_to_mcap` 0.03 to 0.02, `min_market_cap_usd` 300k to 200k | none |

- The one relaxation that would have added trades in number, buy pressure at 1.1, adds two full stops, one small win and two positions that are underwater. That is the third time this table has been drawn (15 Nov 13:30 and 22:30) and the third time it says the same.
- The one winner in the table is not a case for its row. Max at 22:40 (blocked as overheated) and Max at 22:45 (blocked as `m5_dropping`) are the same token bought five minutes and 5.7% apart: the first was stopped at 23:25 with the price 12.7% under it, -16.7% net; the second never fell more than 9.5% under its lower entry and ended at +21.8%. Over the whole record `m5_change_min_pct` at -5 adds exactly that one trade (its other two differences are WASTED on 14 Nov and DIGS on 17 Nov bought one cycle earlier). One trade in 4.6 days does not end a drought, and it is the single winner among some twenty variants tried, which is what searching finds.
- So the bottleneck is not a threshold. Sixteen tokens on a flat night produce no moment the rules call a buy, and the moments just outside the rules lost. Relaxing one anyway would be buying trades the record says lose, on an account that is 16.66% down with a 25% drawdown line.

**What the last reviews asked, answered.**

- The 6-hour change (candidate: `entry.h6_change_min_pct` 0 to 30). No entry was closed after 22:30 on 17 Nov, real or in the replay with the live rules: 0 of the 6 under +30% that the test needs. The entries in the table above are not live-rule entries and do not count; for the record they do not lean its way either (at buy pressure 1.1, Max at +35.9% over six hours was a full stop and JOB at +26.4% the small win).
- 24-hour volume over 100 times the pool: no token inside the universe since ANT's last cycle at 21:35 on 17 Nov. The highest since 22:30 were BAWSAQ at 63 times and BLOB at 54; the next is 16. No second case, no cap.
- Pools that go to $0 in one cycle (walked from the 98 versions of `data/state/watchlist.json` since 22:30): 19 in 8 hours, about 57 a day (it was 44). Nineteen addresses under seven names (NVIDIANS, GTA and GTAVI four times each, Spud three times, GTA6 twice, :3, ANT). All are pumpswap pools against SOL of $52k to $377k, 0.7 to 3.8 hours old, with 3,900 to 14,600 trades in their last hour and $3.3M to $12.1M of reported volume. All were found by GeckoTerminal's most-traded-by-volume list (15 on pages 5 to 8, 4 on pages 2 and 3). None had passed the universe (all under a day old), none gave a signal, none came back. The "ANT" among them is a new address carrying yesterday's name, 1.4 hours old when it was emptied. Seven more pools read under half on the next cycle without going to zero: CHOO twice ($82k and $30k, the batch call answering with a different pool, as before) and five outside the universe.
- What the 1-day floor blocks, forward (`--set universe.min_age_days=0.125`, entries on tokens under a day old opened after 14:45 on 17 Nov): one. JALU, 04:10 today, 9.4 hours old, 10,147 trades in the hour: stop, price at -16.3%, -19.1% net. 1 of the 10 the test needs.
- Tokens 1 to 3 days old: no new trade (3 of 15 closed, 2 of 5 stops). BAWSAQ turned a day old and has been inside the universe on 110 cycles since, with a $70k pool; it is the token that stood 88% under the bot's buy price half an hour after the buy on 17 Nov. Its cooldown ended at 00:25 and the entry rules have not passed it (`h1_weak` 60, `buy_pressure` 23, `h6_down` 9, `h24_dumped` 8).
- The 300-trade floor, forward check (entries on 150 to 299 trades, wide replay, tokens 3 to 30 days old, opened after 06:45 UTC on 16 Nov): 9 closed, 1 win. New: GTA$ 03:30 today (156 trades, a $33k pool), stop, -15.3%. DIGS 03:25 today (209 trades) is open at -1.1%. The test called the floor wrong at 3 winners or more in 10 closed; with 1 in 9 it can no longer get there. That test is settled for the floor. Its other test (2 winners or fewer in the first 10 closed trades on tokens 3 days or older) is unchanged at 2 of 7.
- The cooldown blocked one buy: HOGE at 02:05 today passed the entry rules 8.3 hours after its stop. In the replay with no cooldown it is a stop, -16.5%. With Rings and HOGE on 16 Nov, three cases for keeping it and none against.
- Trailing exits: none new (2 of 10). `suspect_price`: no row.
- `python3 -m bot.replay` with the v8 rules: 19 closed on 12 tokens, 8 wins, +0.93%, unchanged. `--baseline`: every eligible cycle 14,954 on 43 tokens, -4.45% (was -4.69%); cycles the entry rules passed 84 on 12, +4.45%; the first passing cycle of each run 45 on 12, 49% wins, +2.98% (was +3.42% on 44). The one added first signal is HOGE at 02:05, the stop the cooldown kept the bot out of.
- Discovery since 22:30: the 18 tokens inside the universe came from `boosts_top` 6, GeckoTerminal before pages were labelled 5, `profiles_latest` 3, and one each from a trending meta, `gecko:trend2`, `gecko:tx4` (HOGE) and `gecko:vol7` (NVDA). `api_calls` never passed 50, no 429, and the watchlist peaked at 283, under its cap. None of the conditions for reopening the pages is met.

**Changed.** Nothing. Rulebook v8 stays; no code change; 42 tests pass. No trade has closed since the last review, so no test set by an earlier entry has moved except the 300-trade floor's forward check, which now cannot fail. The 12-hour rule allows a relaxation and does not require one; the table above is the reason none was made.

**For the next review.**

- First: cycles, errors, and whether a signal has come. If one has, RugCheck's answer and the fill.
- Where the open replay entries end: DIGS 05:35 and BAWSAQ 05:50 with `entry.min_buy_sell_ratio_h1=1.1`, BAWSAQ 06:30 with `entry.h1_change_min_pct=0`, DIGS 03:25 with `entry.min_txns_h1=150` (wide, ages 3 to 30 days).
- The 6-hour change: 0 of 6. Keep the two groups apart from the first trade closed after 22:30 on 17 Nov.
- BAWSAQ, if it is bought: it is the first trade on a token the bot has already seen lose most of its value in half an hour. Record the stop against the 12% level; it counts in the 1-to-3-day row.
- Pools that go to $0: the count per day (57 now) and whether any had passed the universe (none of 82 so far).
- `batch_miss` less the never-seen tokens: 4 to 8 now, the line is 15. The watchlist against its 300 cap.
- Everything under "For the next review" in the earlier entries still stands.

**Would prove this review wrong.**

- Not relaxing was wrong if DIGS 05:35 and BAWSAQ 05:50 (bought with buy pressure at 1.1) both end as winners and the next 12 hours again bring no signal. Then `entry.min_buy_sell_ratio_h1` 1.2 to 1.1 is the relaxation to make, as a hypothesis, and NIO and Max in the table above are the cost to set against it.
- If the gap passes 24 hours (16:20 UTC today) with cycles arriving, the rules as they have stood since v5 are opening under one trade a day, and the 06:30 entry of 16 Nov set the line: three such days and the universe has to grow before any entry rule can be judged. Count from today.
- Reading the Max pair as noise is wrong if, on a week of data, `entry.m5_change_min_pct` at -5 adds five or more trades on four or more tokens and they average better than the live rules' trades over the same days. On today's record it adds one.
- Leaving the rules alone is wrong by the tests the earlier entries set, which are unchanged: the 6-hour change and the volume cap (22:30 on 17 Nov), the 1-day floor (14:30 on 17 Nov), the 5% trail (22:30 on 16 Nov), tokens 1 to 3 days old (12:30 on 16 Nov, narrowed at 14:30 on 17 Nov).
- The health verdict is wrong if the gap between cycles grows past 15 minutes or skipped cycles become regular.

### v8, 2026-11-17 22:30 UTC review: no rule change, no code change

**Health.** 1,270 cycles since launch, 95 on v8 (from 14:45 UTC), 96 since the last review. Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 5.3. No cycle was skipped, so no message to Ajeeb. One extra cycle (18:30:18, 75 seconds after the one before; both triggers fired). The newest cycle was 1.9 minutes old when the review started, so no `.kick`. No error in any of the 96 cycles. `api_calls` 48 to 51, `allowed_pool_used` 3 to 5, universe 12 to 17 tokens a cycle (median 16), `u:too_young` 2 to 16 (median 10), snapshot rows 54 to 66 (cap 120). RugCheck ran for the one signal and the answer parsed: HOGE `score_normalised` 1, no risks, LP locked 87.6%. The saved sample still matches what `bot/rugcheck.py` reads (`score_normalised`, `risks[].level`, `lpLockedPct`). No `safety:*`, `skip:*` or `suspect_price` rows. No bug found, so no change to `bot/`. 42 tests pass.

- `batch_miss` 16 to 20 a cycle (median 18). Never-seen tokens on the watchlist: 13 to 19 (median 15). `batch_miss` less the never-seen tokens: 0 to 6 (median 2), the line is 15.
- The watchlist reached 285 (cap 300; it was 201 at 14:45 and is 280 now). It is not the tradable part that grew: 124 of the 280 came from `profiles_latest` (92 of them under the $30k floor and waiting out their six hours, 13 never returned data) and 50 from the trending metas (49 under the floor). At 300 the code drops the tokens under the floor first, thinnest first, so reaching the cap costs nothing that can be traded. Not changed.

**Strategy: v8 has 1 closed trade, a loss. One trade is not a hint.** v7 ended at 7 closed, 2 wins, -8.08% a trade (-0.2512 SOL): Leonida and DIGS were its last. Equity 4.1668 SOL (-16.66%; it was 4.1939). All versions: 26 closed, 7 wins on six tokens, -6.84% a trade, -0.8332 SOL, max drawdown 16.66% (the proof gate's line is 25%). The day stands at -8.1% against a 10% daily limit and has used 8 of its 10 new trades; it rolls over at 00:00 UTC. No position is open. SOL $73.5.

| # | Token | Opened (UTC, 17 Nov) | Age | Trades in the hour before | 1-hour change at entry | 6-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|---|
| 23 | DIGS (v7) | 12:45 | 20.0 days | 1,243 | +10.4% | +29.5% | +5.1% | stop, price at -13.4% | -14.96% |
| 25 | Leonida (v7) | 13:55 | 11.8 days | 553 | +2.2% | +36.6% | +28.4% | half sold at +23.5%, rest trailed out at +21.4% | +19.80% |
| 26 | HOGE (v8) | 16:20 | 2.39 days | 1,171 | +5.7% | +48.3% | +8.6% | stop, price at -15.4% | -17.68% |

- HOGE was bought forty minutes after its high. At 15:40 the price was 20% above where the bot later bought and the 1-hour change read +30%; it fell 17%, the 1-hour change dropped to -0.2% at 16:15 and read +5.7% at 16:20, inside the band, because the price an hour earlier was lower still. It was +8.6% on the next cycle, -7.2% at 17:40 and -15.4% at 17:45 ($22k traded in those five minutes), 3.4 points past the stop with the cycle on time. It was at -26% an hour later, so the stop did its job. It is the second stop of the five the last entry's test for tokens 1 to 3 days old asks for (2.5 and 3.4 points past the level; neither past -20%). It cost 1.7% of the day's starting equity; that test's line is 5% in a day.
- DIGS never rose more than +5.1%, slid for four hours and was stopped at -13.4%, 1.4 points past the level. It stayed between -10% and -13% for the next hour. Nothing to learn from the exit.
- Leonida is the second trailing exit under the 5% trail (2 of the 10 the 22:30 entry on 16 Nov asks for). Best price +28.4%, trail level +22.0%, kept half sold at +21.4%, 0.6 points under it. The same entry with a 10% trail ends at +16.63% against +20.00%: 5% is ahead by 3.4 points. An hour after the sale the price was back at the entry, so this was not a sale into noise. Both exits so far are better with 5% (LEOSTAR by 42 points, which is one collapse; Leonida by 3.4).
- Stops: all 17 lost, average -18.00%, total -1.4143 SOL. The price at the stop cycle averages -15.8%. By age at entry: 3 days or more, 12 stops, -14.5% on average, 2.5 points past the level; 1 to 3 days, two stops at -14.5% and -15.4%; under a day, three at -13.1%, -28.3% and -23.5%. Every one of those cycles was on time. Stops on tokens a day old or more are filling 2 to 3 points past the level, which is what a price read every five minutes costs; they are not a sign of late cycles. The seven trailing exits made +0.6314 SOL; the two time stops cost 0.0503.
- Left on the table: the average trade was up 16.2% at its best and realised -6.84%. Five of the 19 losers were up 10% or more first (STANK +17.1%, Max +16.6%, GTA +16.6%, BAWSAQ +12.0%, paws +10.3%). The 06:30 review tested a stop moved to the entry price after +10%, and the 22:30 review on 16 Nov a first target at 15%; neither moved the mean of a buy at any moment by more than 0.3 points. Nothing new in three trades to reopen either.
- LP locked: DIGS 100.0% (lost), Leonida 84.3% (won), HOGE 87.6% (lost). Under 50%: 0 wins of 4, unchanged. At 50% or more: 7 wins of 22.
- 1 signal in the 7.8 hours since v8 went live, 6.2 hours before this review, so the 12-hour rule is not met. Funnel on v8, 1,449 universe-token checks: `h1_weak` 748 (52%), a token in its cooldown 235, `h6_down` 209, `buy_pressure` 134, the held token 40, `h1_overheated` 30, `txns_h1` 19, `h24_dumped` 13, `volume_accel` 11, `m5_dropping` 9, signal 1.

**The strongest pattern in the report, tested and not acted on: the 6-hour change at entry.** `python3 -m bot.report` splits the 26 real trades at the median of each entry feature. One split is clean:

| 6-hour change at entry | Real trades (all versions) | Wins | A trade |
|---|---|---|---|
| under +30% | 13 on 9 tokens | 0 | -16.20% |
| +30% or more | 13 on 10 tokens | 7 | +2.52% |

Every one of the seven winners had a 6-hour change of +34.7% or more when it was bought. On the trades made with today's entry rules on tokens a day old or more (v5 onwards): under +30%, 5 trades, no winner, -12.63%; +30% or more, 5 trades, 3 winners, +5.35%.

- For it. All seven winners falling in one half happens by chance about 1 time in 380. There is a mechanism: the rules buy a rise in the last hour, and a rise in the last hour on a token that is flat over six is the "one burst" entry the reviews keep describing (FLOAT three times, paws twice, NIO), while a rise on a token already up over six hours is a trend. On the recorded snapshots the entry rules' first signals say the same on the bot's universe: under +30%, 14 on 8 tokens, 21% wins, -8.07%; +30% or more, 30 on 7 tokens, 63% wins, +8.78%, and the same direction in both halves of the record (13 to 15 Nov: -2.27% on 4 against +13.34% on 16; 16 and 17 Nov: -10.39% on 10 against +3.58% on 14).
- Against it, plainly. The report prints 13 such splits and this is the best of them: with 13 features and two directions, one split this clean somewhere turns up about 1 time in 15, and the trades are not independent (the losing half holds FLOAT three times, Leonida and paws twice each). It was found by searching, at a threshold set by the median. It is not a steady slope: by band, the first signals made -16.1% at 0 to +15% (5 on 3 tokens), -3.6% at +15 to +30% (9 on 6), +18.1% at +30 to +60% (14 on 7) and +0.7% above +60% (16 on 5), and the replay with the floor at 15, 20, 30 and 40 gives +4.00% (16 trades), +9.30% (14), +13.30% (11) and +5.44% (9). On the wide record (every token 1 to 30 days old) the gap shrinks: first signals under +30% made +0.31% (76 on 23 tokens, 10 tokens positive), at +30% or more +5.87% (65 on 16, 8 positive), and with the floor at 40 the replay falls to -0.23%. A buy at every eligible cycle, with no entry rule, is barely better above +30% on the wide record (-2.72% against -3.22%). The 15 Nov review cut all cycles by this feature and found nothing.
- So it is a hint with a mechanism, the best one the entry section has, and it is still 26 trades on 18 tokens. It would also be a second rule change within eight hours on a version with one closed trade, which is how no version has yet reached 30 trades. Named now as the entry section's candidate, with the number fixed before the next trade: `entry.h6_change_min_pct` 0 to 30. The test is under "Would prove this review wrong". Volume acceleration splits the same way and more weakly (real trades at or under 1.61: 14, -14.42%; above: 12, +2.00%; on the wide record the tokens are level), so it is not carried as a second candidate.

**Discovery, settled for now: the deeper pages stay, and what they find is mostly pools that are emptied within hours.** The last two reviews named `top_volume_pages` 8 to 4 and `top_tx_pages` 6 to 3 as the next change if HOGE was still the only token from a deeper page to pass the universe. It no longer is, and the reason is worth more than the count.

- Since 12:35 on 16 Nov 25 tokens have passed the universe at today's 1-day floor. By the feed that found them: `profiles_latest` 7, GeckoTerminal before pages were labelled 7, `boosts_top` 6, one each from a trending meta, `gecko:trend2`, `gecko:tx4` (HOGE), `gecko:vol6` (ANT, from 16:55 today) and `gecko:vol8` (NVDA, from 22:10 today). 99 tokens from the deeper pages were on the watchlist at some point in those 58 hours (77 from `gecko:vol5` to `vol8`, 22 from `gecko:tx4` to `tx6`); three passed.
- Read from the 419 versions of `data/state/watchlist.json` in git (12:00 on 16 Nov to 22:30 on 17 Nov, 34.5 hours): 63 tokens had a pool of $30k or more on one cycle and a pool of exactly $0 on the next, about 44 a day. None of the 63 ever came back. They are one kind of thing: a pumpswap pool against SOL ($100k to $160k in 47 cases, $36k to $90k in 15), about 12,000 trades in its last hour (8,000 to 15,000 for most), $3.6M to $10M traded, gone at a median age of 1.2 hours; 60 were under 4.1 hours old. Every one was found by GeckoTerminal's most-traded-by-volume list: 47 on pages 5 to 8, 11 on page 4, 3 on pages 1 to 3, 2 on the trade-count pages 5 and 6. So 47 of the 77 tokens the deeper volume pages found were pools that were emptied within hours. The volume that puts them on that list is the bait.
- None of the 62 young ones ever passed the universe, at the 1-day floor or the 3-hour one, and none gave a signal: they were too young or gone first. They have cost nothing. They are also the plainest support so far for v8's floor: the band under a day old is where this is made.
- ANT is the one that lived long enough. It turned a day old at 16:55 and passed the universe on 58 cycles in a row until 21:35: pool $121k to $131k, 24-hour volume $47M to $48M (360 to 400 times its pool; the universe's median is 4.2 times, the 99th percentile 99, and the most any entry signal ever had is 44), 5,500 to 6,000 trades in every hour, the price up 34% over those 4.7 hours in small steps. At 21:40 the pool read $0. The entry rules never said buy: `buy_pressure` stopped it on 56 cycles (1.07 to 1.10 buys per sell against the 1.2 needed) and `h1_weak` on 2, and `volume_accel`, the test after `buy_pressure`, would have failed on every cycle as well (0.77 to 1.15 against 1.2). A machine trading at one steady rate shows neither more buyers than sellers nor rising volume. It passed the 1-hour, 6-hour, 24-hour, 5-minute and trade-count tests on 56 of the 58. RugCheck was never asked, because it is only asked after a signal. A buy would have lost the whole position, about 0.42 SOL or 10% of equity, with no stop able to help. Two entry tests stood between the bot and that, by 0.10 and 0.05, and neither was written to catch it.
- The count behind those 63: 118 times a pool of $30k or more read under half that on the next cycle. The other 55 went to a figure above zero. 30 of them (12 tokens) showed $30k or more again, most within a cycle or two: the batch call answering with a different pool of the same token on different cycles (gtacoin $187k and $22k to $40k thirteen times, CHOO $81k and $30k seven times, SENT $9.2M and $3k). This is the behaviour found on 13 Nov. A held position is priced on its own pool, so no fill is touched; a token that is not held is judged on the thinner pool for that cycle and can miss a signal. The remaining 25 did not come back: real falls (LEOSTAR at 13:05 among them) and pools of up to $4M that read $1k to $4k a cycle later. None of the 55 was inside the universe on the cycle before. Not changed.
- Why the pages stay. Cutting the volume pages would not have kept ANT out (it was found again on page 1 of the trade-count list at 13:00 today), would not change a trade under v8 (the young ones cannot be traded), and would thin the record of young tokens that the last entry's test for the 1-day floor is read from. The pages still cost nothing (`api_calls` never passed 51, no 429). The item is closed, not overdue: reopen it only on the conditions below.
- What would have kept ANT out is a cap on 24-hour volume against the pool, in the universe section (it needs a line in `bot/strategy.py`, and it is a tightening). Not added on one token: a cap at 200 fits ANT and nothing else, and at 100 it starts to touch tokens the record cannot call bad (inuhao 116 and FOOD 107 at their highest, neither ever bought). Named as the universe section's candidate, with its trigger below.

**What the last reviews asked, answered.**

- v8 cycles are clean: `universe_ok` 12 to 17, no new error. The first live cycle is in the last entry.
- `python3 -m bot.replay` with the v8 rules reproduces DIGS, Leonida and HOGE, each within 0.2 points of the journal: 19 closed on 12 tokens, 8 wins, +0.93% (it was +1.88% on 16).
- `python3 -m bot.replay --baseline`, v8, bot's universe: every eligible cycle 13,570 on 41 tokens, -4.69% (was -4.43%); cycles the entry rules passed 83 on 12 tokens, +4.70%; the first passing cycle of each run 44 on 12, 50% wins, +3.42% (was +4.41% on 40). The first row is steady; the last is read off the record the rules were shaped on.
- What the 1-day floor blocks, forward (`--set universe.min_age_days=0.125`, entries on tokens under a day old opened after 14:45): none in 7.8 hours. 0 of the 10 the test needs.
- Tokens 1 to 3 days old since v6: 3 closed (rockstar, HOGE twice), 1 win, -5.67% a trade, -0.0739 SOL. Tokens 3 days or older over the same days: 7 closed, 2 wins, -2.77%, -0.0923 SOL. The test reads at 15 closed.
- The 300-trade floor, forward check (entries on 150 to 299 trades, wide replay, tokens 3 to 30 days old, opened after 06:45 UTC on 16 Nov): 8 closed, 1 win. paws 08:55 ended at the 6-hour limit, -13.65%. No new entry in that band since 13:35. The test needs 10 closed and calls the floor wrong at 3 winners or more; it can no longer get there on these eight unless both of the next two win.
- The floor's other test (2 winners or fewer in the first 10 closed trades on tokens 3 days or older): 2 of 7 (Rings, Leonida). One more winner in the next three passes it.
- The 5% trail's second test (3 of the next 5 kept halves sold under +15% with the token above the first target's price an hour later): 0 of 2.
- `suspect_price`: no row.

**Changed.** Nothing. Rulebook v8 stays; no code change; 42 tests pass. v8 is eight hours old with one closed trade, no test set by an earlier entry has been met, there was a signal 6.2 hours ago, and the one pattern strong enough to tempt a change was found by searching and is now written down with its number before the trades that will test it.

**For the next review.**

- First: cycles, errors, and whether the day's limits did what they should (the day was at -8.1% with 8 of 10 trades used at 22:30).
- The 6-hour change: for every trade closed after 22:30 UTC on 17 Nov, real or in `python3 -m bot.replay`, the 6-hour change at entry and the result. Keep the two groups apart from the first trade.
- Any token inside the universe whose 24-hour volume is more than 100 times its pool: name it, say what blocked a buy, and say what its pool did next. To find them, compute `vol_h24 / liq_usd` on the snapshot rows that pass `universe_reject`.
- Pools that go to $0 in one cycle: the count per day and whether any had passed the universe. The method is in this entry (walk `git log -- data/state/watchlist.json`; the clone is shallow, so `git fetch --shallow-since=<date> origin main` first).
- Tokens 1 to 3 days old: each closed trade and each stop against the 12% level (2 of 5 stops, 3 of 15 trades).
- Each new trailing exit: the trail level, the fill, and what `--set exit.trailing_stop_pct=10` gives (2 of 10).
- `batch_miss` less the never-seen tokens: 0 to 6 now, the line is 15. The watchlist against its 300 cap.
- Everything under "For the next review" in the earlier entries still stands, except the discovery item, which this entry closes.

**Would prove this review wrong.**

- Waiting on the 6-hour change was wrong, and `entry.h6_change_min_pct` should go from 0 to 30 as that review's one change, if of the next 6 closed entries with a 6-hour change under +30% (real trades, or the replay's with the live rules, opened after 22:30 UTC on 17 Nov) one or none is a winner while the entries at +30% or more over the same days average at least 5 points better. The idea is wrong, and should be dropped for good, if 3 or more of those 6 win, or if the entries at +30% or more do no better than the others. In between, carry it to 10. Do not move the number from 30 on what the new trades show.
- Not capping volume against the pool was wrong if a second token with 24-hour volume over 100 times its pool passes the universe for an hour or more, or if any such token gives a signal, whatever RugCheck then says. Then add the cap to the universe section, at 100 unless that entry's data shows a tradable token above it, and write the test for it.
- Keeping the deeper pages was wrong if `api_calls` passes 55, GeckoTerminal 429s start repeating, the watchlist sits at 300 while a token above the $30k floor is dropped by the cap, or a token found only by `gecko:vol5` to `vol8` is bought and ends on `liquidity_drop` or a write-off. Then `top_volume_pages` goes to 4.
- Reading the $0 pools as emptied rather than misreported was wrong if one of them later shows a pool of $30k or more again. None of 63 has.
- Leaving the rules alone is wrong by the tests the earlier entries set, which are unchanged: the 1-day floor (14:30 today), the 5% trail (22:30 on 16 Nov), tokens 1 to 3 days old (12:30 on 16 Nov, narrowed at 14:30 today), the 300-trade floor (06:30 on 16 Nov).
- The health verdict is wrong if the gap between cycles grows past 15 minutes or skipped cycles become regular.

### v8, 2026-11-17 14:30 UTC review: a token can be traded from 1 day after launch, was 3 hours

**Health.** 1,173 cycles since launch, 191 on v7, 99 since the last review. Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 5.2. No cycle was skipped, so no message to Ajeeb. One extra cycle (09:05:47, 37 seconds after the one before; both triggers fired). The newest cycle was 2.0 minutes old when the review started, so no `.kick`. No error in any of the 99 cycles. `api_calls` 48 or 49, `allowed_pool_used` 3 to 5, watchlist 206 to 225 (cap 300), universe 15 to 20 tokens a cycle (median 17). RugCheck ran for all 5 signals and every answer parsed: `score_normalised` 1 and no risks on each, LP locked 84.3% (Leonida), 98.3% (bul) and 100.0% (LEOSTAR, BAWSAQ, DIGS). The saved sample still matches what `bot/rugcheck.py` reads. No `safety:*`, `skip:*` or `suspect_price` rows. No bug found, so no change to `bot/`. 42 tests pass.

- `batch_miss` 16 to 21 a cycle (median 19) and over the 15 single lookups on all 99 cycles, as before. The number the last review said to watch, `batch_miss` less the tokens that have never returned data (15 to 17 on the watchlist, all from `profiles_latest`), was 1 to 5 (median 3): well inside 15. One never-seen token returned data for the first time (BPCat, 07:10, no pool to speak of). No token with a live pool went unpriced.
- The two large falls the bot acted on were real moves by the guard's own measure, and I checked both by hand. BAWSAQ at 12:25: 36% under the last reading on $26.6k traded, 2.7 times what a pool of that size needs to move that far. bul at 13:05: 23.5% under on $10.2k, 1.7 times the need. Neither was a bad print; the readings that followed are below.

**Strategy: v7 closed 5 trades, 1 win, -12.29% a trade (-0.2697 SOL). Five trades are hints, not findings.** Equity 4.1939 SOL (-16.12%; it was 4.4165). All versions: 23 closed, 6 wins on five tokens, -7.18% a trade, -0.7762 SOL, max drawdown 15.52% (it was 11.62%). The day stands at -7.5% against a 10% daily limit and has used 7 of its 10 new trades. SOL $72.1 to $73.9.

| # | Token | Opened (UTC, 17 Nov) | Age | Trades in the hour before | 1-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|
| 20 | FLOAT | 05:55 | 19.3 days | 646 | +18.0% | +3.0% | 6-hour limit, price at -0.4% | -3.95% |
| 21 | LEOSTAR | 11:30 | 12.5 hours | 14,019 | +17.7% | +26.0% | half sold at +26.0%, rest trailed out at +15.2% | +15.62% |
| 22 | BAWSAQ | 12:15 | 16.1 hours | 10,792 | +20.9% | +12.0% | stop, price at -28.3% | -30.55% |
| 23 | DIGS | 12:45 | 20.0 days | 1,243 | +10.4% | +5.1% | open at -6.9% | |
| 24 | bul | 13:00 | 9.6 hours | 1,419 | +12.4% | 0.0% | stop, price at -23.5% | -25.92% |
| 25 | Leonida | 13:55 | 11.8 days | 553 | +2.2% | +3.7% | open at +3.7% | |

- BAWSAQ. Bought at 12:15, +12.0% at 12:20, -28.3% at 12:25: the stop was crossed and passed by 16 points inside one cycle, with the cycle on time. The readings after the stop were -43%, -66%, -80% and -88% (12:45); the pool went from $101k to $33k and the token left the snapshots at 13:20. Selling at -28% was the good outcome here. Half an hour before the buy the price had been 43% lower (11:45); it rose 77% in the 30 minutes to the buy.
- LEOSTAR. Reached the first target at 12:50 (+26.0%, a jump from +14.3% in one cycle on $59.8k) and the kept half was sold on the next cycle at +15.2%, 4.5 points under its trail level (+19.7%). At 13:00 it read +24.7%. At 13:05 the price was 78% lower than five minutes before, the pool had gone from $98k to $45k, and the token left the snapshots. The bot was out by ten minutes.
- bul (Raydium, $97k pool). -23.5% on the first cycle after the buy, 11.5 points past the stop. The next reading was -3.6%, it was above the entry 30 minutes after the stop (+2.6% at 13:35) and at -23.4% by 14:30. A token that swings 20% between two readings cannot be held with a 12% stop read every five minutes: the stop fills wherever the price happens to be.
- FLOAT never moved more than +3.0% or -6.7% and went out at the 6-hour limit with the price 0.4% under the entry: the loss is the costs. The last review recorded it as the third first signal bought on one burst (paws and RAMBO were stops); this one was flat.
- Stops: all 15 lost, average -18.23%, total -1.2742 SOL. The price at the stop cycle now averages -16.0% (it was -14.5% on 13). By age at entry: 3 days or more, 11 stops, -14.6% on average, 2.6 points past the level; 1 to 3 days, one stop at -14.5% (rockstar); under a day, three stops at -13.1%, -28.3% and -23.5%, 9.6 points past the level on average. Every one of those cycles was on time. The six trailing exits made +0.5483 SOL; the two time stops cost 0.0503.
- LP locked said nothing today: the four tokens under a day old read 98% to 100%, and three of them lost. A locked pool does not stop holders selling. Under 50%: still 0 wins of 4, no new trade. At 50% or more: 6 wins of 19.
- 5 signals in the 8 hours since the last review, so the 12-hour rule is not met. Funnel, 1,719 universe-token checks: `h1_weak` 884 (51%), a token in its cooldown 291, `h6_down` 157, the held token 99, `txns_h1` 92, `buy_pressure` 78, `h1_overheated` 68, `m5_dropping` 23, `volume_accel` 17, `h24_dumped` 4, `liquidity_falling` 1, signal 5.

**The young tokens: the test set when the 3-hour floor went in is met.** The 12:30 entry on 16 Nov wrote: young tokens are not worth trading on these rules "if any single day's young-token trades cost more than 5% of equity. Then raise `universe.min_age_days` again (1 day first)".

- Today's four trades on tokens under 3 days old were all on tokens under a day old (GTA 9.4 hours, LEOSTAR 12.5, BAWSAQ 16.1, bul 9.6): -0.0747, +0.0687, -0.1342 and -0.1120 SOL, together -0.2523 SOL. The day started at 4.5319 SOL, so that is 5.6% of equity. The line was 5%.
- Under a day old, all real trades: 4 closed, 1 win, -14.37% a trade. 1 to 3 days old: 2 closed (rockstar, HOGE), 1 win, +0.33%. Young together: 6 of the 15 closed trades that entry asked for, 2 wins, -9.47% a trade, -0.2507 SOL. Tokens 3 days or older over the same two days (Max, Rings, paws, NIO, FLOAT): 5 closed, 1 win, -4.84%, -0.1108 SOL. Young tokens are losing about twice as much a trade, on 6 against 5.
- The 14:35 entry's test (the age table overstates the problem if the first five young-token stops fill within 3 points of the level): four so far at 2.5, 1.1, 16.3 and 11.5 points. It has failed with one to go. The table did not overstate.
- The 12:30 entry's other test (more than one `liquidity_drop` or write-off in the first 15 young trades): none by the letter. But BAWSAQ lost 88% in the half hour after the buy and LEOSTAR 78% in one cycle ten minutes after the sale. Those are the drained-pool cases that test was written for; the bot was a cycle ahead of one of them.
- Why 5-minute cycles cannot handle this band, from the record. For every reading of a token inside the universe, what happened in the six hours after it (the longest a position is held):

| Age at the reading | Readings (tokens) | Price halved, or the token left the snapshots, within 6 hours | Tokens that did so at least once |
|---|---|---|---|
| under 1 day | 3,619 (41) | 29.6% | 32 of 41 |
| 1 to 3 days | 3,440 (20) | 20.2% | 15 of 20 |
| 3 days or more | 8,594 (19) | 1.2% | 3 of 19 |

  (A token leaves the snapshots when its pool falls under the watchlist's $30k floor; these had $50k or more at the reading. The snapshots have never been at their 120-row cap, so rank is not the reason.)

**The entry rules on tokens under a day old, on the record.** The yardstick from 15 Nov, with positions kept to their exit whatever it was. Two readings that point different ways, both given.

| Age at entry | A buy at every eligible cycle (entries up to 01:30 today) | Ended worse than -25% | Price at the stop cycle | The entry rules' first signals (whole record) | Ended worse than -25% |
|---|---|---|---|---|---|
| under 1 day | 3,205 on 40 tokens, -1.95%, median -14.8% | 10.3% | -19.3% | 13 on 8 tokens, 4 wins, -20.92% | 6 of 13 |
| 1 to 3 days | 3,272 on 20, -3.56% | 4.4% | -15.9% | 11 on 4, 6 wins, +4.58% | 0 of 11 |
| 3 days or more | 7,731 on 19, -4.70% | 0.9% | -14.0% | 29 on 8, 15 wins, +4.35% | 0 of 29 |

- For the change: on tokens under a day old the rules' own signals did far worse than a buy at any moment in the same band, and far worse than their signals on older tokens. One position in ten in that band ends worse than -25% against one in a hundred for tokens 3 days or older, and the stop fills 5 points further out. The 13 first signals: MORI +7.5%, bill -23.7%, GETAJOB -26.2%, HOGE +59.7%, GTA -16.6% and -17.8%, LEOSTAR +15.8%, -75.1%, -75.4%, +11.5% and -75.5%, BAWSAQ -30.5%, bul -25.8%. Two of the eight tokens have a positive average.
- Against it, plainly. Nine of the 13 are from today, five of them one token (LEOSTAR). Before today the four first signals under a day old averaged +4.3% (2 wins, HOGE's +59.7% carrying it), which is why the 12:30 entry on 16 Nov let the band in. A buy at any moment in the band did not lose more on average than in older tokens (-1.95% against -4.70%), though that figure stops at 01:30 today and marks 5.7% of its positions at their last price before the token vanished, which flatters it. And with the floor at 1 day the replay of the whole record is about level with v7: 16 closed on 11 tokens, 7 wins, +1.88%, against 24 closed on 18 tokens, 11 wins, +1.30%. So this is not a finding that young tokens have worse returns. It is a finding that their results here are set by where the price happens to be when the bot looks: LEOSTAR ended at +15.6% with a 5% trail and would have ended at -26.7% with the 10% trail of two days ago, the same token, the same entry.
- `python3 -m bot.replay --baseline` shows the same thing from the other side. v7, bot's universe: every eligible cycle 15,939 on 62 tokens, -3.97% (was -4.12%); cycles the entry rules passed 108 on 18 tokens, -3.67%; the first passing cycle of each run 53 on 18, 47% wins, -1.80% (it was +3.63% on 45). With `--set universe.min_age_days=1`: every cycle 12,238 on 38 tokens, -4.43%; passing cycles 79 on 11, +5.27%; first passing cycles 40 on 11, 52% wins, +4.41%. Wide, ages 3 to 30 days: every cycle 26,677 on 46 tokens, -3.38% (was -3.86%); first passing cycles 90 on 17, 51% wins, +3.30% (was +3.24% on 79). The rules' picks beat a buy at any moment by 7 to 10 points on tokens a day old or more and by 0.3 to 2 points once tokens under a day old are in. The first figure is read off the record the rules were shaped on. Do not expect it.

**Changed: rulebook v8, universe section only. `universe.min_age_days` 0.125 to 1. A risk limit set off by its own test, on hints.**

- Why act on six trades. The test was written before the trades, on the day the band was opened, and it names this step. The mechanism was measured before the trades too (14:35 on 16 Nov: a fall of the whole stop distance inside one cycle is 14 times as common under a day old as at 3 days or more) and today's stops did what it said. The proof gate needs a max drawdown under 25%; it is at 15.5% after one such day.
- Why 1 day and not 3. "1 day first" is what the test says, and picking the floor after seeing the tables would be choosing the number that makes the past look best. The 1-to-3-day band is not cleared: its tokens halve or vanish within six hours nearly as often (20% of readings), its one real stop filled 2.5 points past the level, and its good replay numbers are two tokens (WOHAIHAO and HOGE, 9 of the 11 first signals). It stays in as Ajeeb's experiment with a test of its own, below.
- What it does not do. Entry, exit, portfolio, safety, costs and discovery are untouched. A token found at 3 hours old stays on the watchlist and is recorded in the snapshots as before; it becomes tradable when it turns a day old if it still passes everything else. The `volume_accel` handling for tokens under six hours old stays in the code and is no longer reached by a trade. DIGS (20 days) and Leonida (11.8 days) are open, labelled v7, and are managed as before.
- What it costs. On the latest snapshot the universe goes from 16 tokens to 13 (GTA, BAWSAQ and DSP, 17 to 22 hours old, drop out). Of the 28 tokens that passed the universe since the band opened, 11 were under a day old when they first did. Fewer trades, and no chance at a launch-day run like HOGE's +59.7% in the replay.
- What it does to the open tests. The young-token tests carry on for tokens 1 to 3 days old only: 2 of 15 closed (rockstar, HOGE), 1 stop. The 300-trade floor and the 5% trail are read as before. v7 ends at 5 closed trades plus the two open ones.
- Ajeeb: this narrows the rule you asked for on 16 Nov, on the test written into this file that day. The band under a day old was open for 26 hours and took 4 trades. If you want it kept running regardless, say so and it goes back. The honest way to keep it would be a smaller position for tokens under a day old (it needs code in `bot/portfolio.py` and is a different section), so that one stop at -30% costs what a normal stop does.

**What the last reviews asked, answered.**

- `python3 -m bot.replay` with the v7 rules reproduces FLOAT, LEOSTAR, BAWSAQ and bul, each within 0.2 points of the journal: 24 closed on 18 tokens, 11 wins, +1.30% (it was +3.78% on 20).
- Trailing exits, the first under the 5% trail (1 of the 10 the 22:30 entry's test needs):

| # | Token | Half sold at the target | Best while held | Trail level (best less 5%) | Kept half sold at | Under the level | The same entry with a 10% trail |
|---|---|---|---|---|---|---|---|
| 21 | LEOSTAR | +26.0% | +26.0% | +19.7% | +15.2% | 4.5 points | -26.66% for the trade (kept half sold at -72.6%), against +15.78% |

  Better with 5% by 42 points, because the token collapsed two cycles later. That is one trade and mostly luck; it counts as one "better", and the test's average will be bent by it, so read the count as well.
- The 06:30 review's test for the young-token stop (wrong if three of the first five young stops were back above the entry within an hour): 2 of 4 (GTA and bul were; rockstar and BAWSAQ were not). A wider stop would have changed nothing for BAWSAQ (its first reading under the entry was already -28.3%), and the 06:30 table had young tokens doing worse with one, so the two that came back do not make a case for it.
- The 300-trade floor, forward check (entries on 150 to 299 trades opened after 06:45 UTC on 16 Nov, wide replay with `entry.min_txns_h1=150`, tokens 3 to 30 days old): 7 closed, 1 win. New: GTA$ 13:35 today (153 trades, a $40k pool) -15.2%. paws 08:55 today (155 trades) is open at -11.1%. The test needs 10 closed and calls the floor wrong at 3 winners or more.
- The floor's other test (2 winners or fewer in the first 10 closed trades on tokens 3 days or older): 1 of 5 (Max, Rings, paws, NIO, FLOAT). It needs 2 more winners in the next 5; DIGS and Leonida are the sixth and seventh.
- "The 1-hour change fell into the band from above the cap" (Rings on 16 Nov, and now bul, whose 1-hour change read +34% and +40% on the two cycles before the buy, and BAWSAQ, +25.6% on the cycle before). The 06:30 entry on 16 Nov said to test it against all cycles if it repeated. Tested as: a reading over +25% in the 15 minutes before the signal. It fails. First signals with that shape made +5.33% (26 on 12 tokens, 14 wins) and without it -8.66% (27 on 13); with the floor at 1 day, +8.41% against 0.00%. The shape fits three stops and describes most of the winners as well. Dropped.
- Discovery: due, and it fails. Since 12:35 on 16 Nov 28 tokens have passed the universe. By the feed that found them: `profiles_latest` 13, GeckoTerminal before pages were labelled 7, `boosts_top` 5, one each from `gecko:tx4`, `gecko:trend2` and a trending meta. 76 tokens from the deeper pages (`gecko:vol5` to `vol8`, `gecko:tx4` to `tx6`) were on the watchlist at some point in those 26 hours and one passed the universe: HOGE, still the only one. The last review said to put `top_volume_pages` back to 4 and `top_tx_pages` to 3 on this reading. Not done today: one section per review, and the universe change is the one that limits losses. The pages cost nothing meanwhile (`api_calls` 48 or 49, no 429).
- The youngest band, for the record: 24 tokens passed the universe since 22:50 on 16 Nov, 8 of them under a day old when they first did, 4 at about 3 hours old (BAWSAQ on two addresses, SENT, LEOSTAR). The four bought were 9 to 16 hours old. No token under 6 hours old ever gave a signal.
- `suspect_price`: no row. Watchlist peaked at 225. `api_calls` never passed 49.

**Changed, in full.**

1. Rulebook v8: `universe.min_age_days` 0.125 to 1, `version`, `updated`, `notes`.
2. README: the strategy paragraph (v8, 1 to 30 days) and the honesty rule about young tokens.
3. No change to `bot/` or `tests/`: the tests read the age floor from the rulebook. 42 pass.

**First live cycle (14:45 UTC).** Pushed at 14:41 UTC and picked up by the 14:45 cycle: v8, no errors, `api_calls` 48, `batch_miss` 19, `universe_ok` 12 (16 on the cycle before), no signal (6 `h1_weak`, 3 `h6_down`, 2 tokens in their cooldown). `u:too_young` went from 2 to 13, more than the 4 tokens that left the universe: the age test comes first, so tokens under a day old that used to be counted under another reason (mostly liquidity) are now counted there. DIGS (-4.0%) and Leonida (-3.9%) were read and carried on as usual. v8 trades start from the 14:45 cycle.

**For the next review.**

- First: confirm v8 cycles stay clean (`universe_ok` about 12 to 14, `u:too_young` about 13, no new error).
- DIGS and Leonida: record the exits. Both count in the "3 days or more" row and for the floor's test.
- Discovery is overdue and is the named candidate for the next change: `top_volume_pages` 8 to 4 and `top_tx_pages` 6 to 3, or keep `top_tx_pages` at 4 for HOGE's sake and say why. With the age floor at 1 day the deeper pages matter even less than before, since 30 of the first 31 tokens they found were under a day old; a token found young does stay on the watchlist and can age in, which is how HOGE was traded at 1.35 days.
- Tokens 1 to 3 days old: each closed trade, and for each stop the price at the stop cycle against the 12% level.
- What the floor blocks, forward: in `python3 -m bot.replay --set universe.min_age_days=0.125`, the entries on tokens under a day old opened after the first v8 cycle. Count a position "lost from the record" as a loss at its last price, not as nothing.
- Each new trailing exit: the trail level, the fill, and what `--set exit.trailing_stop_pct=10` gives.
- `batch_miss` less the never-seen tokens: 1 to 5 now, the line is 15.
- LP locked under 50%: 0 wins of 4, unchanged. Everything under "For the next review" in the earlier entries still stands.

**Would prove this review wrong.**

- The 1-day floor costs more than it saves if the next 10 replayed entries on tokens under a day old (as above, lost positions counted at their last price) average better than the bot's own closed trades over the same days and no more than one of them ends worse than -25%. Then the 17 Nov trades were one bad day, and the band can go back in, with a smaller position if Ajeeb wants it.
- The floor is too low, and should go to 3 days, if the first five stops on tokens 1 to 3 days old include two that fill past -20% on price (rockstar's -14.5% is the first of the five), if one day's trades on tokens 1 to 3 days old cost more than 5% of equity, or if after 15 closed trades in that band they lose more per trade than older tokens over the same days.
- It changed nothing that matters if v8's first 15 closed trades still show a stop cycle averaging worse than -16% on price: then the gap past the stop is not about age and the next thing to look at is the minimum pool size.
- Putting discovery off was wrong if `api_calls` passes 55 or GeckoTerminal 429s start repeating before the next review.
- The health verdict is wrong if the gap between cycles grows past 15 minutes or skipped cycles become regular.

### v7, 2026-11-17 06:30 UTC review: no rule change, no code change

**Health.** 1,076 cycles since launch, 94 on v7 (from 22:50 UTC on 16 Nov). Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 5.2. No cycle was skipped since the last review (the last skipped one was 21:35 on 16 Nov), so no message to Ajeeb. One extra cycle (01:05:08, 44 seconds after the one before; both triggers fired). The newest cycle was under 2 minutes old when the review started, so no `.kick`. One error in the 94 cycles: GeckoTerminal 429 on page 3 of the trade-count list at 05:45, fetched on the next cycle. `api_calls` 48 to 50, `allowed_pool_used` 4, watchlist 212 to 266 (cap 300; 213 now), universe 15 to 18 tokens a cycle (median 17, was 13). RugCheck ran for both signals and both answers parsed: GTA `score_normalised` 1, no risks, LP locked 100.0%; FLOAT 1, no risks, 71.9%. The saved sample still matches what `bot/rugcheck.py` reads (`score_normalised`, `risks[].level`, `lpLockedPct`). No `safety:*`, `skip:*` or `suspect_price` rows. No bug found, so no change to `bot/`. 42 tests pass.

`batch_miss` is up and I looked for harm, as the 14 Nov 23:35 entry asked once it passed 20. It was 16 to 27 a cycle (median 22, was 15) and over the 15 single lookups on all 94 cycles; `no_data` 14 to 22 (median 18). Read from the 94 versions of `data/state/watchlist.json` in git:

- The rise is mostly tokens that have never returned data: 13 to 20 on the watchlist (median 17, was 12 to 14), every one from `profiles_latest`. The rest are tokens with a data history that the batch call left out: 2 to 7 a cycle. Those are looked up first (the 14:35 change), and 7 is well inside 15.
- No token with a live pool went unpriced. Three tokens with a data history were missing on a cycle (TRALALERO, shitcoin, GARY; 32 token-cycles in all). Their pools read $7.7k to $14.9k when last seen, under the watchlist's $30k floor, and none came back before it was dropped from the watchlist.
- The lookups left over (8 to 13 a cycle) go to the never-seen tokens in address order, so the last few in that order get none. I checked whether that hides anything: 10 never-seen tokens returned data for the first time since 12:00 on 16 Nov, and their pools read $2 to $11.6k (seven of them under $1,100). None was near the watchlist floor, and the delay did not follow the address order. No harm found, not changed.

**Strategy: v7 has 1 closed trade, a loss, and 1 open. One trade is not a hint.** v6 ended at 6 closed, 2 wins, -3.26% a trade (-0.0918 SOL): NIO was its last. Equity 4.4165 SOL (-11.67%; it was 4.5425). All versions: 19 closed, 5 wins on four tokens, -6.33% a trade, -0.5812 SOL, max drawdown 11.62%. The day is at -2.5% against a 10% daily limit. SOL $71.2 to $72.9.

| # | Token | Opened (UTC) | Age | Trades in the hour before | 1-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|
| 18 | NIO (v6) | 16 Nov 20:50 | 26.2 days | 300 | +2.2% | +9.0% | 6-hour limit, price at -3.9% | -7.26% |
| 19 | GTA | 17 Nov 03:25 | 9.4 hours | 3,083 | +9.9% | +16.6% | stop, price at -13.1% | -16.63% |
| 20 | FLOAT | 17 Nov 05:55 | 19.3 days | 646 | +18.0% | +3.0% | open at +0.8% | |

- NIO is the first trade to end at the 6-hour limit. It was bought on exactly 300 trades in the hour, drifted between -9% and +9% and never came near the stop or the target. Nearly half of its loss is costs (price -3.9%, net -7.26%).
- GTA is the first trade on a token under a day old. Its price moved 4% or more between two readings on 8 of the 12 cycles it was held (+10.6%, +8.2%, -9.2%, +11.0% among them). The 1-hour change that let it in read -15.9, -9.6, -2.0, -4.7, +4.3, -3.7, +4.5, -3.3, +1.3 and then +9.9 on the ten cycles up to the buy: on a token like this the number changes sign with each reading. It peaked at +16.6% fifteen minutes in, 3.4 points short of the first target. The reading before the stop was -5.6%, the stop cycle -13.1%, and forty minutes later the price was 2.6% over the entry. This is what the 14:35 entry on 16 Nov wrote before rockstar's result: on a token that moves this much, whichever of the stop and the target is hit first says little about the entry.
- FLOAT was bought on one burst, the shape paws had at 18:00 on 16 Nov. Its trades in the hour went from 137 to 646 in a single cycle (509 trades, $17.5k and +13.7% on price in five minutes), after an hour of almost no trading. From the next cycle on it failed `buy_pressure` (440 buys to 373 sells). It is the third first signal with most of the hour's trades in the last five minutes; the other two (paws, RAMBO) were stops. The 22:30 review tested that idea against all cycles and dropped it; FLOAT's result is one more case, not a reason to reopen it. It is also the token the 300-trade floor blocked at 21:00 on 16 Nov (245 trades, -14.8% in the wide replay) and then let through nine hours later.
- Stops: all 13 lost, average -16.69%, total -1.0280 SOL. The price at the stop cycle averages -14.5%, 2.5 points past the level, with every cycle on time. The five trailing exits made +0.4796 SOL; the one time stop cost 0.0329.
- No trailing exit since v7 went live, so the 5% trail has not been used yet: 0 of the 10 the last entry's test needs.
- Young tokens: 3 closed of the 15 the 12:30 entry asks for (rockstar, HOGE, GTA), 1 win, -5.32% a trade, -0.0731 SOL. Tokens 3 days or older over the same days (Max, Rings, paws, NIO): 4 closed, 1 win, -5.06%, -0.0935 SOL. Level, on seven trades. Young stops: 2 of the 5 the 14:35 entry asks for, 2.5 and 1.1 points past the level, both inside its 3 points. No `liquidity_drop`, no write-off. Today's one young trade cost 1.6% of equity (the test's line is 5% in a day). The day has used 2 of its 10 new trades.
- The youngest band is seen and still not traded. 20 tokens passed the universe since 22:50, 9 of them under 3 days old when they first did, and 6 of those at about 3 hours old (BAWSAQ on two addresses, LEOSTAR, SENT, GTA, DSP). GTA was bought at 9.4 hours; no token under 6 hours old has given a signal.
- LP locked: NIO 41.7%, lost. Every closed trade under 50% lost: 4 of 4 (Rings 26.2%, STANK 40.5%, NIO 41.7%, rockstar 48.5%). At 50% or more: 5 wins of 15, GTA (100.0%) among the losers. A 0-of-4 against 5-of-15 split turns up by chance about one time in four, and the figure moves (Rings read 26.2% and 78.8% fifteen hours apart). Still a hint; a floor would be a tightening of the safety section and is allowed if it firms up.
- 2 signals in the 7.7 hours since 22:50, the last 35 minutes before this review, so the 12-hour rule is not met. Funnel, 1,609 universe-token checks: `h1_weak` 710 (44%), a token in its cooldown 419, `h6_down` 128, `txns_h1` 118, the held token 68, `h1_overheated` 65, `buy_pressure` 40, `m5_dropping` 29, `volume_accel` 27, `h24_dumped` 3, signal 2.

**Two exit ideas tested against a buy at any moment. Neither holds.** Method as in the 06:30 entry on 16 Nov: a position at every eligible cycle, the same entries run through each variant, positions in tokens that left the record kept and marked at their last price, only entries opened 13 hours or more before the end of the record. A scratch script; nothing in `bot/` changed.

1. *A stop moved to the entry price once a trade has been +10% up.* The 14 Nov 13:30 entry named it for trades that peak at +13% to +19% and end at the full stop. There are now three real ones (STANK +17.1%, Max +16.6%, GTA +16.6%). Tested as: before the first target, if an earlier reading was at or over +X%, sell when the price is at or under the entry.

| Variant | Bot's universe, 12,701 entries on 56 tokens | Wide, ages 3 to 30 days, 21,178 entries on 45 tokens |
|---|---|---|
| live exits (v7) | -3.60% | -3.26% |
| break-even after +8% | -3.34% | -3.36% |
| break-even after +10% | -3.41% | -3.33% |
| break-even after +15% | -3.51% | -3.25% |

   It moves the mean by +0.3 to -0.1 points and the two records disagree on the sign. On the entry rules' own first signals it is worse at +10% on both (-0.5 points on 36 and on 68 signals): it turns Max's -20.3% into -3.1% and two WOHAIHAO winners (+17.6%, +16.7%) into -12.2% and -12.9%. A "break-even" exit does not fill at zero: the positions it closed ended at -4.7% on average, because the price is already under the entry when the bot looks and the costs come on top. Dropped. The 22:30 review found the same for a first target at 15%.

2. *A wider stop for young tokens.* GTA was stopped and stood above its entry forty minutes later, so the question is whether 12% is inside the noise for a token this young. The opposite:

| Age at entry | Entries (tokens) | 12% stop (live) | 16% stop | 20% stop | Of those stopped at 12%, better with a 20% stop |
|---|---|---|---|---|---|
| under 1 day | 3,015 (33) | -2.06% | -2.38% | -2.53% | 18% |
| 1 to 3 days | 2,973 (20) | -3.73% | -4.48% | -5.35% | 18% |
| 3 days or more | 6,713 (18) | -4.24% | -3.98% | -3.72% | 44% |

   A young token that has fallen 12% mostly keeps falling: more tokens do worse than better with the wider stop (14 to 8 under a day, 12 to 4 at 1 to 3 days), and the worst single position goes to -91%. GTA coming back was the less common case. For tokens 3 days or older a 20% stop still reads half a point better, as on 16 Nov, with tokens split 5 better to 6 worse: not a case. The stop stays at 12% for all ages.

- The same yardstick by age, updated (live exits): 3 to 6 hours old +3.51% (311 cycles on 12 tokens, median -15.4%, 60% stopped); 6 to 24 hours -2.70% (2,704 on 33, median -14.8%, 54% stopped); 1 to 3 days -3.73% (2,973 on 20, 48% stopped); 3 days or more -4.24% (6,713 on 18, 45% stopped). The price at the stop cycle averages -19.9% for tokens 6 to 24 hours old, -16.0% at 1 to 3 days and -13.6% at 3 days or more. The typical buy of a young token is still a stop, filled further past its level the younger the token.

**What the last reviews asked, answered.**

- `python3 -m bot.replay` with the v7 rules reproduces NIO, GTA and FLOAT, each within 0.1 points of the journal: 20 closed on 15 tokens, 10 wins, +3.78% (it was +5.52% on 18).
- `python3 -m bot.replay --baseline`, v7 rules. Bot's universe: every eligible cycle 14,217 on 59 tokens, 33% wins, -4.12% (was -4.16%); the first passing cycle of each run 45 on 15 tokens, 51% wins, +3.63% (was +4.88% on 42). Wide, ages 3 to 30 days: every cycle 23,871 on 46 tokens, -3.86% (was -3.49%); first passing cycles 79 on 17 tokens, 52% wins, +3.24% (was +2.97% on 73). The first rows are steady. The three first signals added on the bot's universe since 22:30 averaged -13.8% (NIO, and GTA at 03:25 and 03:45), which is what "do not expect them" meant.
- The 300-trade floor, forward check (entries on 150 to 299 trades opened after 06:45 UTC on 16 Nov, wide replay with `entry.min_txns_h1=150`, tokens 3 to 30 days old): 6 closed, 1 win. DIGS 13:20 +24.4% (it read +19.7% with the old trail), Max 13:55 -15.8%, STANK 17:10 -18.3%, CJ 17:30 -18.7%, FLOAT 21:00 -14.8%, RAMBO 22:15 -14.3%. The test needs 10 closed and calls the floor wrong at 3 winners or more.
- The floor's other test (2 winners or fewer in the first 10 closed trades on tokens 3 days or older): 1 of 4 (Max, Rings, paws, NIO). It needs 2 more winners in the next 6 to pass. FLOAT is the fifth.
- Trailing exits: none new. The table in the 22:30 entry stands at five rows.
- Discovery, interim (due after 12:35 UTC today, so not read as a test yet). Since 12:35 on 16 Nov 24 tokens have passed the universe. By the feed that found them: `profiles_latest` 11, GeckoTerminal before pages were labelled 7, `boosts_top` 3, one each from `gecko:trend2`, `gecko:tx4` and a trending meta. 59 tokens from the deeper pages (`gecko:vol5` to `vol8`, `gecko:tx4` to `tx6`) were on the watchlist at some point in that time and one of them passed: HOGE, the same one as before. Since the age floor fell to 3 hours it is the profile feed that supplies the young tokens, not the deeper pages.
- `suspect_price`: no row, so the guard change from 22:30 has still not met a bad print.
- Watchlist size: peaked at 266 at 22:55 and is back at 213. `api_calls` never passed 50.

**Changed.** Nothing. Rulebook v7 stays; no code change; 42 tests pass. v7 is eight hours old with one closed trade, a signal fired 35 minutes before the review, and the two exit ideas the new trades raised both fail on the record.

**For the next review.**

- FLOAT: record the exit. It counts in the "3 days or more" row, for the floor's test and as the third burst entry.
- Discovery is due: after 12:35 UTC, count as above. If HOGE is still the only token from a deeper page that passed the universe, put `top_volume_pages` back to 4 and `top_tx_pages` to 3 (one token in 41 hours that the trade-count list's page 4 found; the volume pages 5 to 8 have found none), or keep `top_tx_pages` at 4 for HOGE's sake and say why. That is a discovery-section change and would be the one change for that review.
- `batch_miss`: the number to watch is `batch_miss` less the never-seen tokens on the watchlist (2 to 7 now). If it nears 15, tokens with a data history start missing lookups. Also count never-seen tokens that first return data with a pool of $30k or more after more than two cycles on the watchlist (0 of 10 so far); one of those would mean the address order is hiding a live token, and the fix is to rotate the leftover lookups.
- Young tokens: 3 of 15 closed, 2 of 5 stops. Each new trailing exit: the trail level, the fill, and what `--set exit.trailing_stop_pct=10` gives.
- LP locked under 50%: 0 wins of 4. Two more losers with no winner and it is worth testing as a floor in the safety section (a tightening); check first how often the figure for one token moves across the line between two readings.
- Everything under "For the next review" in the 16 Nov entries still stands.

**Would prove this review wrong.**

- Leaving the stop alone for young tokens is wrong if the first five young-token stops include three where the price was back above the entry within an hour of the stop (GTA is one of two so far; rockstar was not). Then redo the age table on the longer record before touching anything.
- Dropping the break-even stop is wrong if, on a week of data, it is ahead by a point or more on both records and on the first signals as well. On today's record it is not ahead on either count.
- The `batch_miss` verdict is wrong if a token with a pool over $30k is missing from a snapshot on one cycle and back on the next while `batch_miss` less the never-seen count is over 15, or if `api_calls` passes 55.
- Leaving the rules alone is wrong by the tests the earlier entries set, which are unchanged: the 5% trail (22:30 on 16 Nov), young tokens (12:30), the 300-trade floor (06:30).
- The health verdict is wrong if the gap between cycles grows past 15 minutes or skipped cycles become regular.

### v7, 2026-11-16 22:30 UTC review: the trailing stop is 5% under the best price, was 10% (plumbing: a second trigger a minute later cannot confirm a bad price print)

**Health.** 979 cycles since launch, 96 since 14:40 UTC. Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 10.0. Two cycles were skipped (none between 18:55 and 19:05, none between 21:30 and 21:40); with the one at 12:55 that is three in ten hours. The last review said to tell Ajeeb at more than two in six hours. It is two, so no message, and the gap never reached 15 minutes. Three extra cycles (17:41, 19:53 and 21:59, each 30 seconds to 2 minutes from its neighbour; both triggers fired). The newest cycle was 1.9 minutes old when the review started, so no `.kick`. No error in any of the 96 cycles. `api_calls` 48 to 50, `allowed_pool_used` 4 to 6, watchlist 208 to 261 (cap 300; it was 185 to 215), universe 9 to 17 tokens a cycle (median 13). RugCheck ran for all 5 signals and every answer parsed: `score_normalised` 1 and no risks on four, 29 with one `warn` on Max; LP locked 41.7% to 84.6%. No `safety:*`, `skip:*` or `suspect_price` rows.

The lookup change from 14:35 passed its test. `batch_miss` was 14 to 17 (median 15) and over the 15 single lookups on 46 of the 96 cycles. `api_calls` stayed under 55. A token was missing from one snapshot and back in the next 16 times; I read the watchlist as it stood on eight of those cycles, including all five with more than 15 misses, and every one of those tokens had data on that cycle (`last_ok` set to it). They were out because their pool read under the watchlist's $30k floor for one cycle. No token with a live pool went unpriced.

**Bug fixed: two cycles a minute apart could confirm a bad price print.** The guard against bad prints ignores an impossible reading for one cycle and acts if "the next cycle" shows it again. That assumed cycles five minutes apart. When both triggers fire, or one cycle starts late and the next on time, two cycles run 30 seconds to 4 minutes apart (29 of the 978 gaps so far are under 4 minutes, 16 of them under 2.5), and a bad print can outlive that. The record has the case: CJ on 15 Nov read +42% on almost no volume at 21:17:34 and again at 21:20:14, and was back at its old price at 21:25. A position in CJ would have ignored the first reading and sold half at the second, at a price nobody paid. The bot did not hold CJ, so no real trade was affected. The review tools were: in the any-moment yardstick 39 CJ positions had booked that sale (+10.8% on average); without it they end at -16.1%.

- `hold_suspect` in `bot/strategy.py` now takes the time of the reading. A reading less than four minutes after an ignored one cannot confirm it: while the price is still more than +25% or -20% away from the last accepted price it is ignored too, and it does not use up one of the two cycles a position may be ignored for. The first cycle four minutes or more after the ignored reading decides, as before, so with cycles on time nothing changes and a real move is still delayed by one normal cycle at most. `bot/run.py` and `bot/replay.py` pass the time in.
- Tests: 2 added (the rule itself with CJ's numbers; a scripted position that sees a +42% print on two cycles a minute apart, takes no profit, carries on, and is still stopped on a real fall at the next normal cycle). Both fail on the old code. 42 pass.
- Effect on the review tools: the replay's own trades are unchanged to the hundredth. `--baseline` on the wide record moves from -3.59% to -3.64% for a buy at every cycle (the 39 CJ positions).
- Known limit, not changed: a bad print that lasts two normal cycles is acted on at the second. A rough count over every token in the record, held or not: about 14 bad-print episodes, of which three lasted two normal cycles or more (Dacity twice, TrumpWars). Dacity is over 30 days old and TrumpWars' pool is under $50k, so the bot could not have held either. (gtacoin looks like a fourth and is not: its row flips between two pools, one of them a dead SOL pool with a frozen price, which the 24-hour volume floor rejects. A held token is priced on its own pool.) Waiting two cycles would delay every real crash by ten minutes, so this stays as it is unless a trade is hit.

**Strategy: v6 closed 5 trades, 2 wins, -2.47% a trade (-0.0589 SOL). Five trades are hints, not findings.** Equity 4.5425 SOL (-9.15%; it was 4.5784). All versions: 17 closed, 5 wins on four tokens, -5.67% a trade, max drawdown 10.2%. SOL $70.4 to $71.9.

| # | Token | Opened (UTC, 16 Nov) | Age | Trades in the hour before | 1-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|---|
| 13 | rockstar | 14:30 | 1.15 days | 459 | +8.9% | 0.0% | stop, price at -14.5% | -16.37% |
| 14 | Max | 14:40 | 4.7 days | 319 | +2.5% | +16.6% | stop, price at -17.8% | -20.33% |
| 15 | HOGE | 15:20 | 1.35 days | 1,286 | +18.7% | +39.6% | half sold at +30.1%, rest trailed out at +11.6% | +17.03% |
| 16 | Rings | 17:00 | 5.9 days | 526 | +18.4% | +65.1% | half sold at +24.7%, rest trailed out at +32.4% | +23.97% |
| 17 | paws | 18:00 | 20.6 days | 300 | +16.1% | +10.3% | stop, price at -13.8% | -16.63% |
| 18 | NIO | 20:50 | 26.2 days | 300 | +2.2% | +9.0% | open at +5.9% | |

- Young tokens (rockstar, HOGE): 2 closed, 1 win, +0.33% a trade, +0.0016 SOL. Tokens 3 days or older on the same rules and the same day (Max, Rings, paws): 3 closed, 1 win, -4.33%. Two against three trades says nothing yet. No `liquidity_drop`, no write-off, and the day's young trades cost nothing, so none of the 12:30 entry's tests for the age change is close. The day used 8 of its 10 new trades, 2 of them young: the older tokens were not crowded out.
- The youngest band is now seen but not traded: 20 tokens passed the universe since 12:35, 9 of them under 3 days old, and four of those were first eligible at about 3 hours old (DSP on 30 cycles, GTA 19, COGE 3, ROCCO 2). None gave a signal.
- Stops. rockstar's stop cycle read -14.5% (the reading before: -8.6%), 2.5 points past the level: the first of the five young-token stops the 14:35 entry's age test asks for, and inside its 3 points. Max read -8.8% and then -17.8% on $27.6k of volume in the five minutes, a 9-point fall in one cycle in a token 4.7 days old; it had been held 5 hours 45 minutes. paws read -3.9% and then -13.8%. All 12 stops so far lost, average -16.69%, total -0.9532 SOL; the price at the stop cycle averages -14.6%, 2.6 points past the level, with every one of those cycles on time. The five trailing exits made +0.4796 SOL.
- Max peaked at +16.6% and ended at the stop, the shape STANK had on 14 Nov. Tested as a lower first target on a buy at any moment (same entries, with the 5% trail): a target of 15% moves the mean by +0.2 and +0.1 points (bot's universe and wide) with tokens split 21 better to 13 worse and 16 to 13; a target of 10% makes the entry rules' own picks worse. No case for it.
- paws was bought on one burst. Its trades in the hour went from 76 to 300 in a single cycle (227 trades and +13.8% on price in five minutes), which is the first cycle the 300-trade floor let it through. Tested as an idea ("not when most of the hour's trades came in the last five minutes") against all cycles: only two first signals in the whole record had more than a third of the hour's trades in the last five minutes (paws, and RAMBO on 16 Nov at 03:25), both stops. But a buy at any cycle like that, with 300 or more trades in the hour, made -0.5% and 0.0% (35 and 37 cycles on 17 and 16 tokens), better than the average cycle. Two trades and a yardstick that points the other way: dropped.
- Max is the first trade with a RugCheck score near the limit (29 against 30) and it lost. LP locked: rockstar 48.5% lost, NIO 41.7% is open. Every closed trade under 50% lost (Rings 26.2%, STANK 40.5%, rockstar 48.5%), and so did 9 of the 14 at 60% or more. The figure is not stable either: Rings read 26.2% at 01:45 and 78.8% at 17:00. Still a hint.
- The cooldown: with no cooldown the yardstick would have bought Rings again at 18:40 (-17.8%) and HOGE at 18:30 (-16.2%), each after its winning trade. Two more cases for keeping it.
- 5 signals in the 8 hours since 14:40, the last at 20:50, so the 12-hour rule is not met. Funnel, 1,239 universe-token checks: `h1_weak` 522 (42%), a token in its cooldown 266, the held token 151, `txns_h1` 143, `h1_overheated` 53, `buy_pressure` 45, `h6_down` 38, `m5_dropping` 12, `h24_dumped` 3, `volume_accel` 1, signal 5.

**What the last reviews asked, answered.**

- The 300-trade floor, forward check (entries on 150 to 299 trades opened after 06:45 UTC on 16 Nov, wide replay with `entry.min_txns_h1=150`, tokens 3 to 30 days old): 4 closed, 1 win. DIGS 13:20 (245 trades, a $34k pool outside the universe) +19.7%; Max 13:55 (259) -15.8%, the same fall the real trade 14 took; STANK 17:10 (155) -18.3%; FLOAT 21:00 (245) -14.8%. Two open: CJ 17:30 (255) at -10.4% and RAMBO 22:15 (161) at -9.7%. The test needs 10 closed and calls the floor wrong at 3 winners or more.
- The floor's other test (2 winners or fewer in the first 10 closed trades on tokens 3 days or older): 1 of 3. The bot now buys on the first cycle the count reaches 300: Max at 319, paws and NIO at exactly 300.
- `python3 -m bot.replay --baseline`, wide record, ages 3 to 30 days, with the rules as they stood (v6) and the guard fix in: every eligible cycle 21,540 on 43 tokens, 34% wins, -3.64%; the first passing cycle of each run 73 on 16 tokens, 52% wins, +1.67% (it was +1.83% on 50 at 14:35). The bot's universe, young tokens included: 12,757 cycles on 55 tokens, -4.32%; first passing cycles 42 on 13 tokens, 55% wins, +2.78%.
- `python3 -m bot.replay` with the v6 rules reproduces the five v6 trades, each within 0.1 points of the journal.
- Discovery: not due until 12:35 UTC on 17 Nov. HOGE (`gecko:tx4`) is still the only token from a deeper page that has passed the universe; the bot traded it once (+17.03%).

**The trailing exits: the half kept after the first target has been sold far under its trail level, five times out of five on average and badly on three.**

| # | Token | Half sold at the target | Best while held | Trail level (best less 10%) | Kept half sold at | Under the level |
|---|---|---|---|---|---|---|
| 5 | WASTED | +25.2% | +44.1% | +29.7% | +25.2% | 4.5 points |
| 7 | WASTED | +23.7% | +68.1% | +51.3% | +18.8% | 32.5 |
| 12 | BLOB | +21.8% | +41.7% | +27.5% | +26.6% | 0.9 |
| 15 | HOGE | +30.1% | +39.6% | +25.6% | +11.6% | 14.0 |
| 16 | Rings | +24.7% | +65.1% | +48.6% | +32.4% | 16.2 |

- The kept half was sold 13.6 points under its trail level on average. It was sold at +22.9% on average; the half sold at the target got +25.1%. So over five winners that peaked at +52% on average, trailing the second half earned less than selling it with the first.
- Why. The bot sees one price every five minutes. The 14:35 entry measured how far these tokens move between two readings: the 90th percentile is 4% for a token 3 days or older and 7% to 10% for a younger one. After a run to +40% or +60% the moves are larger still (HOGE: +39.1%, +28.9%, +11.6% on three readings; Rings: +65.1% then +32.4%). A level 10% under the peak is crossed by a fall that is already well past it when the bot looks.
- The 14 Nov 23:35 review named this and set a test: the exit section is the candidate if the next two trailing exits both fill more than 5 points under the level. BLOB came next (0.9) and ended that test. The two since are 14.0 and 16.2, both v6's own trades.
- A 5% trail, the number that review named, on the same entries. It was not picked today from several.

| Measured on | Trades or positions | 10% trail | 5% trail | Better / level / worse |
|---|---|---|---|---|
| Replayed trades that reached the first target (bot's universe and wide together) | 14 on 11 tokens | | | 7 / 7 / 0 |
| The same, bot's universe (v6 rules) | 9 | +22.72% | +26.92% | 4 / 5 / 0 |
| The same, wide, ages 3 to 30 days | 9 | +18.25% | +22.21% | 5 / 4 / 0 |
| A buy at any cycle that reached +20%, bot's universe | 2,846 on 39 tokens | +24.65% | +25.22% | tokens: 21 better, 6 worse |
| A buy at any cycle that reached +20%, wide | 4,744 on 39 tokens | +19.56% | +20.17% | tokens: 23 better, 5 worse |
| A buy at any cycle, all of them, bot's universe / wide | 12,757 / 21,540 | -4.32% / -3.64% | -4.19% / -3.51% | |

  ("Level" is within 0.2 points. The 7 better: WASTED twice, WOHAIHAO, HOGE 15:20, CJ, GTA6, DIGS.)
- Of the five real trailing exits a 5% trail would have been better on three (WASTED +25.7% against +20.8%, WASTED +40.6% against +21.1%, HOGE +25.9% against +17.2%), the same on BLOB and 0.2 points worse on Rings, where it sells at 17:55 at +32.6% and misses the run to +65% that the 10% trail also failed to keep.
- It holds forward. Since the number was named on 14 Nov 23:35, eight replayed trades have been opened and reached the first target: four better with 5% (WOHAIHAO, GTA6, DIGS, HOGE 15:20), four level, none worse.
- It points one way. A 7% trail sits between the two (better on 15 to 17 tokens, worse on 4 to 6). A 15% trail is worse than 10% on 24 and 26 of the 38 and 39 tokens. On the bot's universe 5% beat 10% on three of the four days and was level on the fourth (-0.1 points on 14 Nov); on the wide record on all four. It holds in each age group (under 1 day +1.0 points, 1 to 3 days +0.6, 3 days or more +0.3).
- How weak it is. The gain is small: 0.6 points on a position that reached the target and 0.13 points a trade over all of them. Costs are about 3%. The 06:30 review's exit table, made with a stricter method on the record as it stood then, had the 5% trail level with the 10% (-3.98% against -3.92% on the bot's universe, -3.05% against -3.21% wide), and its conclusion stands: exits move the losses around and the edge, if there is one, has to come from the entry. The large numbers (+4 points on the replay's own winners) are 14 trades on a record the 5 has now been looked at on twice. And a 5% trail gives up the rare long run: it will usually sell the kept half within a cycle or two of the first target.

**Changed: rulebook v7, exit section only. `exit.trailing_stop_pct` 10 to 5. A hypothesis, on hints.**

- Why act on five trades. The mechanism does not depend on them: the trail is narrower than the distance these tokens move between two readings, so its level is not where it sells. The number was named two days before the trades that now support it. No trade and no token on the record did worse with it by more than 0.2 points among those the rules picked. And the counterfactual stays exact: for every trailing exit from here, `python3 -m bot.replay --set exit.trailing_stop_pct=10` shows what the old trail would have done on the same entry.
- What it does not do. It does not touch the stop, the first target, the 6-hour limit, the universe, the entry rules, the portfolio, the safety screen or the costs. It changes nothing for a trade that never reaches +20%, which is 12 of the 17 so far. It does not make the strategy profitable.
- What it does to the open tests. The young-token tests compare young and older tokens on the same days, and both get the same exit, so they carry on across v6 and v7 (use the report's age table, which spans versions). The 300-trade floor is read on winners and losers and in the wide replay, and a trade that reached +20% is a winner under either trail. v6 ends at 5 closed trades. NIO (trade 18) was opened under v6 and is labelled v6; if it reaches +20% from here its kept half is trailed at 5%.
- On the same record with v7: `python3 -m bot.replay` 18 closed on 13 tokens, 10 wins, +5.52% (v6: +3.42%); wide, ages 3 to 30 days, 23 closed on 16 tokens, 10 wins, +0.21% (v6: -1.34%). `--baseline` for the next review to compare with: bot's universe every cycle 12,778 on 56 tokens, -4.16%, first passing cycles 42 on 13 tokens, +4.88%; wide every cycle 21,557 on 43 tokens, -3.49%, first passing cycles 73 on 16 tokens, +2.97%. These are read off the record the change was checked on. Do not expect them.

**Changed, in full.**

1. Rulebook v7: `exit.trailing_stop_pct` 10 to 5, `version`, `notes`.
2. Plumbing, no rule in it: the wait in `hold_suspect` (above), with `bot/run.py` and `bot/replay.py` passing the time.
3. README: the strategy paragraph (v7, the 5% trail) and one sentence in the bad-print honesty rule.
4. Tests: 2 added. 42 pass.

**First live cycle (22:50 UTC).** Pushed just before 22:50 UTC and picked up by the 22:50 cycle: v7, no errors, `api_calls` 50, `batch_miss` 16, universe 15, no signal. NIO was read and carried on as usual (+5.0%, no `suspect_price`), so the changed guard ran on an open position without incident; it has not yet met a bad print. v7 trades start from the 22:50 cycle.

**For the next review.**

- Each new trailing exit: the trail level (best less 5%), the fill, and what `--set exit.trailing_stop_pct=10` gives for the same entry. Keep the table above going.
- Cycle gaps: two skipped cycles in the last six hours and three extra ones. If a third is skipped inside six hours, or any gap passes 15 minutes, tell Ajeeb.
- `suspect_price` rows: after one, check that the position's next accepted reading was at least four minutes later and that no fill happened on the cycle in between.
- Watchlist size: 261 against a cap of 300. At the cap the bot drops rejected and thin tokens first, so nothing breaks; note it if `api_calls` passes 55.
- Young tokens: 2 of the 15 closed trades the 12:30 entry asks for, 1 of the 5 stops the 14:35 entry asks for (2.5 points past the level).
- The 300-trade floor: 4 of 10 closed in the forward check (1 winner); where CJ 17:30 and RAMBO 22:15 end.
- Discovery: due after 12:35 UTC on 17 Nov, as the 14:35 entry set out.
- NIO: record the exit. LP locked 41.7%.
- Everything under "For the next review" in the 14:35, 12:30 and 06:30 entries still stands.

**Would prove this review wrong.**

- The exit change is wrong if, over the next 10 trailing exits, the 10% trail would have done better on the same entries by more than 2 points a trade on average, or better on 5 or more of the 10. Then put it back to 10. One long run kept by the old trail can do the first by itself, so read both numbers.
- It is also wrong if it keeps selling into noise: if 3 of the next 5 kept halves are sold under +15% while the token is above the first target's price again an hour later.
- It made no difference, and the exit section should then be left alone for good, if after 10 trailing exits the two trails are within 1 point a trade of each other.
- The guard fix is wrong if a real move is held back for more than one normal cycle (two `suspect_price` rows on one position more than four minutes apart, followed by a fill at about the same price), or if a position's close shows a stop or a take-profit filled on a reading that reversed on the next cycle after two triggers fired together.
- Leaving the entry, the stop and the first target alone is wrong by the tests the 06:30 and 12:30 entries set, which are unchanged.
- The health verdict is wrong if the gap between cycles grows past 15 minutes or skipped cycles become regular.

### v6, 2026-11-16 14:35 UTC review: no rule change (plumbing: single lookups go first to tokens that have had data)

**Health.** 882 cycles since launch, 95 since the 06:30 review. Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 10.2: one cycle was skipped (none between 12:50 and 13:00), the first skipped cycle since the external scheduler started. One extra cycle (13:30, 34 seconds after the one before; both triggers fired). The newest cycle was 2.3 minutes old when the review started, so no `.kick`. No error in any of the 95 cycles. `api_calls` 46 to 48, watchlist 185 to 215 (cap 300), `allowed_pool_used` 4 or 5. RugCheck ran once (rockstar, 14:30) and parsed: `score_normalised` 1, no risks, LP locked 48.5%. No `safety:*`, `skip:*` or `suspect_price` rows.

**Plumbing fixed: the test the 06:30 review set for the single lookups is met.** `batch_miss` was 13 to 17 per cycle (median 14) and over the 15 single lookups a cycle allows on 31 of the 95 cycles (it was 10 of 100). Twelve tokens on the watchlist have never returned data, all from `profiles_latest`; they take 12 of the 15 lookups every cycle. Six times a token with a live pool was missing from one snapshot and back in the next. Three of the six were on cycles with 16 misses (JAG at 07:35 and 08:15, CYBERDACITY at 08:10), which is the case that review named: a token that has returned data before going unpriced because the lookups ran out. None of the three was in the universe, so no trade was affected. Under v6 it matters more than it did: five of the six tokens that dropped out were under two days old, and young tokens can now be bought.

- `fetch_views` in `bot/run.py` now looks up tokens that have returned data before (`last_ok` set on the watchlist) ahead of tokens that never have. The cap of 15 is unchanged, so `api_calls` does not move. Held tokens were already looked up first and outside the cap.
- Test added: 18 tokens with no pool and one live token the batch call leaves out. The live token is still priced, on the watchlist and in the snapshot, and the lookups stay at 15. It fails on the old code. 40 pass.

**Strategy: v5 closed no trade and v6 has none closed, so there is nothing to judge.** v5 ran 70 cycles (06:50 to 12:30) with no signal. v6 has run 24 cycles (from 12:35) and opened its first trade on the newest one. Equity 4.5784 SOL (-8.43%; it was 4.5853, and the difference is the cost of the open trade's buy). All versions: 12 closed, 3 wins, -7.00% per trade, unchanged. SOL $71.0 to $71.2.

| # | Token | Opened (UTC, 16 Nov) | Age | Trades in the hour before | 1-hour change at entry | Pool | Status |
|---|---|---|---|---|---|---|---|
| 13 | rockstar | 14:30 | 1.15 days | 459 | +8.9% | Meteora, $104k, LP locked 48.5% | open |

- rockstar is the first trade on a token under 3 days old. It passed the entry rules at 14:05, 14:15, 14:20 and 14:25 as well and was held back each time by `liquidity_falling`: the pool's liquidity was 11% to 18% under its one-hour high ($111.9k at 13:55). At 14:30 it was 7% under and the buy went through, at a price 10% below the 14:05 reading.
- What to expect from it, written before the result. In the three hours before the buy, rockstar's price moved 5% or more between two cycles on 18 of 35 cycles and 8% or more on 8 (largest fall in one cycle: 9.3%). The stop is 12% from the entry and the first target 20%. On a token that moves like this, whichever is hit first says little about the entry.
- No signal from BLOB (05:35) to rockstar (14:30): 8.9 hours, so the 12-hour rule is not met. Funnel since 06:45, 779 universe-token checks: `h1_weak` 495 (64%), `h6_down` 88, `txns_h1` 88, a token in its cooldown 44, `h1_overheated` 28, `buy_pressure` 23, `m5_dropping` 7, `liquidity_falling` 4, `h24_dumped` 1, signal 1.

**Young tokens: what v6 let in so far (two hours, hints only).**

- 13 tokens have passed the universe since 12:35, 11 a cycle on average (v5: 7). Five are under 3 days old: Anthropig (19 hours), SWJ (1.0 day), rockstar (1.1), HOGE (1.3), HYGG (1.5). None was under 18 hours old, so the youngest band the change opened is still untested. `u:too_young` fell from about 30 a cycle to 2, but most of those tokens fail another test (liquidity, or liquidity against market cap).
- New measurement: how far the price moves between two cycles, by age. Every pair of consecutive readings of a token inside the v6 universe, whole record:

| Age at the reading | Pairs of readings (tokens) | Median move | 90th percentile | Share that fell 12% or more in one cycle |
|---|---|---|---|---|
| under 1 day | 2,982 (33) | 1.9% | 9.8% | 3.05% |
| 1 to 3 days | 2,882 (20) | 1.3% | 7.3% | 1.87% |
| 3 days or more | 6,434 (17) | 1.1% | 4.2% | 0.22% |

  A fall of the whole stop distance inside one cycle is 8 times as common in a token 1 to 3 days old as in an older one, and 14 times as common under a day. That is the mechanism behind the stops that filled at -20% to -24% on price in the replay of young tokens. A position is held for up to 72 cycles, so on a young token a stop filled well past its level is the expected case, not the rare one. Not acted on: no young trade has closed, v6 is two hours old, and the remedies named at 12:30 (a smaller position or a higher liquidity floor for young tokens) both need code and one of them is a different section.
- `python3 -m bot.replay` with the v6 rules still reads 13 closed on 11 tokens, 8 wins, +5.66% a trade, with HOGE's +59.7% carrying it (without HOGE: +1.2%). It was the basis for the 12:30 entry and has no new closed trade in it.

**What the last reviews asked, answered.**

- The 300-trade floor, forward check (entries on 150 to 299 trades opened after 06:45 UTC on 16 Nov, wide replay with `entry.min_txns_h1=150`, tokens 3 to 30 days old): two, both open. DIGS 13:20 (245 trades, a $34k pool outside the universe) at +1.8%; Max 13:55 (259 trades) at -13.2% after costs, its price 10.5% under the entry and 1.5 points short of the stop. 0 closed of the 10 the test needs. On the bot's own universe the floor also blocked rockstar at 12:10 (270 trades, +22.8% in the replay, trailed out 35 minutes later). rockstar is a young token, which the 12:30 entry said not to count for or against the floor; it is noted here so it is not lost.
- `python3 -m bot.replay --baseline`. Wide record, ages 3 to 30 days: every eligible cycle 18,603 on 42 tokens, 34% wins, -3.60% (was -3.87%); the first passing cycle of each run 50 on 14 tokens, 50% wins, +1.83% (was +0.03% at 06:30). Among the first signals added since is a winner the bot could not trade (GTA6 08:10, +16.7%, outside the universe). It is still mostly the record the number 300 was chosen on, so the wider gap is not new evidence. The bot's-universe row now includes young tokens (50 tokens, -4.29% for a buy at any cycle) and cannot be compared with earlier reviews.
- Discovery, interim. The 12:30 entry moved this test: read it after a day of v6, not at 14:00 today. So far one token from a deeper page has passed the universe: HOGE (`gecko:tx4`, found 00:45 on 16 Nov), on all 24 cycles since 12:35. The other four young tokens came from `profiles_latest`. Pages unchanged.
- Trailing exits and stop fills: no exit since BLOB, nothing new. LP locked: rockstar 48.5%. Only Rings (26.2%) and STANK (40.5%) were lower, and both lost; the other ten trades had 60% or more. Three trades, still a hint.

**Changed.**

1. Rulebook: nothing. v6 stays. It is two hours old with no closed trade, it is Ajeeb's experiment, and a signal fired within the last 12 hours.
2. Plumbing, no rule in it: the order of the single lookups in `fetch_views` (above).
3. Tests: 1 added. 40 pass.

**First live cycles (14:35 and 14:40 UTC).** Pushed at 14:37 UTC and picked up by the 14:40 cycle: no errors, `api_calls` 49 (49 on the cycle before, on the old code), `batch_miss` 15, `no_data` 14, 12 tokens on the watchlist that have never returned data. With 15 misses the lookups did not run out, so the new order has not been put to the test yet. rockstar read -6.1% at 14:40, ten minutes in.

The 14:40 cycle also opened trade 14, after this review's analysis was done:

| # | Token | Opened (UTC, 16 Nov) | Age | Trades in the hour before | 1-hour change at entry | Pool | Status |
|---|---|---|---|---|---|---|---|
| 14 | Max | 14:40 | 4.7 days | 319 | +2.5% | PumpSwap, $136k, LP locked 79.4% | open |

- Max is the first trade on the v5 entry rules in a token 3 days or older, so it is the first that counts for the 300-trade floor. It is the same token the floor blocked at 13:55 (259 trades); the bot bought it 45 minutes later, 7.6% lower, once the count passed 300. The wide replay's 13:55 entry and this one will end close together, so do not count them as two results.
- It is also the first trade with a RugCheck risk on it: `score_normalised` 29 against a limit of 30, one risk, "Copycat token", level `warn`. The answer parsed (the level is read and only `danger` blocks), and the trade was allowed by one point. Not a bug and not a reason to touch the safety section; if trades with a score this close to the limit lose, lowering `max_score_normalised` is a tightening and allowed.
- Open positions 2 of 5, new trades today 4 of 10.

**For the next review.**

- rockstar: record the exit and, if it is a stop, the price at the stop cycle against the 12% level. It counts in the "under 3 days" row only.
- Max: record the exit. It counts in the "3 days or more" row and is the first of the 10 closed trades the 06:30 entry's test for the floor needs.
- The lookup change: on cycles with `batch_miss` over 15, `no_data` should now equal the number of watchlist tokens that have never returned data (12 today), and no token with `last_ok` should miss a snapshot on those cycles.
- Cycle gaps: one cycle was skipped at 12:55. If skipped cycles start to repeat (more than two in six hours), tell Ajeeb; a young token's stop depends on every cycle more than an old one's.
- Discovery: after 12:35 UTC on 17 Nov, count the tokens from `gecko:vol5` to `vol8` and `gecko:tx4` to `tx6` that passed the v6 universe and what the trades on them did. HOGE is one.
- The 300-trade floor: where Max 13:55 and DIGS 13:20 end in the wide replay with `entry.min_txns_h1=150`.
- Everything under "For the next review" in the 12:30 and 06:30 entries still stands.

**Would prove this review wrong.**

- The lookup change is wrong if `api_calls` passes about 55 with the watchlist the same size (it was 49 with one position open before the change and 49 with two after), if a `pair lookup` error starts repeating, or if a token that has returned data before still drops out of a snapshot on a cycle with more than 15 misses. In the last case the batch call is the thing to look at, not the order of the lookups.
- The age table overstates the problem if the first five stops on tokens under 3 days old fill within 3 points of the level, as the stops on older tokens do (2.3 points on average). Then five-minute cycles follow young tokens well enough and no change for them is needed on that account.
- Leaving v6 alone is wrong by the tests the 12:30 entry set, which are unchanged: young tokens' first 15 closed trades losing more per trade than older tokens' over the same days, a single day of young-token trades costing more than 5% of equity, or more than one `liquidity_drop` or write-off in the first 15.
- The health verdict is wrong if the gap between cycles grows past 15 minutes or skipped cycles repeat.

### v6, 2026-11-16 12:30 UTC, at Ajeeb's request: a token can be traded from 3 hours after launch, was 3 days

Not a scheduled review. Ajeeb asked for it after reading the 06:30 note: he believes the volume in young tokens is genuine, not bots, and that a token 3 to 4 hours old with serious buyers and sellers should be considered. It is his experiment and paper money, so the rule is in as a labelled hypothesis and the record will judge it. v5 had run 69 cycles (06:50 to 12:25 UTC) with no error and no trade.

**Changed: rulebook v6, universe section only. `universe.min_age_days` 3 to 0.125 (3 hours).** Everything else a token has to pass is unchanged: $50k liquidity, $100k of 24-hour volume, 500 trades in 24 hours, market cap $300k to $50M, liquidity at least 3% of market cap, a SOL, USDC or USDT pool, the RugCheck screen, and the v5 entry rules (300 trades in the last hour, 1.2 buys per sell, rising volume, a 1-hour change of +2% to +25%). Those are what "serious buyers and sellers" means to the bot. 3 hours and 4 hours give the same trades on the record; 3 is the lower end of what he asked for.

**What the record says about it. Hints only.**

- `python3 -m bot.replay --set universe.min_age_days=0.125` (v5 rules otherwise): 13 trades instead of 6. The 7 new ones are on 6 tokens under 3 days old: 4 wins, +4.23% a trade.

| Token | Opened (UTC) | Age | Trades in the hour before | Exit | Net |
|---|---|---|---|---|---|
| MORI | 14 Nov 01:40 | 6 hours | 796 | trailing stop (best +20.3%) | +7.52% |
| Max | 14 Nov 13:10 | 2.7 days | 529 | stop | -20.45% |
| bill | 15 Nov 02:35 | 7 hours | 10,791 | stop | -23.71% |
| WOHAIHAO | 15 Nov 02:38 | 1.0 day | 7,230 | trailing stop | +12.80% |
| GETAJOB | 15 Nov 11:10 | 20 hours | 870 | stop | -26.24% |
| HOGE | 16 Nov 01:50 | 19 hours | 10,173 | trailing stop (best +114%) | +59.73% |
| WOHAIHAO | 16 Nov 02:20 | 2.0 days | 18,854 | trailing stop | +19.97% |

- The wins are bigger and so are the losses. The three stops filled at -20% to -24% on price against a 12% level; on older tokens the stop cycle averages -14.3%. A young token moves further inside five minutes than the stop can follow. One trade (HOGE) is most of the +4.23%.
- A buy at any moment, same exits, by age (the yardstick from 15 Nov, positions in tokens that left the record marked at their last price): 3 to 6 hours old +3.78% (311 cycles on 12 tokens, median -15.4%); 6 to 24 hours -2.52% (2,669 on 33, median -14.4%); 1 to 3 days -4.10% (2,811 on 19); 3 days or more -4.53% (6,274 on 18). So on this record the young tokens were not worse than the old ones on average, and the typical trade in them was still a stopped-out loss. 302 of the 5,791 positions in tokens under 3 days old (5%) were in a token that left the record while held, which mostly means its pool fell under $30k; the last-price mark flatters those.
- No signal was recorded on a token 3 to 6 hours old, so the youngest band the change opens has no replayed trade at all. Only 12 tokens that young ever passed the other universe numbers.
- The data cannot tell genuine volume from bots. Trade counts and volume are what DexScreener reports; a launch-day pool with $4M to $13M of volume against $40k to $160k of liquidity (the deeper GeckoTerminal pages found 14 of those on 15 Nov) reads the same either way. The RugCheck screen and the liquidity floor are the only defences, and they are unchanged.

**Plumbing that the change needed (no rule in it).**

1. `volume_accel` in `bot/strategy.py`. It compared the last hour's volume with one sixth of the 6-hour volume. For a token 3 hours old the "6-hour" volume is everything since launch, so every young token would have looked as if its volume had doubled. Under six hours old, the average is now taken over the hours the token has existed (never less than one). From six hours on nothing changes, so no trade made so far is affected. The replay uses the same function.
2. `python3 -m bot.report` has a new table, "By age of the token at entry" (under 1 day, 1 to 3 days, 3 days or more), so young-token trades can be judged apart.
3. README: the strategy paragraph, the aim line and a new honesty rule about young tokens.
4. Tests: 2 added (the volume test for tokens under six hours old; the age table), 3 adjusted to read the age floor from the rulebook instead of assuming 3 days. 39 pass.

**What this does to the open tests.**

- v5's entry change had no trades when v6 replaced it. The trading rules for a token 3 days or older are identical in v5 and v6, so read v5's tests on v6 trades in the "3 days or more" row. Young-token trades must not be counted for or against the 300-trade floor.
- The discovery test due at 14:00 UTC today was written for a 3-day floor: "no token from the deeper pages has passed the universe" was true because 30 of the 31 they found were under a day old. Those tokens can pass now. Do not put the pages back to 4 and 3 on the old reading. Re-read it after a day of v6: how many tokens from `gecko:vol5` to `vol8` and `gecko:tx4` to `tx6` passed the universe, and what trades on them did.
- On the latest snapshot (12:25 UTC) v6 adds four tokens to the universe, 7 to 11 (rockstar, HOGE, Anthropig, SWJ, all 19 to 30 hours old); none met the entry rules on that cycle.

**First live cycle (12:35 UTC).** Pushed at 12:31 UTC and picked up by the 12:35 cycle: v6, no errors, `api_calls` 46, `u:too_young` 28 to 2, `universe_ok` 7 to 11, no signal (7 `h1_weak`, 1 each of `h1_overheated`, `h6_down`, `m5_dropping`, `txns_h1`), nothing open. v6 trades start from the 12:35 cycle.

**For the next review.**

- Judge young tokens (under 3 days at entry) as their own group. Under about 30 closed trades it is a hint.
- Watch the stop fills on them: the price at the stop cycle against the 12% level. If they keep filling past -20%, the honest options are a smaller position for young tokens (portfolio) or a higher floor for the pool's liquidity when the token is young (universe). Both are tightenings.
- Watch for a young token written off (`no_data` exit) or closed on `liquidity_drop`: that is the drained-pool case the replay cannot see.
- `max_new_trades_per_day` is 10 and `max_open_positions` 5. If young tokens fill those every day, the older tokens are being crowded out and the two groups stop being comparable.
- Everything in "For the next review" of the 06:30 entry below still stands, except the discovery item, replaced above.

**Would prove this change wrong.**

- Young tokens are not worth trading on these rules if their first 15 closed trades lose more per trade than the older tokens' trades over the same days, or if any single day's young-token trades cost more than 5% of equity. Then raise `universe.min_age_days` again (1 day first: the replay's 1-to-3-day entries were 2 wins of 3).
- The belief that the volume is genuine is in doubt if young-token positions end on `liquidity_drop` or a write-off more than once in the first 15, or if RugCheck rejects most young signals (`safety:*` rows in the funnel).
- The `volume_accel` fix is wrong if a token over six hours old ever gets a different value than before (the test pins this), or if young tokens with plainly rising volume are all rejected as `volume_accel`: then look at what `vol_h6` holds for a token that young in `data/snapshots`.

### v5, 2026-11-16 06:30 UTC review: a buy now needs 300 trades in the last hour, was 150

**Health.** 787 cycles since launch, 100 since the last review. Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 5.3. The newest cycle was 1.9 minutes old when the review started, so no `.kick`. One extra cycle (01:06, 1.6 minutes after the one before): both triggers fired, the concurrency group ran them in turn. One error in the 100 cycles: GeckoTerminal 429 on page 1 of the trade-count list at 06:30, fetched on the next cycle. No `gecko ... p5` to `p8` or `p4` to `p6` line, so the deeper pages still answer. `allowed_pool_used` 4 or 5, `api_calls` 43 to 48 (was 41 to 47), watchlist 185 to 215 (cap 300), no `pool lookup` error. RugCheck ran twice (Rings 01:45, BLOB 05:35) and both answers parsed: `score_normalised` 1, no risks, LP locked 26.2% and 100.0%. No `safety:*`, `skip:*` or `suspect_price` rows. No bug found in the trading path, so no change to `bot/`.

`no_data` is up: 9 to 17 per cycle (median 13, was 10), and `batch_miss` 11 to 17 (median 13) out of about 255 tokens. It is not the deeper pages. All 14 tokens on the watchlist that have never returned data came from DexScreener's `profiles_latest` feed (a profile for a token with no Solana pool yet); each drops off after 24 hours. On 10 of the 100 cycles `batch_miss` was 16 or 17, over the 15 single lookups a cycle allows, so one or two tokens went without a lookup. I looked for harm and found none: of the 32 times a token was missing from the snapshots for a few cycles, one fell in those cycles, and a held token is always looked up first. Not changed. See "For the next review".

**Strategy: v4 closed 3 trades, 1 win. v3 and v4 have the same trading rules: together 6 closed, 2 wins. Six trades are hints, not findings.** Equity 4.5853 SOL (-8.29%, was 4.5583), nothing open. v4 -2.88% per trade, v3 and v4 together -3.73%. All versions: 12 closed, 3 wins on two tokens (WASTED twice, BLOB), -7.00% per trade, max drawdown 10.2%. SOL went from $72.2 to $71.0.

| # | Token | Opened (UTC, 16 Nov) | Trades in the hour before | 1-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|
| 11 | Rings | 01:45 | 843 | +14.3% | 0.0% | stop, price at -12.0% | -14.96% |
| 12 | BLOB | 05:35 | 2,798 | +2.4% | +41.7% | half sold at +21.8%, rest trailed out at +26.6% | +21.20% |

- Rings (Meteora pool, $57k). The price jumped 55.6% in one cycle at 00:45 and then went sideways for an hour. The 1-hour change read +42% to +74%, over the 25% cap, until that jump left the hour: +73.7% at 01:40, +14.3% at 01:45. The bot bought a price 4% lower than it had been 50 minutes earlier. It was stopped twenty minutes later, on the level (-12.0%). Afterwards the price moved between -18% and +15% of the entry for three hours, never reached the +20% target, fell 49% in one cycle at 05:05 (liquidity $56k to $40k, so a real move) and stood 28% under the entry at 06:40. The stop was right. A 20% stop would have filled near -50%.
- Rings had 26.2% of its LP locked, the lowest of any trade so far (the others: 40.5% to 100%). The safety section has no floor for it. One trade; recorded, not acted on.
- BLOB (PumpSwap, $205k). Found by the boost feed at 05:30 and bought five minutes later, on the first cycle its 1-hour change was over +2%, with volume at 4.7 times its 6-hour average. The trail level was +27.5% (peak +41.7% less 10%) and the fill +26.6%: 0.9 points under. A 5% trail would have sold on the same cycle. Ten minutes after the exit the price was +4.7% over the entry. Nothing was left on the table that a rule here could have taken.
- Trailing exits, the test set on 14 Nov 23:35 (the next two both more than 5 points under the trail level): the first of the two is 0.9 points under. The three so far: 4.5, 32 and 0.9.
- Stops: all 9 lost, average -16.33%, total -0.7068 SOL; the three trailing exits made +0.2921 SOL. Across the 9 the price at the stop cycle averages -14.3%, 2.3 points past the level, with every cycle on time.
- Both new trades came from the shallow sources (Rings from `gecko:trend2`, BLOB from `boosts_top`).

**What the last review asked, answered.**

- `python3 -m bot.replay --baseline`, with the rules as they stood (v4):

| Positions opened at | Bot's universe: cycles (tokens) | Win rate | Mean | Wide, ages 3 to 30 days: cycles (tokens) | Win rate | Mean |
|---|---|---|---|---|---|---|
| every cycle a token was eligible | 5,437 (17) | 29% | -4.92% | 15,856 (41) | 33% | -3.87% |
| cycles the entry rules passed | 70 (7) | 50% | -0.73% | 147 (19) | 35% | -4.03% |
| the first passing cycle of each run | 25 (7) | 48% | -0.62% | 60 (19) | 35% | -3.89% |

  The first row moved 0.6 points on 15% more record (it was -4.32% and -3.27%), so the yardstick is steady enough to use. On the wide record the v4 entry rules still picked moments no better than no rule at all. On the bot's own universe 44 of the 70 passing cycles are still WASTED.
- The relaxations it listed: WASTED 20:30 on 15 Nov (bought with `h6_change_min_pct` -5) ended at the time stop, -11.9%. FLOAT 17:45 (bought with `min_volume_accel` 1.0) ended at the time stop, -3.7%. Not relaxing was right for the third review running. There were signals at 01:45 and 05:35, so the 12-hour rule is not met.
- Its test for leaving the rules alone (4 or more winners in the next 10 closed trades): 1 of 2 when the rules changed below. It ends unread.
- v3's test for the 150-trade filter (2 winners or fewer in its first 10 closed): 2 of 6. The change below goes further the same way and replaces it.
- Discovery, interim (the test is due at 14:00 UTC today): from 13:45 on 15 Nov to 06:40, read from 208 versions of `data/state/watchlist.json`, the deeper pages (`gecko:vol5` to `vol8`, `gecko:tx4` to `tx6`) found 43 tokens. 31 reached the snapshots; 30 of those were under a day old when first seen, 25 under two hours old; the other is XTO (market cap far over the ceiling). None has passed the universe filters. Still heading for a fail. Not touched: one section per review, and it is not due.

**New measurement 1: the exits against a buy at any moment. No exit setting is the problem, and none can be the fix.** The stops have lost 0.71 SOL, so the obvious question is whether the 12% stop is too tight. A scratch version of the baseline answers it on far more than 9 stops: open a position at every eligible cycle, run it through each exit variant, and compare the same entries. Two fixes to make that fair: only entries opened at least 13 hours before the end of the record count, and a position whose token left the record is marked at its last price instead of being dropped (the built-in `--baseline` drops them, which flatters wide stops and long holds, so do not read `--baseline --set exit.stop_loss_pct=30` at face value).

| Exit variant | Bot's universe, 4,636 entries on 15 tokens | Wide, ages 3 to 30 days, 13,438 entries on 36 tokens |
|---|---|---|
| live (12% stop, 6 hours) | -3.92% | -3.21% |
| stop 8% | -3.90% | -3.52% |
| stop 16% | -3.32% | -2.77% |
| stop 20% | -2.99% | -2.59% |
| stop 30% | -2.22% | -2.28% |
| hold at most 2 hours | -3.12% | -3.24% |
| hold at most 1 hour | -2.87% | -3.03% |
| sell everything at +20% | -4.01% | -2.61% |
| trail 5% | -3.98% | -3.05% |

- Every variant lands between -2.2% and -4.0%. A round trip costs about 3%. That is what a market with no drift does to any exit rule: exits move the losses around, they do not make or remove them. The edge, if there is one, has to come from when the bot buys.
- Under the live exits 48% of any-moment buys on the bot's universe (43% wide) ended at the stop within six hours. A 12% fall inside six hours is an ordinary event for these tokens, not a sign that a trade was wrong.
- A 20% stop reads 0.6 to 0.9 points better. Not acted on, for four reasons. Of the entries stopped at 12%, the 20% stop ended better on only 41% to 45%. On the bot's universe the per-token average does not move (-2.93% against -2.96%). The bad cases get much worse (Rings: about -50% instead of -15%). And it is under a point on a record where every figure is within a point of the costs.

**New measurement 2: the same yardstick, split by how many trades the token had in the hour before the signal.** Wide record (every recorded token 3 to 30 days old), live exits, the first cycle of each run of signals, with `entry.min_txns_h1` set to 50 so the entries v3 blocks are in the table too:

| Trades in the hour before | First signals (tokens) | Wins | Mean | Tokens with a positive average |
|---|---|---|---|---|
| 50 to 149 | 44 (15) | 4 | -13.50% | 0 of 15 |
| 150 to 299 | 17 (10) | 1 | -13.79% | 1 of 10 |
| 300 to 599 | 9 (4) | 4 | -1.57% | 2 of 4 |
| 600 to 1,199 | 10 (8) | 2 | -7.99% | 2 of 8 |
| 1,200 or more | 24 (7) | 14 | +3.97% | 3 of 7 |
| 300 or more, together | 43 (14) | 20 | +0.03% | 6 of 14 |
| for scale: a buy at any eligible cycle | 15,856 (41) | 33% | -3.87% | 9 of 41 |

- A signal on fewer than 300 trades in the hour is worse than no signal. Any cycle at all with 150 to 299 trades made -3.12% (2,942 cycles on 30 tokens). The cycles the entry rules picked in that band made -13.79%. The rules are not just failing to help there, they are picking the worst moments: the top of a short burst, as the reviews of 14 and 15 Nov described for WEALTH, FLOAT and Leonida one trade at a time.
- It holds on each day the band had signals: -10.5% (2 signals), -10.1% (6) and -17.0% (9) on 13, 14 and 15 Nov. The group at 300 or more made -15.2% (8), +6.8% (19), +1.1% (10) and -2.9% (6, 16 Nov): bad on 13 Nov as well, then about level.
- The real trades say the same. Bought on 150 to 299 trades: FLOAT (160), :3 (223), paws (174), FLOAT (184), Leonida (227): 0 wins of 5, all stops, -15.65% a trade. Bought on 300 or more: Leonida (726) and Rings (843) lost, WASTED (301 and 860) and BLOB (2,798) won: 3 of 5, +6.23%.
- Forward check. The 14 Nov 13:30 review looked at 200 and 250 and declined to pick "the number that makes the past look best". Since then, in the wide replay with the live rules: entries on 150 to 299 trades 0 wins of 8 on 8 tokens (-15.5%), entries on 300 or more 3 of 9 on 7 tokens (-3.5%). Three of the eight are real trades. On wins alone that split turns up by chance about one time in eight.
- The number does not matter much above 250. First signals at or over 200: -1.73%; 250: -0.40%; 300: +0.03%; 400: -0.08%; 500: -0.06%; 600: +0.45%. The gain is all in dropping 150 to 250; nothing above it is a peak picked off the record.
- The blocked entries do not come back a cycle later, which is how the last three entry ideas failed. `python3 -m bot.replay --wide --set universe.min_age_days=3 --set universe.max_age_days=30 --set entry.min_txns_h1=300` drops 12 entries: 11 losers and one winner (CJ, +16.7% on 247 trades, which it buys again 2 hours 20 minutes later on 671 trades for +15.9%). With no cooldown from the dropped losers it adds three: FLOAT +12.4%, CJ +15.9%, RAMBO -21.8%. Result: 18 closed on 14 tokens, 7 wins, -2.85% a trade, against 27 closed on 19 tokens, 6 wins, -7.42% with the floor at 150. On the bot's own universe: 6 closed on 5 tokens, 4 wins, +7.32%, against 10 closed, 3 wins, -4.66%.

**Changed: rulebook v5, entry section only. `entry.min_txns_h1` 150 to 300. A hypothesis, on hints.**

- Why it is more than the last three entry ideas. It was named before the data (13 Nov: "a higher `min_txns_h1`"), it has a mechanism (under 300 trades an hour is under 5 a minute, so the 1-hour change, the buy/sell ratio and the volume acceleration are each set by one burst, and passing all three at once mostly means the burst has just happened), it has held on trades made after it was first looked at, and it passes the test the last review set: the cycles it picks beat all cycles by more than a couple of points on the wide record (+0.03% against -3.87%) on more tokens than one (6 with a positive average: WASTED, BLOB, DIGS, :3, FLOAT, CJ).
- How weak it still is. The 14 Nov review wrote "do not raise it further on replay results alone". Five real trades in the band, none a winner, are the part that is not replay; five trades are a hint. Without WASTED and BLOB the group at 300 or more is 10 wins of 29, -3.35%: level with a buy at any moment. So the honest claim is the narrow one: signals under 300 trades have been reliably bad; signals over 300 have not been shown to be good. All of it is three days of one falling market.
- What it does not do. On the wide record the v5 rules still lose 2.85% a trade, about one round trip's costs. The +7.32% on the bot's universe is six trades on five tokens, read off the same record the number was chosen on. Do not expect it. This removes the worst group; it does not show an edge.
- What it costs. About half the trades: 5 of the 12 real trades had 300 or more, and the replay on the bot's universe goes from 10 trades to 6 in 2.5 days, about 2 a day. The proof gate (100 trades on one version) was already weeks away at 4 a day. Buying a band that has lost every time would fill the count faster and prove nothing.
- The blocked entries stay measurable: `python3 -m bot.replay --set entry.min_txns_h1=150` (add `--wide --set universe.min_age_days=3 --set universe.max_age_days=30`) shows what they would have done; the table has the trade count of each entry.
- Nothing else changed. Exit, universe, portfolio, safety, costs and discovery are v4's.

**Changed, in full.**

1. Rulebook v5: `entry.min_txns_h1` 150 to 300, `version`, `updated`, `notes`.
2. README: the strategy paragraph says 300 trades and v5.
3. Tests: the scripted token used as "a good token" traded 180 times an hour and would now be rejected, so it trades 600 times an hour (same 2:1 buy/sell ratio); the buy-pressure case likewise. One assertion added: a token exactly at the floor passes, one trade under it is rejected (both read the floor from the rulebook). 37 pass.
4. No change to `bot/`.

**First live cycles (06:50 and 06:55 UTC).** Pushed at 06:46 UTC and picked up by the 06:50 cycle. Both cycles ran v5 with no errors, `api_calls` 48, `universe_ok` 7, no signal (5 `h1_weak` each, 1 `buy_pressure`, 1 `h6_down`, 1 token in its cooldown), nothing open. v5 trades start from the 06:50 cycle.

**For the next review.**

- The discovery test is due at 14:00 UTC on 16 Nov. Walk `git log -- data/state/watchlist.json` as before (the checkout is shallow: `git fetch --depth=400 origin main` first, or the walk stops after 50 versions). If no token from `gecko:vol5` to `vol8` or `gecko:tx4` to `tx6` has passed the universe, put `top_volume_pages` back to 4 and `top_tx_pages` to 3. That is a discovery-section change and the one change for that review.
- v5: judge it on v5 trades. For the entry hint, count in the wide replay with `entry.min_txns_h1=150` the entries opened after 06:45 UTC on 16 Nov with 150 to 299 trades, and how they ended.
- Rings' shape, one trade: bought on the cycle a single +55% jump left the 1-hour window, after 50 minutes of no movement. If it repeats, the candidate is a rule on how the 1-hour change got into the band (it fell in from above the cap), which needs code. Test it against all cycles first.
- LP locked: Rings 26%, every other trade 40% or more. If the next losers also sit low, a floor in the safety section is a tightening and allowed.
- `no_data`: if `batch_miss` stays over 15 on most cycles, or a token with data history starts dropping out of the snapshots on those cycles, make the single lookups in `fetch_views` take tokens that have returned data before (`last_ok` set) ahead of tokens that never have. Plumbing, with a test.
- Trailing exits: compare the next one with its trail level (0 of 1 in the test so far).
- To redo the exit table, do not use `--baseline --set exit...` as it stands (it drops unfinished positions). Keep them, marked at the last price, and compare the same entries.

**Would prove this review wrong.**

- The entry change is wrong if the entries it blocks start winning as often as the ones it takes: of the next 10 entries on 150 to 299 trades in the wide replay with `entry.min_txns_h1=150` (opened after 06:45 UTC on 16 Nov), 3 or more winners. So far that band is 1 of 12 in the replay with trades and 0 of 5 for real. Then put it back to 150.
- It is also wrong if v5's first 10 closed trades have 2 winners or fewer: the same rules without it made 2 of 6, so that would be no improvement on the trades it keeps.
- It only removes losers, and the entry section still needs a different idea, if after a week the first signals at 300 or more, with WASTED and BLOB left out, are still level with a buy at any moment on the wide record (-3.35% against -3.87% today).
- It costs too much if v5 opens fewer than one trade a day over three days with cycles arriving. Then the universe has to grow before any entry rule can be judged, and discovery is the section to work on.
- Leaving the stop at 12% is wrong if the exit table, redone on a week of data, shows a 20% stop ahead by 2 points or more on both records and on the per-token average as well.
- The health verdict is wrong if the gap between cycles grows past 15 minutes, or if a token that has returned data before is missing from the snapshots on cycles where `batch_miss` is over 15.

### v4, 2026-11-15 22:30 UTC review: no rule change (review tool: the entry rules measured against a buy at any moment)

**Health.** 688 cycles since launch, 110 since the last review. Last 6 hours: 74 cycles, median gap 5.0 minutes, longest 5.2. The newest cycle was 1.8 minutes old when the review started, so no `.kick`. Two extra cycles (16:41 and 21:17, each 2 to 3 minutes after the one before): both triggers fired, the concurrency group ran them in turn. No error in any of the 107 cycles on v4; the one error since the last review was at 13:40, before v4 was live (GeckoTerminal 429 on trending page 2). No `gecko ... p5` to `p8` or `p4` to `p6` line: the deeper pages have answered on every turn for 8.7 hours. `batch_miss` 10 to 16 per cycle (median 13) out of about 250 tokens; `no_data` 8 to 12 (median 10, the level the 14 Nov review said to watch; not growing). `allowed_pool_used` 3 to 5, `api_calls` 41 to 47, watchlist 168 to 196 (cap 300), no `pool lookup` error. RugCheck ran once (Leonida, 14:55) and parsed: `score_normalised` 1, no risks, LP locked 87.3%. No `safety:*`, `skip:*` or `suspect_price` rows. No bug found in the trading path, so no change to it.

**Strategy: v4 has 1 closed trade, a loss. One trade is not a hint.** Equity 4.5583 SOL (-8.83%, was 4.6271), nothing open. v3 and v4 have the same trading rules; together 4 closed, 1 win, -7.16% per trade. All versions: 10 closed, 2 wins (both WASTED), -9.03% per trade. SOL went from $73.0 to $72.2.

| # | Token | Opened (UTC) | Trades in the hour before | 1-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|
| 10 | Leonida | 15 Nov 14:55 | 227 | +3.9% | +1.6% | stop, price at -12.6% | -14.88% |

- Leonida's entry repeats its own entry of 13 Nov. The price rose 7.7% in the 15 minutes to 14:45, fell 8% in the next five (reported 5-minute change -9.9%), bounced 1.5% and was bought at 14:55. The 1-hour change still read +3.9% because the hour held the rise, and the trade count passed 150 only because of the burst (108 at 14:25, 227 at 14:55). At 14:40 and 14:45, 7% higher, it was rejected: 117 and 129 trades in the hour, and more sells than buys.
- The stop. The reading before it was -10.7%; the stop cycle read -12.6% on $31 of volume in the five minutes; the next read -9.4%. The last two points were the pool's price hopping between buy and sell side, as with paws. The token was back at +0.5% two hours later and at -14.2% at 22:30, so nothing says the stop was wrong. Across all 8 stops the price at the stop cycle averages -14.6%, 2.6 points past the level, with every cycle on time.
- Left on the table: nothing. Three of the four v3 and v4 trades never got above +2%.

**What the last review asked, answered.**

- Not relaxing a threshold was right. Its test: wrong if Leonida at 12:05 (bought with `h6_change_min_pct` -5) and paws at 13:20 (bought with fewer trades) both end as winners. Leonida ended at the time stop, -0.2%; paws at the stop, -15.5%.
- The 150-trade filter. On the bot's universe `python3 -m bot.replay --set entry.min_txns_h1=50` now differs from the live rules by two trades, both stops (STANK -18.1%, paws -15.5%). In the wide replay (ages 3 to 30 days, `min_txns_h1=50`) entries under 150 trades are 2 wins of 15 (-11.1% per trade) against 5 of 18 (-5.9%) at 150 or more; it was 2 of 10 against 5 of 15. The five new entries under 150 all lost (updog, paws, WEALTH, GTA6, TrumpWars). Evidence for the filter is a little better than at 13:30. v3's own test (2 winners or fewer in the first 10 closed trades) stands at 1 of 4.
- The 1-hour change. Wide replay with the live rules: 1 win of 11 at or under +7.8%, 4 of 12 above (was 1 of 9 and 4 of 9). The five trades closed since 13:30 all lost, two under the line and three over it, so the new trades say nothing for it.
- "The 1-hour change must have been above the floor on the previous cycle too" (the candidate named at 13:30): tested, does not help. Bot universe -6.70% per trade against -6.63%; wide 21 closed, 4 wins, -8.33% against 23 closed, 5 wins, -7.63%. It delays the losers by one cycle and costs a winner: mihao (+13.9%) was bought on its first cycle over the floor and never passed two cycles running.
- "Do not buy a token that has just fallen from a spike" (Leonida twice, and AMD and WEALTH in the replay: 0 wins of 4). Tested as "price not more than 5% under its highest reading of the last 15 minutes": the four entries are blocked and three come back 10 to 15 minutes later for much the same result (Leonida -14.6% against -14.8%, AMD -17.3% against -15.2%, WEALTH -0.7% against -4.6%). Wide 22 closed, 5 wins, -7.13% against -7.63%. And over every recorded cycle, a token 5% or more under its 15-minute high did better afterwards, not worse (-2.3% against -3.3% for all cycles). The story fits four trades and not the record. Dropped.

**New measurement: the entry rules against a buy at any moment.** Each review so far has judged the entry rules on 4 to 23 replayed trades, and every fix tried on those has failed the same way. So this review asked a wider question of the same snapshots: open a position at every cycle a token was inside the universe, run each through the live exits, costs and bad-print guard, and compare the cycles the entry rules pass with all the rest. It is now `python3 -m bot.replay --baseline`.

| Positions opened at | Bot's universe: cycles (tokens) | Win rate | Mean | Wide, ages 3 to 30 days: cycles (tokens) | Win rate | Mean |
|---|---|---|---|---|---|---|
| every cycle a token was eligible | 4,743 (16) | 29% | -4.32% | 13,541 (35) | 34% | -3.27% |
| cycles the entry rules passed | 67 (5) | 49% | -1.15% | 131 (17) | 37% | -3.03% |
| the first passing cycle of each run | 22 (5) | 45% | -1.88% | 51 (17) | 37% | -3.18% |

- On the wide record the entry rules pick moments no better than no rule at all: -3.03% against -3.27%, and the same win rate within 3 points. On the bot's own universe they look 3 points better, but 44 of the 67 passing cycles are WASTED (30 wins, +4.8%); the other four tokens are 23 cycles with 3 wins. That is one token, not a rule.
- A buy at any moment lost 3.3% a trade. A round trip costs about 3%. So over a holding period these tokens went nowhere on average, and whatever the entry rules add has to cover the costs before it shows. Nothing they add is visible yet.
- No single entry feature shifts the outcome across tokens. With a scratch version of the same measurement (flat 3.2% cost, tokens 3 to 30 days old) I cut all cycles by 1-hour, 6-hour, 24-hour and 5-minute change, trades in the hour, buy/sell ratio, volume acceleration, liquidity, 24-hour volume, age, DEX, SOL's own 1-hour and 6-hour change and the share of tokens rising. Every band has a negative mean except two: a 24-hour change over +100% (+1.5%, 13 tokens) and 24-hour volume under $100k (+1% to +3%, 3 and 7 tokens, under the universe's floor). A dozen cuts on one record will always show a band or two like that; they are not findings.
- The day decides more than any threshold. Wide replay with the live rules: 13 Nov 0 wins of 6, 14 Nov 5 of 8 (+4.7% per trade), 15 Nov 0 of 9 (-14.6%). The baseline for all cycles on those days was -0.0%, -3.4% and -4.7%, so 14 Nov was not a better day for the universe as a whole; the rules found WASTED, :3, CJ and mihao on that day and nothing on the other two. Three days cannot say whether that is skill on some days or luck on one.
- What this means for the reviews. Two and a half days of one market cannot tell these entry rules from chance, and no threshold in them is the obvious culprit. The honest reading of -9.03% over 10 real trades is "no edge shown", not "nearly there". Three entry fixes have now been tested in the replay (a higher 1-hour floor on 14 Nov, the two-cycle floor and the fall from a spike today) and each time the losers it blocked came back a cycle or two later. Use the baseline as the yardstick from here: a new entry idea is worth a rule only if the cycles it picks beat all cycles across many tokens, not if it removes the last three losers.

**Discovery (v4's change): the test is due at 14:00 UTC on 16 Nov. So far the deeper pages have found nothing the bot can trade.** Read from the 108 versions of `data/state/watchlist.json` in git since 13:45, so tokens that were found and dropped are counted.

- Pages 5 to 8 of the volume list and 4 to 6 of the trade-count list found 23 tokens in 8.7 hours. 17 were under one day old when found, 14 of them under two hours old with $4M to $13M of reported 24-hour volume in a pool of $40k to $160k; those 14 left the snapshots within two hours, 10 of them within 30 minutes. The volume pages keep returning one name on different addresses (on the watchlist at 22:30: BUTTHOLE four times, rockstar four, bill three, Emojis twice). That is launch-day churn, not the 3-to-30-day tokens the change was after. One was 1.4 days old (XTO, next point) and 5 never returned data.
- One is still in the snapshots: XTO (`gecko:tx4`, 1.7 days old, $1.2M liquidity). It will not become tradable when it turns 3 days old: its market cap is $298M against a $50M ceiling.
- None of the 23 has passed the universe filters, and none of those still alive can. The reason is visible now: a list ranked by 24-hour volume is filled by same-day launches with inflated volume and by old, large pools, and tokens that trade $100k to $2M a day rank far below page 8.
- The one new token in the band since 13:30 came from a shallow page: Rings (`gecko:trend2`, found 18:20, 5 days old, Meteora, $275k volume). Its liquidity sits at $48k to $50k, so it passed the universe on two cycles (22:10 and 22:15). One token is a hint that the trending list is where tokens of this age show up.
- `universe_ok` is 7 or 8 per cycle (was 8 or 9): GLITCH turned 30 days old at 15:40 and WEALTH's 24-hour volume fell under $100k at 11:20. The universe is shrinking while discovery adds nothing.
- Cost so far: none. `api_calls` 41 to 47, watchlist under 200 (median 189, was 179), no 429 since the change. `u:too_young` is 27 a cycle, as before (29).
- Not changed today. The test has 15 hours to run and was set in advance; a second discovery change before it is due would leave neither readable. The interim reading is that it will fail.

**No signal for 7.6 hours (last: Leonida 14:55). The 12-hour rule is not met.** Funnel since 13:30, 804 universe-token checks: `h1_weak` 502 (62%), `h6_down` 102, a token in its cooldown 85, `txns_h1` 39, `buy_pressure` 34, `h24_dumped` 15, the held token 11, `volume_accel` 10, `m5_dropping` 3, `h1_overheated` 2, signal 1. If the next review finds the rule met, this is what each modest relaxation would have added on the bot's universe since 13:30:

| Change tried | Trades it adds since 13:30 UTC |
|---|---|
| `entry.h1_change_min_pct` 2 to 1, or to 0 | none |
| `entry.h6_change_min_pct` 0 to -5 | WASTED 20:30, open at +4.2% |
| `entry.min_buy_sell_ratio_h1` 1.2 to 1.1 | none |
| `entry.min_volume_accel` 1.2 to 1.0 | FLOAT 17:45, open at -6.0% |
| `entry.h1_change_max_pct` 25 to 35, `entry.min_txns_h1` 150 to 100 | none |
| `portfolio.token_cooldown_hours` 12 to 6 | none |
| `universe.min_volume_h24_usd` 100k to 50k | WEALTH 15:05, time stop, -4.6% |
| `universe.min_liquidity_usd` 50k to 40k, `max_age_days` 30 to 35, `min_age_days` 3 to 2, `min_liq_to_mcap` 0.03 to 0.02 | none |

**Changed.**

1. Rulebook: nothing. v4 stays. v4 has one trade, the zero-signal rule is not met, the discovery test is not due, and no entry or exit variant holds up on the record (above).
2. Review tool, no rule in it and nothing in the bot's trading path: `python3 -m bot.replay --baseline` (`baseline` and `baseline_report` in `bot/replay.py`). To share one set of exit code, the replay's own loop was split into small helpers (`_eligible`, `_signal`, `_open`, `_manage`, `_record`); its output is unchanged, checked line for line on four replays of the live record before and after.
3. Tests: 1 added (a scripted token: one position per eligible cycle, the passing cycles and the first of them marked, the first one equal to the replay's own trade, open positions and a too-young token left out). 37 pass. The new test fails on the old code.

**For the next review.**

- After 14:00 UTC on 16 Nov, read the discovery test. Count tokens whose `source` is `gecko:vol5` to `vol8` or `gecko:tx4` to `tx6` that passed the universe (walk `git log -- data/state/watchlist.json` as this review did, because the watchlist only shows tokens still on it). If it is still none, put `top_volume_pages` back to 4 and `top_tx_pages` to 3. What to try instead is open. The one lead is the trending list (Rings); `trending_pages` is 2. It cannot be tested from the review session, so if it is tried, try it the same way: labelled pages, a dated test.
- Run `python3 -m bot.replay --baseline` and the same with `--wide --set universe.min_age_days=3 --set universe.max_age_days=30`. The entry rules have shown something when the passing cycles beat all cycles by more than a couple of points on the wide record, across more tokens than one.
- If 12 hours pass with no signal (02:55 UTC on 16 Nov), a relaxation is allowed, not required. The table above says none would have bought a closed winner. `h6_change_min_pct` -5 is the only one with an open trade in profit (WASTED 20:30); record where it ends.
- v3's test for the 150-trade filter: 1 winner in 4 closed so far, 10 needed.
- Trailing exits: none since 14 Nov. Compare each new one with its trail level, as the 14 Nov 23:35 review set out.

**Would prove this review wrong.**

- Leaving the rules alone is wrong if the next 10 closed trades on these rules include 4 or more winners: then the rules were better than this record shows and the baseline reading was too gloomy. It is also wrong the other way if `--baseline` on a week of data still shows passing cycles no better than all cycles and the rules are still unchanged: at that point the entry section needs a different idea, not another threshold.
- The baseline is misleading if its first row moves by several points when the record doubles (then two days were too few to be a yardstick), or if the replay with the live rules stops reproducing the bot's real trades (then the shared exit code has drifted from the bot's).
- Waiting on discovery is wrong if a deeper-page token passes the universe before 14:00 UTC on 16 Nov: then the interim reading above was wrong and the pages should stay.
- The health verdict is wrong if the gap between cycles grows past 15 minutes or a `gecko` error on one of the deeper pages starts repeating.

### v4, 2026-11-15 13:30 UTC review: GeckoTerminal's most-traded lists read twice as deep; no trading rule changed

**Health.** 578 cycles since launch, 170 since the last review. Last 6 hours: 73 cycles, median gap 5.0 minutes, longest 5.2. The newest cycle was 2.6 minutes old when the review started, so no `.kick`. Two extra cycles (02:40 and 09:55, each 1 to 2 minutes after the one before): both triggers fired, the concurrency group ran them in turn. Errors in 3 of the 170 runs (02:50, 03:35 and 08:15 UTC), each one GeckoTerminal 429 on a single page; the page was fetched on the next cycle each time. `batch_miss` 8 to 15 per cycle (median 11) out of about 238 tokens; `no_data` 8 to 12 (median 9, was 7 to 9). It touched 12 between 00:00 and 06:00 UTC and is back at 9: over the 10 the last review named, not growing. `allowed_pool_used` 3 to 5, `api_calls` 40 to 47, no `pool lookup` error. RugCheck ran once (FLOAT, 23:50) and parsed: `score_normalised` 1, no risks, LP locked 73.7%. No `safety:*`, `skip:*` or `suspect_price` rows. No bug found in the trading path.

**Strategy: v3 closed 3 trades, 1 win. Three trades are a hint at most.** Equity 4.6271 SOL (-7.46%, was 4.7534), nothing open. v3: -4.58% per trade, -0.0683 SOL. All versions: 9 closed, 2 wins (both WASTED), -8.38% per trade. SOL rose from $69.4 to $73.0 (+5%) since the last review.

| # | Token | Opened (UTC) | Trades in the hour before | 1-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|
| 7 | WASTED | 14 Nov 20:45 | 860 | +23.3% | +68.1% | half sold at +23.7%, rest trailed out at +18.8% | +21.00% |
| 8 | paws | 14 Nov 22:05 | 174 | +3.3% | 0.0% | stop, price at -12.6% | -14.22% |
| 9 | FLOAT | 14 Nov 23:50 | 184 | +11.2% | +0.9% | stop, price at -20.1% | -20.52% |

- Stops. FLOAT read -6.5% at 01:40 and -20.1% at 01:45: a 14.5% fall inside one cycle on $29k of volume (2.7 times what a $286k pool needs to move that far, so the traded-volume check rightly let it through; the next readings were -19.5%, -15.5%, -16.1%). That stop filled 8 points past its level with every cycle on time. paws drifted down for three hours and was stopped at -12.6% on a reading with $9 of volume in the five minutes; the reading before was -9.9% and the one after -10.9%, so the last 2 points were the pool's price hopping between buy and sell side, on a trade that was already 10% down. Across all 7 stops the price at the stop cycle averaged -14.9%, 2.9 points past the level. It is the 5-minute sampling, not the trigger.
- FLOAT's entry (hint, n=1, the same shape as WEALTH and Leonida on 13 Nov). The price rose 10.9% in the 15 minutes before the buy (0.002741 at 23:35, 0.003041 at 23:50), the 1-hour change went from +1.4% to +11.2% and the hourly trade count from 62 to 184 in those three cycles. The bot bought the top of that burst; the trade never got above +0.9%. The 150-trade filter was passed only because of the burst itself.
- The 1-hour-change test from the last review is not met: v3's losers entered at +3.3% and +11.2%, so they do not both sit under +8%. In the wide replay with v3's rules the split is now 1 win of 9 at or under +7.8% against 4 of 9 above it (was 0 of 6 against 4 of 5): mihao entered at +2.9% and made +13.9%, FLOAT (+11.2%) and RAMBO (+18.9%) lost. The hint is weaker.
- The 150-trade filter. On the bot's own universe `python3 -m bot.replay --set entry.min_txns_h1=50` took the same trades as v3 until 13:20 today, when it bought paws (101 trades in the hour; open, -4.75% after ten minutes, most of it costs). That is the first trade the filter has blocked; no result yet. In the wide replay (ages 3 to 30 days, `min_txns_h1=50`) entries under 150 trades are now 2 wins of 10 (-9.4% per trade) against 5 of 15 (-4.2%) at 150 or more; it was 0 of 7 against 4 of 10. The two new winners are WANTED (55 trades, +25.6%) and TrumpWars (62 trades, +2.1%), both in pools of about $31k that the universe rejects. The group with no winner in it now has two, so the evidence for the filter is thinner than when it was made. Not changed today: one section per review, and v3's own test (2 winners or fewer in the first 10 closed trades) is 1 of 3 so far.
- Trailing exits: none since the last review, so nothing new. In the wide replay a 5% trail is still better or level on each of the four trailing exits.
- Meteora, on a full day of rows with `dex` (290 snapshots, 13:50 on 14 Nov to 13:30 on 15 Nov). Quiet-cycle price step, 90th percentile: Meteora 3.1% (282 cycles, 3 pools: STANK 4.1%, Macca 2.3%, DacityCoin 2.2%); PumpSwap 2.6% (2,214 cycles, 27 pools; SOL pools 2.1% to 3.1%); Raydium 0.9% (5 pools; FLOAT 0.8%); MetaDAO 1.1% (1 pool). STANK stands apart, Meteora as a group does not. No case for excluding or repricing Meteora. This closes the question unless a Meteora trade shows otherwise.

**No signal for 13.7 hours, so the zero-signal rule is met. Thresholds are not the reason.** The last signal was FLOAT at 23:50 UTC on 14 Nov; 166 cycles since.

- Funnel since then, 1,389 universe-token checks: `h1_weak` 607 (44%), a token in its cooldown 436 (31%), `h6_down` 159 (11%), `txns_h1` 84 (6%), the held token 38, `buy_pressure` 18, `h1_overheated` 17, `h24_dumped` 15, `volume_accel` 10, `m5_dropping` 5. The universe was 8 to 10 tokens a cycle (median 8), ten different tokens in all. Their median 1-hour change was -0.2% and 35% of readings were at +2% or better, a little stronger than yesterday.
- Gaps this long are normal for a universe this small: the three longest gaps between signals so far are 10.7, 12.8 and now 13.7 hours.
- The cooldown did not block anything: none of the 436 checks on a token in its cooldown (FLOAT, paws, WASTED, STANK) would have passed the entry rules.
- No modest relaxation would have bought a winner. Replayed on the recorded snapshots since 23:55 UTC:

| Change tried | Trades it adds since the last signal |
|---|---|
| `entry.h1_change_min_pct` 2 to 1, or to 0 | none |
| `entry.h6_change_min_pct` 0 to -5 | Max 10:15, stop, -15.1%; Leonida 12:05, open at -0.2% |
| `entry.min_buy_sell_ratio_h1` 1.2 to 1.1 | none (to 1.0: Max 11:00, stop, -18.3%) |
| `entry.min_volume_accel` 1.2 to 1.0 | none |
| `entry.h1_change_max_pct` 25 to 35 | STANK 03:25, stop, -13.6% |
| `entry.min_txns_h1` 150 to 100 or 50 | paws 13:20, open at -4.8% |
| `portfolio.token_cooldown_hours` 12 to 6 | none |
| `universe.min_liquidity_usd` 50k to 40k or 30k, `min_volume_h24_usd` 100k to 50k, `max_age_days` 30 to 35, `min_age_days` 3 to 2 | none |
| `universe.min_liq_to_mcap` 0.03 to 0.02 | RAMBO 04:10, stop, -17.5% |
| `universe.min_age_days` 3 to 1 (not modest) | WOHAIHAO 02:38, one day old, +12.8% |

  Every relaxation the rule allows adds nothing, an open trade near zero, or a stop-loss. Relaxing one anyway would be buying trades the record says lose.

**The bottleneck is what discovery finds.** This has been said in every review since 13 Nov; this time there are numbers for it.

- Since 18:40 UTC on 13 Nov, 15 tokens have ever passed the universe filters. 12 of them were on the watchlist by 14:48 UTC on 13 Nov, the bot's first hour. In the 47 hours since, discovery has added three that became eligible: GLITCH (DexScreener boosts, 14 Nov 01:00), GTA$ (DexScreener profiles, 14 Nov 11:10) and POLYMARKET (GeckoTerminal, 15 Nov 07:35, eligible for under an hour before it turned 30 days old).
- GeckoTerminal found 8 of the 15 on its first full pass and one since. Its 9 pages (the top 180 pools by trending, volume and trade count) keep returning the same pools: the 75 or so "new" GeckoTerminal tokens every 6 hours in the funnel are the same too-old tokens dropped and found again.
- Its current depth misses tokens the bot can trade. WASTED (both of the bot's winning trades) and GLITCH were in the tradable band when a DexScreener boost feed found them, and GeckoTerminal had not shown either. WASTED (14 days old, $110k liquidity, $147k volume) was not among the pools the 9 GeckoTerminal calls of the 13:52 run on 13 Nov returned and came in from the boost feed at 14:18. GLITCH (28 days old, $113k liquidity, $160k volume) first appears in the record at 01:00 on 14 Nov, from the boost feed, after 11 hours of page rotation. The source label only names the first feed to find a token, so this shows what GeckoTerminal missed before then, not what it lists now. Half of today's universe (WASTED, GLITCH, Leonida, Max) is there only because a team paid DexScreener for visibility.
- Why deeper pages are the likely place. The universe needs $100k of 24-hour volume; the bot's tokens trade $150k to $2M a day. Page 4 of the volume list ends at rank 80 on a chain with thousands of pools, so the list stops well above where most 3-to-30-day tokens of that size rank.
- The bot keeps trading the same few tokens: 9 trades on 7 tokens, FLOAT and WASTED twice each. Even a good result on so few tokens would say little.

**Changed: rulebook v4, discovery section only. `geckoterminal.top_volume_pages` 4 to 8 and `top_tx_pages` 3 to 6. A hypothesis; it could not be tested from here.**

- What it does. The rotation is now 16 pages (2 trending, 8 by volume, 6 by trade count) instead of 9. Still 2 GeckoTerminal calls per cycle, so the rate-limit exposure is the same; a full pass takes 40 minutes instead of 22.5. A token stays on the watchlist once found, so the slower pass costs little. Pools are still pre-filtered to $30k reserve and 35 days.
- What it does not do. No entry, exit, universe, portfolio, safety or costs number changed. A token from a deeper page passes the same universe filters and the same RugCheck screen as any other. v3 and v4 trades are made by identical trading rules on a different pool of tokens, so the tests set for the 150-trade filter, the trail and the 1-hour change carry on across both; the version tables keep them apart so the effect of the wider net can be seen.
- Not verified. GeckoTerminal is not reachable from the review session. CoinGecko's documentation for the paid version of the same endpoint (read today) says 20 pools per page and that paging past page 10 needs a higher plan; it says nothing about what the free API serves on pages 5 to 8. If a page is refused the bot now copes (next point).
- Why not more. Trending pages are unchanged and both lists stop short of page 10. If pages 5 to 8 find tradable tokens the next review can go deeper; if they find none, more pages are not the answer.

**Plumbing (no rule in it).**

1. A GeckoTerminal page that fails two cycles running is skipped until its next turn (`GECKO_SKIP_AFTER` in `bot/run.py`). Before, a failing page was retried every cycle for ever and the pages behind it were never fetched. That was harmless with pages that always answer after a 429, and would have stopped all GeckoTerminal discovery if one of the new pages is refused. One retry is kept, because a 429 usually clears by the next cycle.
2. A token found by GeckoTerminal now records the list and page that found it: `source` in `data/state/watchlist.json` reads `gecko:trend2`, `gecko:vol6` or `gecko:tx5` (tokens already on the watchlist keep `gecko`). This is what makes the change testable.
3. Tests: 1 added (a page that keeps failing is skipped, the rotation carries on, the skipped page is tried again next time round, a token from the deepest page is labelled with it), 1 adjusted (the rotation test no longer assumes 9 pages). 36 pass. The new test fails on the old code.

**First live cycles (13:50 to 14:05 UTC).** Pushed at 13:45 UTC and picked up by the 13:50 cycle. Four cycles on v4, no errors, 2 GeckoTerminal calls each, `api_calls` 41, `universe_ok` 8, no signal. The rotation went through volume pages 2 to 8 and trade-count page 1: pages 5 to 8 of the volume list all answered on the free API. They added four tokens the bot had not seen: Socks (`gecko:vol5`, $149k liquidity, one hour old, so `too_young`) and three that DexScreener returned no data for. Nothing tradable from them yet. Trade-count pages 4 to 6 come round at 14:10 to 14:20 UTC and were not seen by this review.

**For the next review.**

- Check the deeper pages first. Errors: any `gecko ... p5` to `p8` (volume) or `p4` to `p6` (trade count) line repeating in `data/runs`. Yield: in `data/state/watchlist.json`, count tokens whose `source` is `gecko:vol5` to `gecko:vol8` or `gecko:tx4` to `gecko:tx6`, and how many of those pass the universe filters in the latest snapshot. Also `universe_ok` per cycle (8 to 9 now), `watchlist` (176 now, cap 300) and `api_calls` (42 now).
- v3 is closed at 3 trades (1 win). Judge v4 on v4 trades; for the entry and exit hints, v3 and v4 trades may be read together because those sections are identical.
- The 150-trade filter: record where the replay's paws entry (13:20 on 15 Nov, 101 trades) ends. If the entries it blocks keep winning as often as the ones taken, put it back to 50 as the 14 Nov review said.
- Entry hint to test in the replay before choosing any number: a buy made at the top of a 15-minute burst (WEALTH, Leonida, FLOAT twice). One candidate with a mechanism: the 1-hour change must have been above the floor on the previous cycle too.
- Trailing exits: unchanged from the last review. Compare each new one with its trail level.

**Would prove this review wrong.**

- The discovery change is wrong if, by 14:00 UTC on 16 Nov, no token found on a deeper page (`gecko:vol5` to `vol8`, `gecko:tx4` to `tx6`) has passed the universe filters: then the deeper pages hold nothing the bot can trade. Put the pages back to 4 and 3 and look for another source instead. It is half wrong if they add tokens and `universe_ok` still sits at 8 to 9 after two days.
- It is also wrong if the new pages are refused (the same `gecko ... p5`-style error twice in a row, every 40 minutes): cut the page counts to the pages that answer.
- It costs too much if `api_calls` passes about 60, the watchlist reaches its 300 cap, or GeckoTerminal 429s rise above a handful a day.
- Not relaxing a threshold is wrong if the entries a modest relaxation would have added (Leonida 12:05 with `h6_change_min_pct` -5, paws 13:20 with fewer trades) both end as winners and the next 12 hours again bring no signal.

### v3, 2026-11-14 23:35 UTC review: no rule change, no code change

**Health.** 408 cycles since launch, 61 since the last review. Last 6 hours: 74 cycles, median gap 5.0 minutes, longest 5.2. The newest cycle was 1.9 minutes old when the review started, so no `.kick`. Two extra cycles (19:25, 31 seconds after the one before, and 23:12, 2 minutes after): both triggers fired, the concurrency group ran them in turn, nothing was lost. No errors in any run since 07:05 UTC. `batch_miss` 12 to 15 per cycle out of about 240 tokens (6%, was 8 to 12): 7 to 9 are `no_data` as before, the rest are recovered by the single lookup. `allowed_pool_used` 3 to 5, `api_calls` 43 to 47, no `pool lookup` error. RugCheck ran for both signals (WASTED 20:45, paws 22:05) and both answers parsed: `score_normalised` 1, no risks, LP locked 85.8% and 60.9%. No `safety:*`, `skip:*` or `suspect_price` rows. No bug found, so no code change.

The traded-volume check from the last review met its first real case and made the right call. WASTED read -24.3% in one cycle at 22:25 while held. A move that size in a $235k pool needs about $15k of volume; $255k had traded (16.7 times the need), so the reading was acted on in the same cycle. The next two readings stayed there (0.00539, 0.00502), so the fall was real.

**Strategy: v3 has 1 closed trade and 1 open. One trade is not a hint, let alone a finding.** Equity 4.7534 SOL (-4.93%, was 4.6954). SOL fell from $72.6 to $69.5 since the last review (-4.4%) and is 14% under its price at launch.

| # | Token | Opened (UTC, 14 Nov) | Trades in the hour before | 1-hour change at entry | Best while held | Exit | Net |
|---|---|---|---|---|---|---|---|
| 7 | WASTED | 20:45 | 860 | +23.3% | +68.1% | half sold at +23.7%, rest trailed out at +18.8% | +21.00% |
| 8 | paws | 22:05 | 174 | +3.3% | 0.0% | open, -7.6% (lowest -7.8%, stop at -12%) | |

- Signals. Two in the five hours since the last review, so the 12-hour zero-signal rule is not met. The last review's test (fewer than 2 v3 trades by the end of 15 Nov) is already passed: 2 opened in v3's first 10 hours.
- Funnel since 18:40 UTC, 492 universe-token checks: `h1_weak` 263 (53%), `h6_down` 84 (17%), a token in its cooldown 76 (15%), the held token 37, `volume_accel` 10, `txns_h1` 9, `h1_overheated` 6, `buy_pressure` 4, `m5_dropping` 1, signal 2. The universe was 7 to 10 tokens a cycle (median 8), ten different tokens in all. Their median 1-hour change was -1.75% and 32% of readings were at +2% or better. Same picture as before: a falling market and a small universe.
- What the v3 filter cost. `txns_h1` blocked 9 checks, all GLITCH. `python3 -m bot.replay --set entry.min_txns_h1=50` takes the same trades as v3 since 13:50, so the filter has not yet blocked a trade the bot would otherwise have made. In the wide replay (`--wide`, ages 3 to 30 days, `min_txns_h1=50`) entries under 150 trades are still 0 wins of 7 closed, with one new entry open (TrumpWars 18:35, 62 trades, +5.6%, a $32k pool outside the universe); entries at 150 or more are 4 of 10 (was 3 of 9, the new one is the real WASTED trade). Nothing against the hypothesis, nothing new for it.
- Exits: the trailing stop filled far under its level. WASTED peaked at +68.1% at 22:10, which put the trailing stop at +51.2%. At 22:20 it read +56.9%, at 22:25 +18.8%: the fall came inside one 5-minute cycle, on $236k of volume. The second half was sold 32 points under the trail level, about 16 points off the trade. The first trailing exit (trade 5) filled 4.5 points under its level (+25.2% against +29.7%). Two cases, one token. In the wide replay a 5% trail is better on three of the four trailing exits and level on the fourth (WASTED +40.6% against +21.1%, WASTED +25.7% against +20.8%, CJ +18.7% against +16.7%, :3 +13.8% against +13.9%) and lifts the 11 closed trades from -2.16% to +0.23% per trade. Four exits on three tokens, and 5 is a number tried because 10 just failed. A hint for the exit section, not acted on.
- 1-hour change at entry (the hint from 13:30, updated). Wide replay with v3's rules: entries at or under +7.8% are 0 wins of 6, above it 4 of 5. With `min_txns_h1=50` it is 0 of 8 against 4 of 9. paws (+3.3%) is underwater. But two things keep this a hint. It is the best of six splits tried on the same trades. And the obvious fix does not work: with `entry.h1_change_min_pct=5` the replay still takes FLOAT and paws, one cycle later (at +5.5% and +5.7%), for about the same loss, and of the six losers it removes one (DacityCoin). Only a floor near +8% removes the group, and that number is read off the losers.
- Cooldown: nothing new. WASTED was bought again 14.7 hours after its last exit and won. The replay without a cooldown adds the same four trades as before (FLOAT, WASTED three times; 3 wins), all from one night.
- Meteora, measured again on 120 snapshots (13:50 to 23:30 UTC, still short of a full day). Quiet-cycle price step, 90th percentile: Meteora 2.6% (119 cycles, 5 pools: CHOO 3.6%, STANK 2.9%, Dacity 2.4%, DacityCoin 2.0%, Macca 2.0%); PumpSwap 2.8% (717 cycles, 19 pools; the 11 quoted in SOL read 1.4% to 3.1%, the highest figures, up to 8.6%, are pools quoted in another token whose own price moves are in the number); Raydium 1.1% (96 cycles, 3 pools); MetaDAO 1.3% (1 pool). Meteora still does not stand apart. Worth noting for the entry rules: on PumpSwap and Meteora a quiet pool's price steps by 2 to 3% with almost no trading, which is the size of the +2% 1-hour floor.

**Changed.** Nothing. Rulebook v3 stays; no code change; 35 tests pass. v3 is 10 hours old with one closed trade. Both hints above (a tighter trail, a higher 1-hour floor) come from the replay, each rests on a handful of trades in two or three tokens, and changing either now would end v3 before its own change (150 trades in the hour) has been tested at all.

**For the next review.**

- Judge v3 on v3 trades. It needs about 10 closed before the test set on 14 Nov 13:30 can be read (2 winners or fewer in the first 10 means the 150-trade filter did not help).
- Trailing exits: for each new one, compare the fill with the trail level (peak less 10%). If the next two also fill more than 5 points under it, the exit section is the candidate (a 5% trail, or selling more than half at the first target). Check with `python3 -m bot.replay --wide --set universe.min_age_days=3 --set universe.max_age_days=30 --set exit.trailing_stop_pct=5` that the tighter trail is still no worse on each trailing exit, not only on average.
- 1-hour change: record where paws ends. If v3's closed losers sit under +8% at entry and its winners above, the entry section is the candidate, but a floor of 5 is not the fix (see above). Look for a rule with a mechanism, for example a 1-hour change that must hold for two cycles running, and test it in the replay before choosing a number.
- Only one of those two sections may change in one review. Take the one v3's own trades point to.
- Still open: the cooldown hint, the universe size (discovery is the lever and cannot be tested from the repo's data), and a full-day Meteora measurement (from 13:50 UTC on 15 Nov).
- `batch_miss` crept from 8 to 12 up to 12 to 15 per cycle. Harmless at this level; look again if it passes 20 or if `no_data` grows past 10.

**Would prove this review wrong.**

- Leaving the exit alone is wrong if v3's next two trailing exits again give back more than 5 points between the trail level and the fill: then the 10% trail is too wide for 5-minute sampling and waiting cost real paper money.
- Leaving the entry alone is wrong if v3 closes three or more losers that all had a 1-hour change under +8% at entry while every v3 winner was above it.
- The health verdict is wrong if a `suspect_price` event appears for a move that the next cycle confirms, or if the gap between cycles grows past 15 minutes: stops depend on the 5-minute trigger.

### v3, 2026-11-14 18:40 UTC review: no rule change (plumbing: a second kind of bad price print)

**Health.** 347 cycles since launch, 57 since the last review. Last 6 hours: 72 cycles, median gap 5.0 minutes, longest 5.2. The newest cycle was 2 minutes old when the review started, so no `.kick`. No errors in any run since 07:05 UTC. `batch_miss` 8 to 12 per cycle out of about 245 tokens (4%), 6 to 9 of them `no_data`. `allowed_pool_used` 4 or 5, `api_calls` 39 to 43, no `pool lookup` error. RugCheck was not called (no signal); the saved sample and the six cached answers still parse (`score_normalised` 1, no risks, `lpLockedPct` read). No `safety:*`, `skip:*` or `suspect_price` rows. Two cycles ran 31 seconds apart at 14:30 (both triggers fired); the workflow's concurrency group ran them one after the other and nothing was lost.

**Strategy: v3 has no trades, so there is nothing to judge.** 59 cycles on v3 (13:50 to 18:35 UTC), no signal, nothing open, equity unchanged at 4.6954 SOL (-6.09%). The last signal was STANK at 07:55 UTC, 10.7 hours before this review. The 12-hour zero-signal rule is not met, so no threshold was relaxed. All-time record is still v2's 6 closed trades (1 win), which are closed business.

- Why no signal. 455 universe-token checks on v3: 235 `h1_weak` (52%), 111 a token in its cooldown (24%), 63 `h6_down`, 40 `buy_pressure`, 2 `h1_overheated`, 2 `m5_dropping`, 2 `txns_h1`. The universe was 6 to 9 tokens a cycle (median 8). Their median 1-hour change was -2.4% and only 29% of readings were at +2% or better, while SOL fell from $75.7 to $72.7 (-4%). The market is what kept the bot out.
- The v3 filter is not the cause. `txns_h1` blocked two checks, both GLITCH at 18:30 and 18:35 (96 and 99 trades in the hour), and at 18:30 GLITCH would have failed the buy-pressure test next (buy/sell 0.55).
- New entries the v3 filter would have blocked, from `python3 -m bot.replay --wide --set universe.min_age_days=3 --set universe.max_age_days=30 --set entry.min_txns_h1=50`: Macca (13:10, 112 trades, -12.9%) and CHILL (14:30, 91 trades, -18.5%). Entries under 150 trades are now 0 wins of 7 in that replay, against 3 of 9 at 150 or more. Both new ones are outside the bot's own universe and the gap still turns up by chance about one time in seven. A hint in the hypothesis's favour, no more.
- A modest relaxation would have bought nothing good. Replayed on the bot's universe: `h1_change_min_pct` at 1 or even 0 adds no trade at all in the whole record; `min_buy_sell_ratio_h1` 1.1 adds one (Leonida 16:35, open at -10%); `h6_change_min_pct` -5 adds one stop-loss (Leonida 11:55, -14.4%); `min_volume_accel` 1.0 adds one stop-loss (paws 10:05, -12.1%).
- Buy-pressure hint (n=1, not acted on). NIO passed every price test on 29 checks between 13:50 and 17:25 while its 6-hour change went from +4% to +36%, and failed only `buy_pressure`: 0.70 to 1.00 buys per sell against 1.2 needed. The rule counts trades, not money, so a rise carried by fewer, larger buys reads as selling. With the ratio at 0.7 the replay takes NIO at 14:05 for +15.0% and NIO on 13 Nov for +42.9%, and also paws for -18.3%: 7 closed, 3 wins, +1.8% per trade, against 4 closed, 1 win, -6.2% for v3 as it stands. The whole difference is two wins in one token, and 0.7 is a number found by looking for the one that lets NIO in. A story, not evidence.
- Meteora, the measurement the last review asked for. Snapshot rows have carried `dex` since 13:50, so this is 58 snapshots. Price step in quiet cycles (1 to 5 trades, volume under 0.5% of one side of the pool, SOL's own move taken out, tokens with 8 or more such cycles), 90th percentile: Meteora 2.4% over 63 cycles in 4 pools (CHOO 3.9%, STANK 3.2%, Dacity 2.3%, DacityCoin 1.7%); PumpSwap 2.4% over 223 cycles in 10 pools (1.6% to 3.3%); Raydium 1.4% over 53 cycles in 3 pools; MetaDAO 1.2% in 1. On this window Meteora pools do not stand apart from PumpSwap, and STANK reads 3.2%, not the 4.2% of this morning. No case for excluding Meteora or pricing it differently. Five hours is short: measure again on a full day.
- Stops: no new exits, so nothing new on fills.

**Bug fixed: a bad price print the guard from this morning could not see.** Two readings in the record are prices nobody traded at, on tokens that are in the bot's universe:

| Token | Time (UTC, 14 Nov) | Price before, at, after | Liquidity | Traded in those 5 minutes | Volume a real move that size needs |
|---|---|---|---|---|---|
| GLITCH | 04:50 | 0.001829, 0.002650 (+45%), 0.001834 | +22.8% | $12 | about $11,300 |
| Leonida | 16:50 | 0.000627, 0.000390 (-38%), 0.000623 | -20.0% | $2,286 (24-hour volume up $2,564) | about $6,600 |

The guard added this morning ignores a price that more than halves or doubles while liquidity stays within 15%. These two are smaller than 2x, and DexScreener appears to work out the liquidity figure from the same wrong price, so liquidity moved with it (a liquidity figure worked out from a price printed 45% too high would read 22.5% too high, and it read +22.8%). The bot held neither token. Had it held Leonida, the stop would have sold at -38%: the replay with a looser buy-pressure rule booked exactly that, -35.0%. Had it held GLITCH, half the position would have been sold at +45%, a profit that never existed.

The fix uses a second thing a pool cannot do: move without trades. Moving a constant-product pool by a price ratio r takes about half its liquidity times |sqrt(r) - 1| in volume. An open position now also ignores, for one cycle, a move beyond +25% or -20% since its last accepted reading when the volume traded since then is under half of that amount. "Traded since then" is the larger of the 5-minute volume and the rise in 24-hour volume; the second is there because the 5-minute figure sometimes lags the price (AI at 06:30: a real -24% that stayed, 5-minute volume $30, 24-hour volume up $4,031). The check only runs when the two readings are at most 6 minutes apart, so on the next cycle a move it held back is acted on whatever the volume: the delay is one cycle, never more. The old check is unchanged and both feed the same `suspect_price` log line, which now records the traded volume.

How well it separates, on all 15,751 pairs of consecutive readings of one pool in the record (161 moves that large): every bad print came with 0.39 of the needed volume or less (the two above and Dacity's); real moves came with 0.56 or more, and all but three with more than the full amount. One real move lands on the wrong side: GTA$ at 12:40, +89% while its liquidity fell 19% (0.28), on a pool the bot could not have held (under $50k). Run over every reading of every token as if it were held, the new check holds back three readings in 15,888: GLITCH, Leonida and GTA$. The half is a number chosen between 0.39 and 0.56 on two bad prints, so it is fitted; what is not fitted is the mechanism, and a wrong call costs one cycle of delay on a stop or a take-profit.

The replay uses the same check. With the live rules it gives the same trades as before (the five v2 trades it can see, each to the same hundredth; `--wide` 27 closed, unchanged).

**Changed, in full.**

1. Rulebook: nothing. v3 stays.
2. Plumbing, no rule in it: `traded_since` and `unbacked_move` in `bot/strategy.py`, used by `hold_suspect`; positions now remember the time and the 24-hour volume of their last accepted reading (`last_ts`, `last_vol_h24`). `bot/replay.py` mirrors it. README honesty rule updated.
3. Tests: 6 added, 2 adjusted (the scripted market now states the volume behind a real crash), 35 pass.

**First live cycle (18:45 UTC).** Pushed at 18:41 UTC and picked up by the 18:45 cycle: no errors, `api_calls` 43, `universe_ok` 7, no signal, nothing open. With no position open the new check has not run live yet; the first open position will carry `last_ts` and `last_vol_h24`.

**For the next review.**

- If the next review still finds no signal since 07:55 UTC, the 12-hour rule will allow one relaxation. The numbers above say none of the modest ones would have helped: the 1-hour floor at 1% or 0% adds nothing, and the others add one losing or underwater trade each. A relaxation is allowed, not required. If one is made, buy pressure is the only filter with a hint behind it (NIO), and a modest step (1.2 to 1.1) would not have let NIO in.
- Judge v3 only on v3 trades. There are none yet.
- Still open from the last review: the exit hint (entries that peak at +13% to +19% and end at the stop), the 1-hour-change hint, the cooldown hint, and the size of the universe (median 8 tokens a cycle; discovery is the lever and cannot be tested from the repo's data).
- Measure the Meteora price step again once a full day of rows has `dex`.
- Check `suspect_price` in the funnel and in `data/journal/events.jsonl`. Each event should be followed by a normal price on the next cycle.

**Would prove this review wrong.**

- Leaving the rules alone is wrong if cycles keep arriving and v3 has opened fewer than 2 trades by the end of 15 Nov while the replay with `--set entry.min_txns_h1=50` shows winners among the entries v3 blocked: then put `min_txns_h1` back to 50. If the replay shows no trades either way, the universe is the bottleneck, not the entry rules.
- The new check is wrong if a `suspect_price` event with a move under 2x is followed by the same price on the next cycle more than once in a while (real moves are being delayed), or if a position's close shows a stop or take-profit filled on a one-cycle spike that reversed (a bad print got through). In the first case raise nothing and remove `unbacked_move` from `hold_suspect`; in the second, look at what the volume read on that cycle before changing the half.

### v3, 2026-11-14 13:30 UTC review: a buy now needs 150 trades in the last hour, was 50 (plumbing: bad price prints, replay tool, DEX in snapshots)

**Health.** 288 cycles since launch, 172 since the last review. Last 6 hours: 72 cycles, median gap 5.0 minutes, longest 5.2. The newest cycle was 2 minutes old, so no `.kick`. Errors in 2 runs since the last review (06:45 and 07:05 UTC, one GeckoTerminal 429 each; the page was fetched on the next cycle) and none in the 80 runs after. `batch_miss` is 9 to 13 per cycle out of about 258 tokens (4%); 6 to 10 of those are `no_data`. The pool fix from the last review held: `allowed_pool_used` 4 to 6 per cycle, `api_calls` 39 to 46, no `pool lookup` error. RugCheck has run for all 6 signals and every response parsed (`score_normalised` 1, no risks, LP locked 40.5% to 99.8%). No `safety:*` or `skip:*` rows.

**v2 final record: 6 closed trades, 1 win. Six trades are hints, not findings.** Equity 4.6954 SOL (-6.09%), nothing open. Expectancy -10.28% per trade, total -0.3046 SOL, max drawdown 6.33%. SOL fell from $80.8 at launch to $75.4 (-7%).

| # | Token | Opened (UTC) | Trades in the hour before | Best while held | Exit | Net |
|---|---|---|---|---|---|---|
| 1 | WEALTH | 13 Nov 17:25 | 125 | +0.5% | stop | -18.84% |
| 2 | FLOAT | 13 Nov 18:50 | 160 | +2.4% | stop | -13.55% |
| 3 | Leonida | 13 Nov 18:55 | 726 | 0.0% | stop | -16.84% |
| 4 | :3 | 14 Nov 03:40 | 223 | +4.2% | stop | -15.10% |
| 5 | WASTED | 14 Nov 04:25 | 301 | +44.1% | half sold at +25%, rest trailed out | +20.76% |
| 6 | STANK | 14 Nov 07:55 | 108 | +17.1% | stop | -18.08% |

- Exits. The five stops cost 0.4029 SOL, average -16.48%. The price at the stop cycle was -12.2% to -15.8% (average -14.3%), so 2.3 points past the stop level with every cycle on time. As before, that is the gap between two 5-minute readings, not a late trigger.
- Left on the table. WASTED: the second half trailed out at +25%; two hours and twenty minutes later the token was 76% above the entry. STANK: +17.1% fifteen minutes in, 3 points short of the take-profit, then five hours down to the stop. One case each way; no exit change on that.
- The test the last review set for changing the entry rules (the next 5 to 10 trades stopped out without being more than a few percent up) is not met: of the three trades since, one won and one reached +17%. The change below rests on different evidence and is weaker than that test asked for. I say so plainly.

**New review tool: `python3 -m bot.replay`.** It replays the rulebook on the recorded snapshots. With v2's numbers it reproduces all six real trades, each within 0.1 points of the journal. Its limits are at the top of `bot/replay.py`: no RugCheck, no caps, one day of one falling market, and every variant tried on it is fitted to it. It gave three things.

1. *Universe.* The 24-hour check from 13 Nov is due and fails: `universe_ok` was 8 to 10 per run and under 10 in 140 of 169 runs. But looser universe numbers would not have found trades. Replayed since 18:40 UTC on 13 Nov: minimum age 2 days or 1 day adds one signal (Max, 13:10 today); `min_liq_to_mcap` 0.02 adds one (RAMBO, a stop-loss); maximum age 35 days adds none. About 9 tokens under 3 days old pass every other universe number each run and then fail the entry rules like the rest (`h1_weak` on 55% of their checks). More tokens have to come from discovery, not from thresholds. Not changed today.
2. *Cooldown (hint for later).* 443 of 1,505 universe-token checks (29%) were a token inside its 12-hour cooldown. With no cooldown the replay takes five more trades in WASTED and FLOAT: three wins, two stops, average +1.3%. Two tokens on one night. Portfolio section, not touched.
3. *Thin trading at entry (the change).* Below.

**Changed: `entry.min_txns_h1` 50 to 150. A hypothesis, on weak evidence.**

| Entries made with | Real v2 trades | Replay: every recorded token 3 to 30 days old |
|---|---|---|
| under 150 trades in the hour | 0 wins of 2 (WEALTH, STANK) | 0 wins of 5, average -16.7% (WEALTH, AMD, Gato, STANK, PIRATE) |
| 150 or more | 1 win of 4 | 3 wins of 9, average -3.3% |

The replay column is `python3 -m bot.replay --wide --set universe.min_age_days=3 --set universe.max_age_days=30 --set entry.min_txns_h1=50`: the v2 entry and exit rules on any token of tradable age, whatever its quote token or size.

- How weak. Two of the five are the real trades, so the replay adds three tokens (AMD, Gato, PIRATE), not five. The universe filters reject all three and none was RugChecked. Zero of 5 against 3 of 9 turns up by chance about one time in four. I also split the same 14 replayed trades on five other entry features. The 1-hour change split them just as cleanly (at or under +7.8%: 0 wins of 7; above: 3 of 7). Buy/sell ratio, volume acceleration, liquidity and age showed nothing. So the data does not single out thin trading, and the best of six splits always looks better than it is.
- Why act anyway, and why this one. (a) It is the candidate named after the first trade on 13 Nov ("a higher `min_txns_h1`"), not a pattern found by searching; the 1-hour change was found by searching. (b) There is a mechanism. Under 150 trades an hour is under 3 a minute, so the 1-hour change, the buy/sell ratio and the volume acceleration are each set by a handful of trades. STANK shows it: between 05:45 and 06:15 UTC its price sat at $0.00202 to $0.00203 while its reported 1-hour change read +3.3, -0.8, +3.3, +4.6, +0.5, +4.9, +0.6. That swing is only which side traded last (see the next section), and it is enough to pass the +2% entry test by itself. (c) It is a tightening and costs little: 54 of the 65 cycle-level entry passes since 18:40 on 13 Nov had 150 or more trades, and 4 of the 6 real trades would still have been taken, so expect about a third fewer trades. (d) The blocked entries stay measurable: `python3 -m bot.replay --set entry.min_txns_h1=50` keeps showing what they would have done.
- Why 150 and not more. At 200 the replay would also drop FLOAT's losing entry, at 250 also :3's, and the bot's own universe replays at +0.3% and +5.5% per trade instead of -8.5%. Picking the number that makes the past look best is tuning to the result. 150 removes only the group with no winner in it.
- What it does not do. On the same replay the v3 rules still lose: 10 closed, 3 wins, -4.5% per trade. This removes the worst group. It does not make the strategy profitable on the record.

**STANK and the Meteora cost blind spot: measured, not fixed.** STANK was the first trade on a Meteora pool, the SOL pool the last review's fix made visible. While it was held (one pool, liquidity about $140k) the price hopped between two levels on almost no volume: 10:40 to 11:20 UTC read 0.002256, 0.002352, 0.002352, 0.002352, 0.002257, 0.002350, 0.002234, 0.002327, 0.002213. Two of those 4% hops came with $21 and $106 of volume in the 5 minutes; a $106 trade moves a constant-product pool of that size by 0.3%. So the buy price and the sell price in that pool sit 4 to 5% apart, where the cost model charges about 2% for a round trip (0.5% fee and 0.5% slippage each way) plus impact. STANK's -18.08% is therefore 2 to 3 points too kind, and its entry and stop were read off whichever side traded last. In quiet cycles (1 to 5 trades, volume under 0.5% of one side of the pool) the 90th-percentile price move was 4.2% for STANK and 4.2% and 4.1% for the two other Meteora SOL pools the bot reads (CHOO, DacityCoin), against 2.1% to 3.1% for the PumpSwap tokens WEALTH, Leonida and :3 and 1.3% for FLOAT on Raydium. Three pools is a hint. The costs section is untouched: the data cannot give a fee per pool, and one section per review. The new entry rule would have blocked STANK (108 trades) but does not fix the cost of a busy Meteora pool. Snapshot rows now carry the DEX so the next review can measure this across the watchlist.

**Bug fixed: a bad price print could close a position at -100%.** DexScreener misprinted Dacity's price four times in 14 hours (00:40, 01:25, 07:10 and 07:39 UTC): under $0.000001 instead of $0.0021 for a single cycle, with liquidity only 5 to 8% lower than the reading before and the reported 1-hour change at -100%. The bot never held Dacity (it is over 30 days old), so no trade was affected. Had it held it, the stop would have fired and sold at that price: the replay booked exactly that, -100%, twice. A print the other way would have filled a take-profit at a fantasy price. Both would corrupt the record.

The fix uses what a pool cannot do. When a price really halves, the pool's liquidity in USD falls by about 30%. Every one of the 9 genuine one-cycle moves beyond 2x in the record shows it (inuhao: price -66%, liquidity -42%). So an open position now ignores, for one cycle, a price that more than halved or doubled since its last accepted reading while liquidity stayed within 15%. If the next reading agrees with the ignored one, it is acted on, so a real move is delayed by one cycle at most; readings that keep contradicting each other are ignored for two cycles and then taken as shown. Each ignored reading is logged as `suspect_price` in the run funnel and in `data/journal/events.jsonl`. In 12,911 pairs of consecutive readings only Dacity trips it. One real crash trips it across a gap in the record: GTA at 17:55 on 13 Nov, three hours old and never tradable, read 84% lower than 20 minutes earlier with more liquidity, not less. That is the known cost: one cycle of delay on a real crash that happens with flat or rising liquidity. Entries need no guard: on a bad print the reported 1-hour change reads -100% or far above the 25% cap, and the entry rules reject both.

**Changed, in full.**

1. Rulebook v3: `entry.min_txns_h1` 50 to 150. Nothing else.
2. Plumbing, no rule in it: the bad-print guard for open positions (`suspect_print` and `hold_suspect` in `bot/strategy.py`).
3. Plumbing: snapshot rows gain a 22nd field, `dex`.
4. New `bot/replay.py`, read-only, with its own tests.
5. Tests: 7 added, 2 adjusted, 29 pass. An offline dry run of four cycles on a copy of the live state ran clean: a thin signal was rejected with `e:txns_h1`, a busy one opened, a bad print on the open position was ignored and the position carried on.

**First live cycles (13:50 and 13:55 UTC).** Pushed at 13:50:00 UTC and picked up by the 13:50 cycle. Both cycles ran v3 with no errors, `api_calls` 41, `universe_ok` 8, no signal (4 `h1_weak`, 1 `buy_pressure`, 1 `h6_down`), nothing open. Snapshot rows have 22 fields; of the 51 rows at 13:50, 44 are PumpSwap pools, 4 Meteora, 2 Raydium and 1 MetaDAO. v3 trades start from the 13:50 cycle.

**For the next review.**

- Judge v3 only on v3 trades. v2 is closed at 6 trades.
- With `dex` in the snapshots, measure the quiet-cycle price step by DEX across the watchlist. If Meteora pools as a group show the 4% step, the choice is to exclude them in `universe` or to price them in `costs` (tightening either is allowed).
- Exit hint: three entries in the replay peaked at +13% to +19% and still ended at the full stop (STANK, AMD, Gato). If v3 trades do the same, the exit section is the candidate (a take-profit nearer +15%, or a stop moved to break-even after +10%).
- Entry hint not acted on: the 1-hour change. In the replay every entry with a 1-hour change at or under +7.8% lost (0 of 7, the real trades WEALTH at +4.3% and FLOAT at +4.1% among them). If v3's losers cluster there, `h1_change_min_pct` is the next candidate.
- Cooldown hint, item 2 above.
- Universe size: thresholds are not the lever, discovery is. Nothing in the repo's data can test a new source; that needs a session with API access or a new feed.
- Check `suspect_price` in the funnel. It should be rare, and never two cycles running on one position.

**Would prove this review wrong.**

- The entry change is wrong if v3's first 10 closed trades have 2 winners or fewer: v2 won 1 of 6 without the filter, so that would be no improvement. It is also wrong if, after a week, `python3 -m bot.replay --set entry.min_txns_h1=50` shows the blocked entries (under 150 trades) winning as often as the ones taken. In either case put it back to 50 and look at the exit side instead. Do not raise it further on replay results alone.
- It costs too much if v3 opens fewer than 2 trades a day over three days with cycles arriving: at that rate the proof gate is out of reach, and the universe has to grow before any entry filter can be judged.
- The bad-print guard is wrong if a `suspect_price` event is followed by the same price on the next cycle more than once in a while (it would mean real moves are being delayed), or if a position is ever ignored for more than two cycles running: then remove it.

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
