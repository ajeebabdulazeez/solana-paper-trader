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

### v1, 2026-11-13: starting hypotheses

No data yet. Thresholds are guesses based on the agreed approach: established tokens (3 to 30 days), real liquidity, safety-screened, moderate momentum entries, tight risk per trade. First job of the first reviews is to confirm the bot's data plumbing against the live API, which could not be tested before launch.
