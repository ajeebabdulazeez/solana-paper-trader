# Lessons and rule changes

The running record of what paper results have shown and why each rulebook version exists. Newest first. Each review adds an entry; a rule only changes when the data here supports it.

## How to review (instructions for each review session)

1. Run `python3 -m bot.report` and read `data/STATUS.md` and the latest `data/runs/*.jsonl` errors.
2. First check the bot is healthy: runs arriving, no repeated errors, `batch_miss` low, signals appearing. Fix plumbing before judging strategy.
3. Judge the current rulebook version only on its own trades. Under about 30 closed trades, treat every pattern as a hint, not a finding.
4. Look for: which exit reasons lose the most, which entry features separate winners from losers, how much gain was left on the table, and which funnel stage blocks the most candidates. `python3 -m bot.replay` (add `--wide`, `--no-cooldown` or `--set entry.min_txns_h1=50`) replays the rules on the recorded snapshots, so you can look past the bot's own few trades and keep measuring entries a rule now blocks. Its output is a hint, never a finding; the limits are listed at the top of `bot/replay.py`.
5. Change at most one rulebook section per review, bump `version`, and write the entry below: what the data showed, what changed, and what result would prove the change wrong.
6. Never loosen a safety rule to get more trades. Never tune to hit a return target.
7. Once a version looks good, stop changing it: the proof gate needs 100+ trades on one frozen version.

## Log

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
