"""FIN 43900 Lab 17 — point-in-time FRED / ALFRED audit app."""

from datetime import date
from io import StringIO
from urllib.parse import quote

import pandas as pd
import requests
import streamlit as st


FRED_GRAPH_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
ALFRED_GRAPH_URL = (
    "https://alfred.stlouisfed.org/graph/alfredgraph.csv?id={series_id}"
    "&vintage_date={vintage_date}"
)
DEFAULT_SERIES = {
    "BAA": "Moody's Seasoned Baa Corporate Bond Yield",
    "FEDFUNDS": "Effective Federal Funds Rate",
    "DGS10": "Market Yield on U.S. Treasury Securities at 10-Year Constant Maturity",
    "MORTGAGE30US": "30-Year Fixed Rate Mortgage Average in the United States",
}


def _read_fred_csv(url: str, series_id: str) -> pd.DataFrame:
    """Download and normalize a FRED graph CSV, where '.' means missing."""
    response = requests.get(url, timeout=30, headers={"User-Agent": "FIN43900-Lab17/1.0"})
    response.raise_for_status()
    frame = pd.read_csv(StringIO(response.text), na_values=["."], keep_default_na=True)
    if frame.empty or len(frame.columns) < 2:
        raise ValueError("FRED returned no usable observations.")

    date_column = frame.columns[0]
    value_column = series_id if series_id in frame.columns else frame.columns[-1]
    frame = frame[[date_column, value_column]].copy()
    frame.columns = ["observation_date", "value"]
    frame["observation_date"] = pd.to_datetime(frame["observation_date"], errors="coerce")
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    return frame.dropna(subset=["observation_date"]).sort_values("observation_date")


@st.cache_data(ttl=3600, show_spinner=False)
def download_current_data(series_id: str) -> pd.DataFrame:
    """Get the currently revised FRED version of a series."""
    series_id = series_id.strip().upper()
    return _read_fred_csv(FRED_GRAPH_URL.format(series_id=quote(series_id)), series_id)


@st.cache_data(ttl=3600, show_spinner=False)
def download_historical_data(series_id: str, vintage_date: str) -> pd.DataFrame:
    """Get the ALFRED vintage that was available on ``vintage_date``."""
    series_id = series_id.strip().upper()
    return _read_fred_csv(
        ALFRED_GRAPH_URL.format(series_id=quote(series_id), vintage_date=vintage_date), series_id
    )


def last_valid_observation(frame: pd.DataFrame) -> pd.Series | None:
    """Return the latest non-missing observation, or None."""
    valid = frame.dropna(subset=["value"])
    return None if valid.empty else valid.iloc[-1]


def fred_link(series_id: str) -> str:
    return f"https://fred.stlouisfed.org/series/{quote(series_id)}"


def format_value(value: float | None) -> str:
    return "—" if value is None or pd.isna(value) else f"{value:,.3f}".rstrip("0").rstrip(".")


def format_date(value: pd.Timestamp | date) -> str:
    """Platform-independent long date formatting (Windows does not support %-d)."""
    return f"{value.strftime('%B')} {value.day}, {value.year}"


def audit_series(current: pd.DataFrame, historical: pd.DataFrame) -> tuple[pd.Series | None, pd.Series | None, int, int]:
    """Compare vintages on matching observation dates, never on row positions."""
    current_last = last_valid_observation(current)
    historical_last = last_valid_observation(historical)
    current_valid = current.dropna(subset=["value"])
    historical_valid = historical.dropna(subset=["value"])

    matched = historical_valid.merge(
        current_valid, on="observation_date", how="inner", suffixes=("_historical", "_current")
    )
    revision_count = int((matched["value_historical"] != matched["value_current"]).sum())
    latest_historical_date = historical_valid["observation_date"].max()
    published_after_count = int(
        (current_valid["observation_date"] > latest_historical_date).sum()
    )
    return historical_last, current_last, published_after_count, revision_count


st.set_page_config(page_title="FRED Point-in-Time Audit", page_icon="📈", layout="wide")
st.title("Point-in-Time Audit for Interest Rates")
st.caption(
    "Data from FRED and ALFRED, Federal Reserve Bank of St. Louis, downloaded today. "
    "Built with AI help. A learning demonstration, not investment advice."
)

with st.sidebar:
    st.header("Audit settings")
    selected = st.multiselect(
        "Series",
        options=list(DEFAULT_SERIES),
        default=list(DEFAULT_SERIES),
        format_func=lambda series_id: f"{series_id} — {DEFAULT_SERIES[series_id]}",
    )
    extra_id = st.text_input("Add another FRED series ID", placeholder="For example: PAYEMS").strip().upper()
    start_date = st.date_input("Start date", value=date(2020, 1, 1))
    as_known_on = st.date_input("As known on", value=date.today(), max_value=date.today())

series_ids = selected.copy()
if extra_id and extra_id not in series_ids:
    series_ids.append(extra_id)

if not series_ids:
    st.info("Choose at least one series in the sidebar.")
    st.stop()

st.subheader(f"Vintage cutoff: {format_date(as_known_on)}")
st.write("Each chart uses today's FRED data. The table compares it with the ALFRED vintage available on the cutoff date.")

summary_rows = []
for series_id in series_ids:
    series_name = DEFAULT_SERIES.get(series_id, "User-added FRED series")
    st.divider()
    st.subheader(f"{series_id} — {series_name}")
    try:
        with st.spinner(f"Downloading {series_id}…"):
            current = download_current_data(series_id)
            historical = download_historical_data(series_id, as_known_on.isoformat())

        historical_last, current_last, published_after, revisions = audit_series(current, historical)
        chart_data = current.loc[
            (current["observation_date"].dt.date >= start_date) & current["value"].notna(),
            ["observation_date", "value"],
        ].set_index("observation_date")
        if chart_data.empty:
            st.warning(f"No current non-missing {series_id} observations on or after {start_date:%Y-%m-%d}.")
        else:
            st.line_chart(chart_data, y="value", width="stretch")

        if historical_last is None:
            st.warning(f"ALFRED returned no non-missing {series_id} value for this vintage.")
        else:
            st.info(
                f"Last observation known on {as_known_on:%Y-%m-%d}: "
                f"{format_date(historical_last['observation_date'])} — "
                f"{format_value(historical_last['value'])}"
            )
        summary_rows.append(
            {
                "Series ID": fred_link(series_id),
                "Last observation date known historically": (
                    historical_last["observation_date"].date() if historical_last is not None else pd.NaT
                ),
                "Historical value": historical_last["value"] if historical_last is not None else None,
                "Last observation date available today": (
                    current_last["observation_date"].date() if current_last is not None else pd.NaT
                ),
                "Current value": current_last["value"] if current_last is not None else None,
                "Observations published after historical cutoff": published_after,
                "Revised matching observation dates": revisions,
            }
        )
    except (requests.RequestException, ValueError, pd.errors.ParserError) as error:
        st.error(f"Could not download {series_id}: {error}")

if summary_rows:
    st.divider()
    st.subheader("Point-in-time summary")
    summary = pd.DataFrame(summary_rows)
    st.dataframe(
        summary,
        hide_index=True,
        width="stretch",
        column_config={
            "Series ID": st.column_config.LinkColumn("Series ID", display_text=r".*/series/(.*)"),
            "Historical value": st.column_config.NumberColumn(format="%.3f"),
            "Current value": st.column_config.NumberColumn(format="%.3f"),
        },
    )
