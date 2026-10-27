# Lab 16 — Provenance Gate

## 1. Objective

The goal of this lab was to determine what data was actually available on March 31, 2026, and compare those results to what we would see if we used information published later.

## 2. Row Funnel

| Step | Row(s) |
| --- | --- |
| Missing ticker | Row 11 |
| Exact duplicate | Row 7 |
| Published after decision date | Rows 3, 8, 10 |
| Older revision removed | Row 2 |
| Final as-of panel | Rows 1, 4, 5, 6, 9, 12 |

## 3. Signal Comparison

| Ticker | As-of signal | Naive signal |
| --- | --- | --- |
| AAA | +1.98% (February) | +5.83% (March) |
| BBB | -1.02% (February) | -5.15% (March) |
| CCC | +0.91% (February) | +1.82% (February, revised) |

## 4. Validation

I ran the Python file using March 31, 2026, as the decision date, and all the results matched the expected answers. I also changed the date to April 15, 2026, and the as-of signals matched the naive signals for all three tickers. After testing, I changed the decision date back to March 31.

## 5. Reflection

### What is look-ahead bias?

Look-ahead bias happens when we use information in an analysis that wasn't actually available at the time of the decision.

### Why do publication dates and revisions matter?

A number can measure one month but not be published until later. It can also be revised. We need to make sure we are only using information that was available when the decision was made.

### Which rule mattered most?

Rule 3 was important because it removed information that wasn't published by March 31. For example, AAA's March value wasn't published until April 10. Rule 4 was also important because it kept AAA's revised February value of 103 instead of the original 104. Because of these rules, AAA's as-of signal was only +1.98%, compared to the naive signal of +5.83%.

### What would a naive backtest claim?

A backtest using naive data could make a strategy look better than it really was because it uses information that wasn't available when the trades would have happened.
