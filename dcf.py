# Editable inputs (USD amounts and share counts are in millions).
STARTING_FCFF = 100.0
YEARLY_GROWTH_RATES = [0.08, 0.06, 0.05, 0.04, 0.03]
WACC = 0.10
TERMINAL_GROWTH = 0.03
NON_OPERATING_CASH = 50.0
DEBT = 300.0
DILUTED_SHARES = 50.0


def main():
    """Calculate a five-year FCFF discounted cash flow valuation."""
    if TERMINAL_GROWTH >= WACC:
        raise SystemExit(
            "Error: terminal growth must be less than WACC for the Gordon-growth formula."
        )

    if len(YEARLY_GROWTH_RATES) != 5:
        raise SystemExit("Error: provide exactly five yearly growth rates.")
    if DILUTED_SHARES <= 0:
        raise SystemExit("Error: diluted shares must be greater than zero.")

    fcff_by_year = []
    fcff = STARTING_FCFF
    for growth_rate in YEARLY_GROWTH_RATES:
        fcff *= 1 + growth_rate
        fcff_by_year.append(fcff)

    present_value_explicit_fcff = sum(
        cash_flow / (1 + WACC) ** year
        for year, cash_flow in enumerate(fcff_by_year, start=1)
    )
    terminal_value_year_5 = (
        fcff_by_year[-1] * (1 + TERMINAL_GROWTH) / (WACC - TERMINAL_GROWTH)
    )
    present_value_terminal_value = terminal_value_year_5 / (1 + WACC) ** 5
    enterprise_value = present_value_explicit_fcff + present_value_terminal_value
    equity_value = enterprise_value + NON_OPERATING_CASH - DEBT
    value_per_diluted_share = equity_value / DILUTED_SHARES
    terminal_value_share_of_enterprise_value = (
        present_value_terminal_value / enterprise_value
    )

    for year, cash_flow in enumerate(fcff_by_year, start=1):
        print(f"FCFF Year {year}: {cash_flow:.4f}")
    print(f"Present Value of Explicit FCFF: {present_value_explicit_fcff:.4f}")
    print(f"Terminal Value at Year 5: {terminal_value_year_5:.4f}")
    print(f"Present Value of Terminal Value: {present_value_terminal_value:.4f}")
    print(f"Enterprise Value: {enterprise_value:.4f}")
    print(f"Equity Value: {equity_value:.4f}")
    print(f"Value per Diluted Share: {value_per_diluted_share:.4f}")
    print(
        "PV Terminal Value as Share of Enterprise Value: "
        f"{terminal_value_share_of_enterprise_value:.4f}"
    )


if __name__ == "__main__":
    main()
