"""FIN 43900 Lab 14: Portfolio baselines for the Meridian Foundation.

All rates below are course-authored training values, expressed as decimals.
The functions are kept separate so they can be imported in Lab 15.
"""

import csv
import math
import statistics


# Editable inputs: investment names, expected annual returns, and volatilities.
investments = [
    "Treasury bills",
    "Treasury 10-year note",
    "Investment-grade bond fund",
    "Global equity index fund",
]
expected_returns = [0.035, 0.043, 0.050, 0.080]
volatilities = [0.005, 0.070, 0.060, 0.160]

# Correlations use the same investment order as the lists above.
correlations = [
    [1.00, 0.10, 0.05, 0.00],
    [0.10, 1.00, 0.80, -0.10],
    [0.05, 0.80, 1.00, 0.25],
    [0.00, -0.10, 0.25, 1.00],
]

EXPECTED_RETURN_OBJECTIVE = 0.065  # CPI of 2.5% plus 4.0%
RESERVE_ELIGIBLE_INDICES = (0, 1)  # Treasury bills and 10-year note


def validate_correlation_matrix(correlation_matrix):
    """Raise ValueError unless a correlation matrix is square and symmetric."""
    size = len(correlation_matrix)
    if size == 0 or any(len(row) != size for row in correlation_matrix):
        raise ValueError("Correlation matrix must be square.")

    for row_index in range(size):
        for column_index in range(size):
            value = correlation_matrix[row_index][column_index]
            if not -1.0 <= value <= 1.0:
                raise ValueError(
                    "Correlation at row " + str(row_index + 1) + ", column "
                    + str(column_index + 1) + " is outside the allowed range -1 to +1."
                )
            if not math.isclose(value, correlation_matrix[column_index][row_index],
                                rel_tol=0.0, abs_tol=1e-12):
                raise ValueError("Correlation matrix must be symmetric.")


def build_covariance_matrix(volatility_values, correlation_matrix):
    """Return covariance[i][j] = correlation[i][j] * vol[i] * vol[j]."""
    if len(volatility_values) != len(correlation_matrix):
        raise ValueError("Volatility list and correlation matrix must have the same size.")
    validate_correlation_matrix(correlation_matrix)
    return [
        [correlation_matrix[i][j] * volatility_values[i] * volatility_values[j]
         for j in range(len(volatility_values))]
        for i in range(len(volatility_values))
    ]


def portfolio_return(weights, return_values):
    """Calculate the weighted expected annual return."""
    return sum(weight * expected_return for weight, expected_return in zip(weights, return_values))


def portfolio_volatility(weights, covariance_matrix):
    """Calculate sqrt(w' C w), using every covariance matrix entry."""
    if len(weights) != len(covariance_matrix):
        raise ValueError("Weight list and covariance matrix must have the same size.")
    variance = sum(
        weights[i] * weights[j] * covariance_matrix[i][j]
        for i in range(len(weights))
        for j in range(len(weights))
    )
    # Very small negative values can arise from floating-point rounding.
    if variance < -1e-12:
        raise ValueError("Portfolio variance cannot be negative.")
    return math.sqrt(max(variance, 0.0))


def reserve_eligible_weight(weights, eligible_indices=RESERVE_ELIGIBLE_INDICES):
    """Return the combined weight in Treasury bills and the 10-year Treasury note."""
    return sum(weights[index] for index in eligible_indices)


def benchmark_weights(number_of_investments=4):
    """Return the 40% IG bond fund / 60% global equity benchmark weights."""
    if number_of_investments != 4:
        raise ValueError("The benchmark is defined for the four course investments.")
    return [0.0, 0.0, 0.40, 0.60]


def equal_weight_weights(number_of_investments):
    """Return weights split equally among all investments."""
    if number_of_investments <= 0:
        raise ValueError("At least one investment is required.")
    return [1.0 / number_of_investments] * number_of_investments


