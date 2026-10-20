"""FIN 43900 Lab 14: Portfolio baselines for the Meridian Foundation.

All rates below are course-authored training values, expressed as decimals.
The functions are kept separate so they can be imported in Lab 15.
"""

import math


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
