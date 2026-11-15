# Paper trading status

Updated 2026-11-15T03:35:11Z (UTC), rulebook v3. **Simulated trades only. No real money.** Full trade ledger: [trades.csv](trades.csv).

- Equity: **4.6271 SOL** (started with 5.0 SOL, -7.46%)
- Cash: 4.6271 SOL, open positions: 0, closed trades: 9
- Watchlist: 186 tokens, entry signals this run: 0

## Closed trades

| Group | Trades | Win rate | Avg win | Avg loss | Expectancy/trade | Total P&L (SOL) | Profit factor |
|---|---|---|---|---|---|---|---|
| All | 9 | 22.2% | 20.88% | -16.74% | -8.38% | -0.3729 | 0.35 |

Max drawdown 7.46%, average hold 156.7 min, simulated fees 0.0819 SOL.

## Last 10 closed

| # | Token | Closed | Exit | P&L % | P&L SOL |
|---|---|---|---|---|---|
| 9 | FLOAT | 2026-11-15T01:45:11Z | stop_loss | -20.52% | -0.0976 |
| 8 | paws | 2026-11-15T01:15:10Z | stop_loss | -14.22% | -0.0693 |
| 7 | WASTED | 2026-11-14T22:25:08Z | trailing_stop | +21.00% | +0.0986 |
| 6 | STANK | 2026-11-14T13:25:08Z | stop_loss | -18.08% | -0.0864 |
| 5 | WASTED | 2026-11-14T06:05:08Z | trailing_stop | +20.76% | +0.0983 |
| 4 | :3 | 2026-11-14T05:40:10Z | stop_loss | -15.10% | -0.0718 |
| 2 | FLOAT | 2026-11-13T23:15:13Z | stop_loss | -13.55% | -0.0671 |
| 1 | WEALTH | 2026-11-13T19:55:09Z | stop_loss | -18.84% | -0.0942 |
| 3 | Leonida | 2026-11-13T19:35:08Z | stop_loss | -16.84% | -0.0834 |

## Errors in the last run

- gecko h24_volume_usd_desc p2: HTTP 429 for https://api.geckoterminal.com/api/v2/networks/solana/pools?sort=h24_volume_usd_desc&page=2