def inverse_volatility_weights(volatility_values):
    """Weight each investment by 1 / volatility and normalize to 100%."""
    if any(volatility <= 0 for volatility in volatility_values):
        raise ValueError("All volatilities must be greater than zero.")
    inverse_volatilities = [1.0 / volatility for volatility in volatility_values]
    total = sum(inverse_volatilities)
    return [value / total for value in inverse_volatilities]


def find_lowest_risk_portfolio(expected_return_values, volatility_values,
                               correlation_matrix, target_expected_return,
                               minimum_reserve_weight, reserve_eligible_assets):
    """Search 5% long-only allocations and return the eligible lowest-risk result.

    ``reserve_eligible_assets`` may be a Boolean flag for each asset or a list
    of eligible asset indices.  The return and volatility are expected values,
    not guarantees of future results.
    """
    asset_count = len(expected_return_values)
    if asset_count == 0:
        raise ValueError("At least one asset is required for a portfolio search.")
    if len(volatility_values) != asset_count or len(correlation_matrix) != asset_count:
        raise ValueError("Returns, volatilities, and correlations must have the same size.")
    if any(volatility < 0 for volatility in volatility_values):
        raise ValueError("Volatilities cannot be negative.")
    if not 0.0 <= minimum_reserve_weight <= 1.0:
        raise ValueError("Minimum reserve weight must be between 0% and 100%.")

    if (len(reserve_eligible_assets) == asset_count
            and all(isinstance(flag, bool) for flag in reserve_eligible_assets)):
        eligible_indices = tuple(
            index for index, flag in enumerate(reserve_eligible_assets) if flag
        )
    else:
        eligible_indices = tuple(reserve_eligible_assets)
        if any(not isinstance(index, int) or isinstance(index, bool)
               or index < 0 or index >= asset_count for index in eligible_indices):
            raise ValueError("Reserve-eligible asset indices must identify valid assets.")

    # Build covariance once, then reuse the Lab 14 return/volatility functions.
    covariance_matrix = build_covariance_matrix(volatility_values, correlation_matrix)
    best_result = None
    increments = 20  # 20 x 5% increments make one fully invested portfolio.

    # Integer counters avoid floating-point totals that are almost, but not, 100%.
    def evaluate_allocations(prefix, remaining, positions_left):
        nonlocal best_result
        if positions_left == 1:
            allocation = prefix + [remaining]
            weights = [amount / increments for amount in allocation]
            expected_return = portfolio_return(weights, expected_return_values)
            reserve_weight = reserve_eligible_weight(weights, eligible_indices)
            if (expected_return >= target_expected_return
                    and reserve_weight >= minimum_reserve_weight):
                volatility = portfolio_volatility(weights, covariance_matrix)
                if best_result is None or volatility < best_result["volatility"]:
                    best_result = {
                        "weights": weights,
                        "expected_return": expected_return,
                        "volatility": volatility,
                        "reserve_eligible_weight": reserve_weight,
                    }
            return

        for amount in range(remaining + 1):
            evaluate_allocations(prefix + [amount], remaining - amount,
                                 positions_left - 1)

    evaluate_allocations([], increments, asset_count)
    return best_result


