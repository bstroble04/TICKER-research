# Editable inputs (USD amounts and share counts are in millions).
STARTING_FCFF = 4741.8
YEARLY_GROWTH_RATES = [0.05, 0.045, 0.04, 0.035, 0.03]
WACC = 0.074
TERMINAL_GROWTH = 0.03
NON_OPERATING_CASH = 1015
DEBT = 8410
DILUTED_SHARES = 484

# Sensitivity and reverse-DCF inputs. Edit these without changing the base inputs above.
SENSITIVITY_WACCS = [0.064, 0.074, 0.084]
SENSITIVITY_TERMINAL_GROWTHS = [0.02, 0.03, 0.04]
TARGET_SHARE_PRICE = 86.91
REVERSE_SHIFT_LOWER_BOUND = -0.05
REVERSE_SHIFT_UPPER_BOUND = 0.10
BISECTION_TOLERANCE = 0.000001
BISECTION_MAX_ITERATIONS = 200
REVERSE_VARIABLE_NAME = "Uniform shift to all five explicit growth rates"


def calculate_valuation(wacc=None, terminal_growth=None, yearly_growth_rates=None):
    """Return the DCF results for a supplied set of valuation assumptions."""
    if wacc is None:
        wacc = WACC
    if terminal_growth is None:
        terminal_growth = TERMINAL_GROWTH
    if yearly_growth_rates is None:
        yearly_growth_rates = YEARLY_GROWTH_RATES
    if terminal_growth >= wacc:
        raise ValueError("terminal growth must be less than WACC")
    if len(yearly_growth_rates) != 5:
        raise ValueError("provide exactly five yearly growth rates")
    if DILUTED_SHARES <= 0:
        raise ValueError("diluted shares must be greater than zero")

    fcff_by_year = []
    fcff = STARTING_FCFF
    for growth_rate in yearly_growth_rates:
        fcff *= 1 + growth_rate
        fcff_by_year.append(fcff)

    present_value_explicit_fcff = sum(
        cash_flow / (1 + wacc) ** year
        for year, cash_flow in enumerate(fcff_by_year, start=1)
    )
    terminal_value_year_5 = (
        fcff_by_year[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
    )
    present_value_terminal_value = terminal_value_year_5 / (1 + wacc) ** 5
    enterprise_value = present_value_explicit_fcff + present_value_terminal_value
    equity_value = enterprise_value + NON_OPERATING_CASH - DEBT
    value_per_diluted_share = equity_value / DILUTED_SHARES
    terminal_value_share_of_enterprise_value = (
        present_value_terminal_value / enterprise_value
    )
    return {
        "fcff_by_year": fcff_by_year,
        "present_value_explicit_fcff": present_value_explicit_fcff,
        "terminal_value_year_5": terminal_value_year_5,
        "present_value_terminal_value": present_value_terminal_value,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "value_per_diluted_share": value_per_diluted_share,
        "terminal_value_share_of_enterprise_value": terminal_value_share_of_enterprise_value,
    }


def print_sensitivity_grid():
    """Print value per diluted share for each valid WACC/growth combination."""
    print("\nSensitivity Grid: Value per Diluted Share ($)")
    header = "WACC \\ Terminal Growth".ljust(24)
    header += "".join(f"{growth:.1%}".rjust(12) for growth in SENSITIVITY_TERMINAL_GROWTHS)
    print(header)
    for wacc in SENSITIVITY_WACCS:
        row = f"{wacc:.1%}".ljust(24)
        for terminal_growth in SENSITIVITY_TERMINAL_GROWTHS:
            if terminal_growth >= wacc:
                row += "invalid".rjust(12)
            else:
                value = calculate_valuation(wacc=wacc, terminal_growth=terminal_growth)[
                    "value_per_diluted_share"
                ]
                row += f"{value:.2f}".rjust(12)
        print(row)


def reverse_dcf_uniform_growth_shift():
    """Use bisection to solve for a uniform shift to all five annual growth rates."""
    lower = REVERSE_SHIFT_LOWER_BOUND
    upper = REVERSE_SHIFT_UPPER_BOUND

    if lower > upper:
        print("\nReverse DCF: no solution (lower bound is greater than upper bound).")
        return
    if any(rate + lower <= -1 or rate + upper <= -1 for rate in YEARLY_GROWTH_RATES):
        print("\nReverse DCF: no solution (the specified bracket creates annual growth of -100% or below).")
        return

    def price_for_shift(shift):
        shifted_rates = [rate + shift for rate in YEARLY_GROWTH_RATES]
        return calculate_valuation(yearly_growth_rates=shifted_rates)["value_per_diluted_share"]

    def print_fixed_inputs():
        print("Held fixed:")
        print(f"  Base explicit growth rates: {YEARLY_GROWTH_RATES}")
        print(f"  WACC: {WACC:.2%}")
        print(f"  Terminal growth: {TERMINAL_GROWTH:.2%}")
        print(f"  Starting FCFF: {STARTING_FCFF}")
        print(f"  Non-operating cash: {NON_OPERATING_CASH}")
        print(f"  Debt: {DEBT}")
        print(f"  Diluted shares: {DILUTED_SHARES}")

    lower_price = price_for_shift(lower)
    upper_price = price_for_shift(upper)
    if not min(lower_price, upper_price) <= TARGET_SHARE_PRICE <= max(lower_price, upper_price):
        print("\nReverse DCF: no solution in the specified bracket.")
        print(f"Target price: ${TARGET_SHARE_PRICE:.2f}; bracket: {lower:+.2%} to {upper:+.2%}")
        return

    for _ in range(BISECTION_MAX_ITERATIONS):
        midpoint = (lower + upper) / 2
        midpoint_price = price_for_shift(midpoint)
        if abs(midpoint_price - TARGET_SHARE_PRICE) < BISECTION_TOLERANCE:
            break
        if midpoint_price < TARGET_SHARE_PRICE:
            lower = midpoint
        else:
            upper = midpoint
    else:
        print("\nReverse DCF: no solution within the iteration limit.")
        return

    print(f"\nReverse DCF: {REVERSE_VARIABLE_NAME}")
    print(f"Solved shift: {midpoint:+.4%}")
    print(f"Target price: ${TARGET_SHARE_PRICE:.2f}")
    print_fixed_inputs()

def main():
    """Calculate a five-year FCFF discounted cash flow valuation."""
    try:
        results = calculate_valuation()
    except ValueError as error:
        raise SystemExit(f"Error: {error} for the Gordon-growth formula.") from error

    for year, cash_flow in enumerate(results["fcff_by_year"], start=1):
        print(f"FCFF Year {year}: {cash_flow:.4f}")
    print(f"Present Value of Explicit FCFF: {results['present_value_explicit_fcff']:.4f}")
    print(f"Terminal Value at Year 5: {results['terminal_value_year_5']:.4f}")
    print(f"Present Value of Terminal Value: {results['present_value_terminal_value']:.4f}")
    print(f"Enterprise Value: {results['enterprise_value']:.4f}")
    print(f"Equity Value: {results['equity_value']:.4f}")
    print(f"Value per Diluted Share: {results['value_per_diluted_share']:.4f}")
    print(
        "PV Terminal Value as Share of Enterprise Value: "
        f"{results['terminal_value_share_of_enterprise_value']:.4f}"
    )
    print_sensitivity_grid()
    reverse_dcf_uniform_growth_shift()


if __name__ == "__main__":
    main()
