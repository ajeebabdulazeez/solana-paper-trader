# solana-paper-trader

A paper-trading bot for Solana tokens. **It trades simulated money only.** It holds no wallet, no keys and cannot place a real order.

The aim is to find out, with evidence, whether a rule-based strategy for established Solana tokens makes money after costs, before any real SOL is risked.

## How it works

| Part | What it does | Where |
|---|---|---|
| Bot | Every 5 minutes, one short run per cycle: discovers tokens (DexScreener feeds, GeckoTerminal pool lists), pulls DexScreener data, records a snapshot, applies the rulebook mechanically, opens and closes paper trades | `bot/`, run by `.github/workflows/bot.yml` |
| Rulebook | Every threshold the bot uses. Versioned; each trade records the version that produced it | `rulebook.json` |
| Data | Snapshots, trade journal, portfolio state | `data/` |
| Reviews | A few times a day Claude reads the results, writes up what worked and what did not, and changes the rulebook | `reviews/` |

The bot never edits the rules. Reviews never place trades. That separation is what makes results traceable.

## Where to look

- `data/STATUS.md`: current equity, open positions, last trades. Rewritten every run.
- `data/trades.csv`: the trade ledger as a spreadsheet, one row per paper trade (open and closed), newest first. Rewritten every run.
- `data/journal/trades.jsonl`: one line per closed trade, with the market conditions at entry.
- `reviews/LESSONS.md`: what has been learned so far and why each rule changed.

## Strategy in one paragraph (rulebook v3)

Only tokens 3 to 30 days old with real liquidity, volume and trading activity, that pass a RugCheck safety screen. Buy when the last hour shows moderate upward momentum with more buyers than sellers, rising volume and at least 150 trades. Risk 0.5 SOL per trade, at most 5 positions and 10 new trades a day. Exit on a 12% stop-loss, sell half at +20% and trail the rest, or leave after 6 hours. Every number is a starting guess to be tested.

## Honesty rules for the simulation

- Every fill pays a swap fee, a network fee, base slippage and price impact sized to the pool.
- Stops fill at the price seen when the bot runs, not at the stop level, so gaps between runs cost what they would really cost.
- A drained pool returns almost nothing. A token that disappears from the data is written off at zero.
- If the safety check cannot be completed, the trade is skipped.
- A bad data print fills nothing. If a held token's price more than halves or doubles between two cycles while its pool's liquidity stays within 15%, the reading is ignored for that cycle: no stop, no take-profit. In a real pool, price and liquidity move together, so this pattern is the data source misprinting. If the next cycle shows the same price it is acted on, so a real move is delayed by one cycle at most. The same one-cycle wait applies to a second kind of bad print, where the data source moves the liquidity figure along with the wrong price: a move beyond +25% or -20% between two cycles five minutes apart, on less than half the trading volume a pool of that size needs to move that far. Every ignored reading is logged (`suspect_price` in the run funnel and in `data/journal/events.jsonl`).
- A token is judged on one pool: its deepest pool quoted in SOL, USDC or USDT if that pool has at least the watchlist's minimum liquidity, otherwise its deepest known pool (which the rulebook then rejects for its quote token). Fills, liquidity checks and stops use that pool's own numbers, and an open position stays on the pool it was opened on.
- Known blind spots: prices are sampled every 5 minutes or slower, real fills can be worse, and tokens are discovered from DexScreener's boost and profile feeds (which favour tokens whose teams paid for visibility) and GeckoTerminal's trending and most-traded pool lists, so anything outside those lists is never seen. Swap fees also differ from pool to pool (some Meteora pools charge well over 0.5%) and DexScreener does not report them, so the flat 0.5% in the cost model can be too low for a given pool; the review report splits results by DEX for that reason. Measured on 14 Nov 2026: in one Meteora pool the buy and sell prices sat 4 to 5% apart, against about 2% in the cost model, so a result on such a pool is a few points too kind.

## Proof gate before real money

At least 100 closed paper trades across at least two weeks on one frozen rulebook version, positive expectancy after costs, max drawdown under 25%, then one further untouched week as a dry run.

## Commands

```
python3 -m bot.run                         # one bot cycle
python3 -m bot.report                      # review statistics
python3 -m bot.replay                      # what the rulebook would have done on the recorded snapshots (hints only)
python3 -m unittest discover -s tests -v   # offline tests
```

Python 3.10+, standard library only.

## Snapshot row format

`data/snapshots/YYYY-MM-DD/HH.jsonl`, one line per run: `{ts, sol_usd, rows}`. Each row:

`[token, symbol, price_usd, liquidity_usd, market_cap, vol_m5, vol_h1, vol_h6, vol_h24, buys_m5, sells_m5, buys_h1, sells_h1, buys_h24, sells_h24, chg_m5, chg_h1, chg_h6, chg_h24, age_days, quote_symbol, dex]`

`quote_symbol` was added on 2026-11-13 (from the 18:40 UTC run); earlier rows have 20 fields. `dex` (the DEX of the pool the row describes) was added on 2026-11-14 (from the 13:50 UTC run); rows before that have 21 fields.

Not financial advice. Most traders of new tokens lose money.
