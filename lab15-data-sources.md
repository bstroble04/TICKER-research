# Lab 15 historical data sources

## Funds

- `BIL` — SPDR Bloomberg 1–3 Month T-Bill ETF
- `IEF` — iShares 7–10 Year Treasury Bond ETF
- `AGG` — iShares Core U.S. Aggregate Bond ETF
- `VTI` — Vanguard Total Stock Market ETF
- `VXUS` — Vanguard Total International Stock ETF

## Download details

- Data source: Yahoo Finance, accessed through `yfinance`.
- Download date: 2026-10-22.
- First observation: 2021-09-30.
- Last observation: 2026-09-30.
- Monthly price observations: 61.
- `auto_adjust=True` was used, so Close prices are adjusted for distributions and splits.
- The September 2021 starting price supports 60 monthly returns from October 2021 through September 2026.

Historical returns calculated from these prices are estimates based on past data, not forecasts.
