"""Download reproducible, adjusted month-end ETF prices for FIN 43900 Lab 15."""

from datetime import date
from pathlib import Path

import pandas as pd
import yfinance as yf


TICKERS = ["BIL", "IEF", "AGG", "VTI", "VXUS"]
START_DATE = "2021-09-01"
END_DATE = "2026-10-01"  # yfinance end dates are exclusive; this includes Sep. 2026.
PROJECT_FOLDER = Path(__file__).resolve().parent
CSV_PATH = PROJECT_FOLDER / "prices.csv"
SOURCES_PATH = PROJECT_FOLDER / "lab15-data-sources.md"

FUND_NAMES = {
    "BIL": "SPDR Bloomberg 1–3 Month T-Bill ETF",
    "IEF": "iShares 7–10 Year Treasury Bond ETF",
    "AGG": "iShares Core U.S. Aggregate Bond ETF",
    "VTI": "Vanguard Total Stock Market ETF",
    "VXUS": "Vanguard Total International Stock ETF",
}


def download_month_end_prices():
    """Return final-trading-day monthly adjusted Close values, oldest first."""
    # auto_adjust=True makes Close adjusted for distributions and stock splits.
    daily_data = yf.download(
        TICKERS, start=START_DATE, end=END_DATE, auto_adjust=True,
        progress=False, group_by="column", threads=False,
    )
    if daily_data.empty or "Close" not in daily_data:
        raise RuntimeError("Yahoo Finance returned no adjusted Close price data.")

    close_prices = daily_data["Close"].reindex(columns=TICKERS)
    monthly_prices = close_prices.resample("ME").last()
    monthly_prices = monthly_prices.loc["2021-09-01":"2026-09-30"].copy()

    if monthly_prices.isna().any().any():
        missing = monthly_prices.columns[monthly_prices.isna().any()].tolist()
        raise RuntimeError(
            "Yahoo Finance returned missing month-end prices for: " + ", ".join(missing)
        )
    if not monthly_prices.index.is_monotonic_increasing:
        raise RuntimeError("Month-end observations are not sorted oldest to newest.")
    if len(monthly_prices) < 61:
        raise RuntimeError(
            f"Only {len(monthly_prices)} monthly prices were available; 61 are needed for 60 returns."
        )

    # September 2021 is the starting price; its successor creates October 2021's return.
    return monthly_prices


def write_sources(observations):
    """Document the live data source and the historical-estimate limitation."""
    access_date = date.today().isoformat()
    source_lines = [
        "# Lab 15 historical data sources",
        "",
        "## Funds",
        "",
    ]
    source_lines.extend(f"- `{ticker}` — {FUND_NAMES[ticker]}" for ticker in TICKERS)
    source_lines.extend([
        "",
        "## Download details",
        "",
        "- Data source: Yahoo Finance, accessed through `yfinance`.",
        f"- Download date: {access_date}.",
        f"- First observation: {observations.index[0].date().isoformat()}.",
        f"- Last observation: {observations.index[-1].date().isoformat()}.",
        f"- Monthly price observations: {len(observations)}.",
        "- `auto_adjust=True` was used, so Close prices are adjusted for distributions and splits.",
        "- The September 2021 starting price supports 60 monthly returns from October 2021 through September 2026.",
        "",
        "Historical returns calculated from these prices are estimates based on past data, not forecasts.",
        "",
    ])
    SOURCES_PATH.write_text("\n".join(source_lines), encoding="utf-8")


def main():
    """Download, validate, and save CSV observations and their source documentation."""
    monthly_prices = download_month_end_prices()
    output = monthly_prices.reset_index().rename(columns={"Date": "Date"})
    output["Date"] = output["Date"].dt.strftime("%Y-%m-%d")
    output.to_csv(CSV_PATH, index=False, columns=["Date", *TICKERS], float_format="%.10f")
    write_sources(monthly_prices)

    print(f"Saved {len(monthly_prices)} monthly prices to {CSV_PATH.name}.")
    print(f"First date: {output['Date'].iloc[0]}; last date: {output['Date'].iloc[-1]}.")
    print(f"Monthly returns available: {len(monthly_prices) - 1}.")


if __name__ == "__main__":
    main()
