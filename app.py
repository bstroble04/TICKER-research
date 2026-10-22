"""Streamlit interface for FIN 43900 Lab 15.

This app intentionally imports the Lab 15 calculations from portfolio.py so
the user interface never maintains a separate version of portfolio math.
"""

import hashlib
import os
import tempfile

import streamlit as st

from portfolio import (
    EXPECTED_RETURN_OBJECTIVE,
    RESERVE_ELIGIBLE_INDICES,
    correlations,
    estimate_historical_inputs,
    expected_returns,
    find_lowest_risk_portfolio,
    investments,
    volatilities,
)


def read_uploaded_prices(uploaded_file, use_last_36):
    """Give the existing CSV estimator a temporary file path from Streamlit's upload."""
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temporary_file:
            temporary_file.write(uploaded_file.getvalue())
            temporary_path = temporary_file.name
        return estimate_historical_inputs(temporary_path, use_last_36=use_last_36)
    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.unlink(temporary_path)


def portfolio_table(asset_names, result):
    """Show a search result with percentage formatting suitable for a class demo."""
    if result is None:
        st.warning("No mix meets the objective")
        return

    rows = "\n".join(
        f"| {asset_name} | {weight:.2%} |"
        for asset_name, weight in zip(asset_names, result["weights"])
    )
    st.markdown("| Asset | Weight |\n| --- | ---: |\n" + rows)
    st.write(f"Expected return: **{result['expected_return']:.2%}**")
    st.write(f"Volatility: **{result['volatility']:.2%}**")
    st.write(f"Reserve-eligible weight: **{result['reserve_eligible_weight']:.2%}**")


st.set_page_config(page_title="Lab 15 — Portfolio Stability Decision", layout="wide")
st.title("Lab 15 — Portfolio Stability Decision")
st.caption("Built with AI help, a learning demonstration, not investment advice.")

# Sidebar controls describe the portfolio policy and optional historical data source.
with st.sidebar:
    st.header("Portfolio settings")
    return_objective_percent = st.number_input(
        "Expected-return objective (%)", min_value=0.0, max_value=100.0,
        value=EXPECTED_RETURN_OBJECTIVE * 100, step=0.1, format="%.2f",
    )
    minimum_reserve_percent = st.number_input(
        "Minimum reserve-eligible weight (%)", min_value=0.0, max_value=100.0,
        value=3.0, step=0.1, format="%.2f",
    )
    uploaded_prices = st.file_uploader("Historical investment prices (CSV)", type="csv")
    use_last_36 = st.checkbox("Use only the last 36 monthly returns")

# portfolio.py uses decimals, while the interface uses familiar percentage entries.
return_objective = return_objective_percent / 100
minimum_reserve_weight = minimum_reserve_percent / 100

# The portfolio.py Meridian inputs remain the no-upload starting point.
loaded_names = list(investments)
loaded_returns = list(expected_returns)
loaded_volatilities = list(volatilities)
loaded_correlations = [row[:] for row in correlations]
active_names = loaded_names
active_returns = loaded_returns
active_volatilities = loaded_volatilities
active_correlations = loaded_correlations
input_context = "meridian"
selected_period = "all_history"
reserve_default_flags = [index in RESERVE_ELIGIBLE_INDICES for index in range(len(active_names))]
loaded_reserve_flags = list(reserve_default_flags)

if uploaded_prices is not None:
    try:
        # A file hash and period name isolate widget state by data source and horizon.
        input_context = hashlib.sha256(uploaded_prices.getvalue()).hexdigest()[:12]
        selected_period = "last_36" if use_last_36 else "all_history"
        # This all-history version is retained as the "as-loaded" comparison.
        (loaded_names, loaded_returns, loaded_volatilities,
         loaded_correlations) = read_uploaded_prices(uploaded_prices, False)
        if use_last_36:
            (active_names, active_returns, active_volatilities,
             active_correlations) = read_uploaded_prices(uploaded_prices, True)
        else:
            (active_names, active_returns, active_volatilities,
             active_correlations) = (
                loaded_names, loaded_returns, loaded_volatilities, loaded_correlations
            )
        # Project 2's ETF policy treats BIL, not IEF, as reserve-eligible.
        reserve_default_flags = [asset_name == "BIL" for asset_name in active_names]
        loaded_reserve_flags = [asset_name == "BIL" for asset_name in loaded_names]
        st.info(
            "Historical annual returns shown below are estimates from past prices, "
            "not forecasts. The as-loaded comparison always uses all available months."
        )
    except ValueError as error:
        st.error(f"Could not estimate inputs from the uploaded CSV: {error}")
        st.stop()

st.subheader("Expected-return estimates and reserve eligibility")
st.caption("Expected returns are editable estimates, not forecasts. Enter percentages (for example, 8.00).")

# Each current estimate and reserve designation can be changed without copying math here.
edited_returns = []
reserve_flags = []
for index, (asset_name, return_estimate) in enumerate(zip(active_names, active_returns)):
    # Keeping this context in the key prevents one period's estimates leaking into another.
    widget_context = f"{input_context}_{selected_period}_{index}_{asset_name}"
    left_column, right_column = st.columns([3, 2])
    with left_column:
        edited_returns.append(st.number_input(
            f"{asset_name} expected annual return estimate (%)",
            min_value=-100.0, max_value=100.0, value=float(return_estimate * 100),
            step=0.1, format="%.2f", key=f"return_{widget_context}",
        ) / 100)
    with right_column:
        reserve_flags.append(st.checkbox(
            f"{asset_name} is reserve-eligible",
            value=reserve_default_flags[index],
            key=f"reserve_{widget_context}",
        ))

try:
    # "As loaded" uses unedited, all-history inputs when a CSV is supplied.
    as_loaded_result = find_lowest_risk_portfolio(
        loaded_returns, loaded_volatilities, loaded_correlations,
        return_objective, minimum_reserve_weight, loaded_reserve_flags,
    )
    current_result = find_lowest_risk_portfolio(
        edited_returns, active_volatilities, active_correlations,
        return_objective, minimum_reserve_weight, reserve_flags,
    )
except ValueError as error:
    st.error(f"The portfolio inputs cannot be evaluated: {error}")
    st.stop()

st.subheader("Lowest-risk portfolios meeting the policy")
original_column, revised_column = st.columns(2)
with original_column:
    st.markdown("#### Original as-loaded portfolio")
    portfolio_table(loaded_names, as_loaded_result)
with revised_column:
    st.markdown("#### Current lowest-risk portfolio")
    portfolio_table(active_names, current_result)

# Compare only like-for-like asset lists; uploaded estimates retain the CSV asset order.
if (as_loaded_result is not None and current_result is not None
        and len(as_loaded_result["weights"]) == len(current_result["weights"])):
    largest_change = max(
        abs(current_weight - original_weight)
        for original_weight, current_weight in zip(
            as_loaded_result["weights"], current_result["weights"]
        )
    )
    st.metric("Largest weight change", f"{largest_change * 100:.2f} percentage points")
