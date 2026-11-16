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

## Log

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