def estimate_historical_inputs(csv_filename, use_last_36=False):
    """Estimate annual inputs from monthly adjusted prices in a CSV file.

    These historical returns are estimates based on past prices, not forecasts.
    Set ``use_last_36`` to True to estimate from only the most recent 36 monthly
    returns; otherwise every available monthly return is used.
    """
    try:
        with open(csv_filename, "r", newline="", encoding="utf-8-sig") as price_file:
            rows = list(csv.reader(price_file))
    except OSError as error:
        raise ValueError(f"Could not read historical-price CSV '{csv_filename}': {error}") from error

    if len(rows) < 4:
        raise ValueError("Historical-price CSV needs a header and at least three price rows.")
    header = rows[0]
    if len(header) < 2 or not header[0].strip():
        raise ValueError("The first CSV column must contain dates, followed by asset tickers.")
    asset_names = [name.strip() for name in header[1:]]
    if any(not name for name in asset_names) or len(set(asset_names)) != len(asset_names):
        raise ValueError("Asset ticker names must be present and unique.")

    prices = []
    expected_columns = len(header)
    for row_number, row in enumerate(rows[1:], start=2):
        if len(row) != expected_columns:
            raise ValueError(f"CSV row {row_number} has {len(row)} columns; expected {expected_columns}.")
        if not row[0].strip():
            raise ValueError(f"CSV row {row_number} is missing its date.")
        try:
            price_row = [float(value) for value in row[1:]]
        except ValueError as error:
            raise ValueError(f"CSV row {row_number} contains a non-numeric adjusted price.") from error
        if any(not math.isfinite(price) or price <= 0 for price in price_row):
            raise ValueError(f"CSV row {row_number} has a missing, invalid, or non-positive price.")
        prices.append(price_row)

    monthly_returns = [
        [(current / previous) - 1.0 for current, previous in zip(current_row, previous_row)]
        for previous_row, current_row in zip(prices, prices[1:])
    ]
    if use_last_36:
        if len(monthly_returns) < 36:
            raise ValueError("At least 37 monthly prices are required to use the last 36 returns.")
        monthly_returns = monthly_returns[-36:]
    if len(monthly_returns) < 2:
        raise ValueError("At least two monthly returns are required to estimate volatility and correlation.")

    returns_by_asset = list(zip(*monthly_returns))
    monthly_means = [statistics.mean(values) for values in returns_by_asset]
    monthly_standard_deviations = [statistics.stdev(values) for values in returns_by_asset]
    if any(standard_deviation == 0 for standard_deviation in monthly_standard_deviations):
        raise ValueError("Correlation cannot be estimated when an asset has zero monthly-return variation.")

    correlation_matrix = []
    for left_index, left_returns in enumerate(returns_by_asset):
        correlation_row = []
        for right_index, right_returns in enumerate(returns_by_asset):
            if left_index == right_index:
                correlation_row.append(1.0)
                continue
            covariance = sum(
                (left - monthly_means[left_index]) * (right - monthly_means[right_index])
                for left, right in zip(left_returns, right_returns)
            ) / (len(monthly_returns) - 1)
            correlation = covariance / (monthly_standard_deviations[left_index]
                                        * monthly_standard_deviations[right_index])
            # Clamp only insignificant floating-point spillover beyond +/- 1.
            correlation_row.append(max(-1.0, min(1.0, correlation)))
        correlation_matrix.append(correlation_row)

    return (
        asset_names,
        [monthly_mean * 12 for monthly_mean in monthly_means],
        [standard_deviation * math.sqrt(12) for standard_deviation in monthly_standard_deviations],
        correlation_matrix,
    )


def print_portfolio(name, weights, covariance_matrix):
    """Print one portfolio's weights, return, volatility, and objective result."""
    expected_return = portfolio_return(weights, expected_returns)
    volatility = portfolio_volatility(weights, covariance_matrix)
    reserve_weight = reserve_eligible_weight(weights)

    print(name)
    for investment, weight in zip(investments, weights):
        print(f"  {investment}: {weight:.1%}")
    print(f"  Expected annual return: {expected_return:.2%}")
    print(f"  Portfolio volatility: {volatility:.2%}")
    print(f"  Reserve-eligible weight: {reserve_weight:.1%}")
    print(f"  Meets {EXPECTED_RETURN_OBJECTIVE:.1%} objective: "
          f"{'Yes' if expected_return >= EXPECTED_RETURN_OBJECTIVE else 'No'}")
    print()


def main():
    """Validate inputs, build covariance, and report the three baseline portfolios."""
    covariance_matrix = build_covariance_matrix(volatilities, correlations)
    portfolios = [
        ("Benchmark", benchmark_weights(len(investments))),
        ("Equal weight", equal_weight_weights(len(investments))),
        ("Inverse volatility", inverse_volatility_weights(volatilities)),
    ]
    for name, weights in portfolios:
        print_portfolio(name, weights, covariance_matrix)


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        print(f"Error: {error}")
        raise SystemExit(1)
