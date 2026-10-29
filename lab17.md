# Lab 17 — Point-in-Time Audit

## Objective

This lab determines whether economic data was actually available on historical investment decision dates. I compare today's FRED data with historical ALFRED vintages, which show what was known on a selected date.

Publication lag is the delay between the date an economic value describes and the date it becomes available. A revision is a later change to an already published value. Look-ahead bias happens when a historical backtest uses data that was not available at the time of the decision. That can make a strategy appear better than it could have been in real time.

## Streamlit Application

The `asof_app.py` application downloads current FRED observations and historical ALFRED vintages without an API key. It displays separate charts for BAA, FEDFUNDS, DGS10, and MORTGAGE30US. The app also accepts an additional series ID, such as PAYEMS.

For each selected series, the app compares today's data with the selected historical vintage. It calculates observations that became available after the historical cutoff and revisions on matching observation dates.

## Known Answer Validation

I tested the application using an As known on date of October 5, 2026. All four series matched the expected historical values. 

| Series | Historical observation returned | Value | Result |
|---|---|---:|---|
| BAA | September 2026 | 6.47 | Pass |
| FEDFUNDS | September 2026 | 3.75 | Pass |
| DGS10 | October 2, 2026 | 5.28 | Pass |
| MORTGAGE30US | October 1, 2026 | 7.28 | Pass |

## PAYEMS Revision Test

I tested PAYEMS using a historical cutoff of January 15, 2025, to compare the historical employment value with today's revised value.

| Check | Result |
|---|---:|
| Historical cutoff | January 15, 2025 |
| Observation month | December 2024 |
| Historical value | 159,536 |
| Current revised value | 158,316 |
| Difference | -1,220 |
| Revised matching observation dates | 381 |
| Validation | Pass |

The historical and current values for the same December 2024 observation are different. This shows why point-in-time data matters: a backtest should use the value that was known at the time, not a later revision that an investor could not have seen.

## My Series — DGS10

I chose DGS10 because my Project 2 portfolio includes bonds and equities. Treasury yields affect bond prices and can also influence equity valuations through discount rates and investor expectations.

On October 29, 2026, my Streamlit app showed the last known DGS10 observation as October 27, 2026, with a yield of 4.99%. This observation was visible in my app screenshot.

## Data Card

| Field | DGS10 details |
|---|---|
| Original source | Board of Governors of the Federal Reserve System |
| Data provider | FRED, Federal Reserve Bank of St. Louis |
| Release | H.15 Selected Interest Rates |
| Official FRED link | <https://fred.stlouisfed.org/series/DGS10> |
| Measure | Market yield on U.S. Treasury securities at 10-year constant maturity |
| Units | Percent, not seasonally adjusted |
| Frequency | Daily |
| Publication timing | Published through the Federal Reserve's H.15 Selected Interest Rates release. I use ALFRED to determine which observations were available by the historical decision date. |
| Revisions | Compare historical ALFRED vintages with today's FRED data; do not assume a specific DGS10 revision count without testing. |
| Download date | October 29, 2026 |
| Observation shown in my app | October 27, 2026 — 4.99% |

## Three Values Checked Against FRED

| Observation date | App value | FRED page value | Match? |
|---|---:|---:|---|
| October 27, 2026 | 4.99% | 4.99% | Pass |
| October 26, 2026 | 5.00% | 5.00% | Pass |
| October 23, 2026 | 5.00% | 5.00% | Pass |

I compared three DGS10 observations against the FRED data and found that all three values matched.

## September 30, 2026 Historical Test

I ran this DGS10 historical test in the application with **As known on = September 30, 2026**.

| Check | Result |
|---|---|
| Latest DGS10 observation known on September 30, 2026 | September 29, 2026 |
| Historical yield | 5.26% |
| Observations published after cutoff | 19 |
| Revised matching observations | 0 |

When I changed the historical cutoff to September 30, 2026, the most recent DGS10 observation available was September 29, 2026, at 5.26%. This shows why I need to consider publication timing when using economic data for investment decisions.

## Code Explanation

The app uses separate cached functions for current FRED data and historical ALFRED vintages. Caching avoids downloading the same series again every time the page refreshes. The current function uses FRED, while the historical function requests the ALFRED vintage for the selected cutoff date.

The code treats `.` as a missing value and parses observation dates and values into usable date and number formats. It finds revisions by matching current and historical observations using their observation dates, not their row positions. It counts newly available observations as current nonmissing observations dated after the latest nonmissing observation in the historical vintage.

The vintage cutoff is the key point-in-time rule. The historical table and last-known historical value come from the ALFRED version available on that date. This prevents the code from using later observations or later revisions in a decision that is supposed to be historical, which helps prevent look-ahead bias.

## Partner Attack

| Item | Response to complete |
|---|---|
| Partner name | **Aaliah Blanco** |
| Field challenged | **Publication timing** |
| Partner's actual question | **"How do you know that the September 30, 2026 investment decision could use the 10-year Treasury yield without looking ahead?"** |
| My two-sentence response supported by the app or FRED page | **“When I set the ALFRED cutoff to September 30, 2026, the last known DGS10 observation in my app was September 29, 2026, at 5.26%. For Project 2, I would use that available vintage rather than a later observation or revision.”** |

## Final Decision — Admit, Quarantine, or Reject

**Decision: Admit with a point-in-time availability rule.** DGS10 is appropriate for my Project 2 bond and equity portfolio, but historical investment decisions may use only observations that were available by the decision time. If the current day's observation was not yet published, I will use the most recent available observation.

I will quarantine DGS10 if I cannot verify the release timing or the relevant historical vintage. I will reject it if the series cannot be used without look-ahead bias.

## Reflection

The September 30, 2026 historical test showed that the latest known DGS10 observation was September 29, 2026, at 5.26%. The October 29, 2026 audit showed that the latest known DGS10 observation was October 27, 2026, at 4.99%. These are practical examples that observations are not necessarily available immediately.

Publication delays and revisions mean that a historical backtest should not automatically use today's downloaded data. A strategy should be evaluated using the information an investor actually could have known on each decision date.

## Conclusion

Comparing FRED with ALFRED makes it possible to evaluate whether historical data was actually knowable at the time of an investment decision. This point-in-time approach gives Project 2 a more realistic and defensible data process.
