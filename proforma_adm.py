"""ADM five-year three-statement projection and FCFE valuation.

All monetary amounts and the share count are in millions. The model uses
FY2025 as its opening balance sheet and forecasts FY2026 through FY2030.
"""

YEARS = [2026, 2027, 2028, 2029, 2030]

OPENING = {
    "cash": 1_015.0,
    "inventory": 10_369.0,
    "ppe": 11_179.0,
    "other_assets": 29_826.0,
    "debt": 8_410.0,
    "liquidity_facility": 0.0,
    "other_liabilities": 21_239.0,
    "equity": 22_740.0,
}

ASSUMPTIONS = {
    "revenue_2025": 80_269.0,
    "growth": [0.020] * 5,
    "gross_margin": [0.0675] * 5,
    "sga_as_pct_gross_profit": [0.650] * 5,
    "depreciation_as_pct_opening_ppe": [0.105] * 5,
    "impairment": [0.0] * 5,
    "inventory_days": [51.0] * 5,
    "capex": [1_400.0] * 5,
    "debt_interest_rate": 0.053,
    # Simplified pro-forma liquidity assumption; not ADM's contractual revolver.
    "minimum_cash": 500.0,
    "liquidity_facility_limit": 6_000.0,
    "liquidity_facility_interest_rate": 0.040,
    "tax_rate": 0.180,
    "dividend_per_share": 2.08,
    "buyback": [0.0] * 5,
    "cost_of_equity": 0.080,
    "terminal_growth": 0.025,
    "share_count": 484.0,
}


def assert_valid_forecast(year, gap, cash, facility):
    """Refuse valuation if the balance sheet, cash floor, or facility fails."""
    tolerance = 1e-6
    problems = []
    if abs(gap) > tolerance:
        problems.append(f"balance-sheet gap {gap:.6f}")
    if cash < ASSUMPTIONS["minimum_cash"] - tolerance:
        problems.append(f"cash shortfall {ASSUMPTIONS['minimum_cash'] - cash:.6f}")
    if facility > ASSUMPTIONS["liquidity_facility_limit"] + tolerance:
        problems.append(f"modeled liquidity limit exceeded by {facility - ASSUMPTIONS['liquidity_facility_limit']:.6f}")
    if problems:
        raise AssertionError(f"{year}: " + "; ".join(problems) + "; valuation refused.")


def require_valid_inputs():
    if len(YEARS) != 5:
        raise ValueError("This model requires exactly five forecast years.")
    for name, values in ASSUMPTIONS.items():
        if isinstance(values, list) and len(values) != len(YEARS):
            raise ValueError(f"{name} must have one value for each forecast year.")
    if ASSUMPTIONS["terminal_growth"] >= ASSUMPTIONS["cost_of_equity"]:
        raise ValueError("terminal_growth must be lower than cost_of_equity.")
    if ASSUMPTIONS["share_count"] <= 0:
        raise ValueError("share_count must be positive.")
    if ASSUMPTIONS["minimum_cash"] < 0:
        raise ValueError("minimum_cash cannot be negative.")
    if ASSUMPTIONS["liquidity_facility_limit"] < OPENING["liquidity_facility"]:
        raise ValueError("liquidity_facility_limit cannot be below the opening facility balance.")
    opening_gap = (
        OPENING["cash"] + OPENING["inventory"] + OPENING["ppe"] + OPENING["other_assets"]
        - OPENING["debt"] - OPENING["liquidity_facility"]
        - OPENING["other_liabilities"] - OPENING["equity"]
    )
    if abs(opening_gap) > 1e-6:
        raise ValueError(f"Opening balance sheet does not balance; gap {opening_gap:.6f}.")


def project():
    """Build and return linked income, balance-sheet, and cash-flow forecasts."""
    require_valid_inputs()
    a = ASSUMPTIONS
    income, balance, cash_flow, checks = {}, {}, {}, {}
    opening = OPENING.copy()
    prior_revenue = a["revenue_2025"]

    for index, year in enumerate(YEARS):
        revenue = prior_revenue * (1 + a["growth"][index])
        gross_profit = revenue * a["gross_margin"][index]
        sga = gross_profit * a["sga_as_pct_gross_profit"][index]
        depreciation = opening["ppe"] * a["depreciation_as_pct_opening_ppe"][index]
        impairment = a["impairment"][index]
        operating_income = gross_profit - sga - depreciation - impairment
        debt_interest = opening["debt"] * a["debt_interest_rate"]
        # Beginning-balance convention avoids a circular draw/interest calculation.
        facility_interest = opening["liquidity_facility"] * a["liquidity_facility_interest_rate"]
        interest = debt_interest + facility_interest
        pretax_income = operating_income - interest
        tax = max(0.0, pretax_income) * a["tax_rate"]
        net_income = pretax_income - tax

        # Commodity working capital: inventory equals cost of products sold times days held.
        cost_of_products_sold = revenue - gross_profit
        inventory = cost_of_products_sold * a["inventory_days"][index] / 365.0
        ppe = opening["ppe"] + a["capex"][index] - depreciation
        other_assets = opening["other_assets"]
        debt = opening["debt"]  # Policy: hold interest-bearing debt constant.
        other_liabilities = opening["other_liabilities"]
        dividends = a["dividend_per_share"] * a["share_count"]
        buyback = a["buyback"][index]
        equity = opening["equity"] + net_income - dividends - buyback

        change_inventory = inventory - opening["inventory"]
        # FCFE before facility borrowing is before shareholder distributions.
        fcfe_before_facility = net_income + depreciation + impairment - a["capex"][index] - change_inventory
        cash_before_facility = opening["cash"] + fcfe_before_facility - dividends - buyback
        facility_draw = 0.0
        facility_repayment = 0.0
        if cash_before_facility < a["minimum_cash"]:
            facility_draw = a["minimum_cash"] - cash_before_facility
            required_ending_facility = opening["liquidity_facility"] + facility_draw
            if required_ending_facility > a["liquidity_facility_limit"] + 1e-6:
                raise AssertionError(
                    f"{year}: required facility borrowing {facility_draw:.6f}; "
                    "modeled liquidity limit has been exceeded; valuation refused."
                )
        elif cash_before_facility > a["minimum_cash"]:
            facility_repayment = min(opening["liquidity_facility"], cash_before_facility - a["minimum_cash"])
        facility = opening["liquidity_facility"] + facility_draw - facility_repayment
        net_facility_borrowing = facility_draw - facility_repayment
        # Include net borrowing in FCFE, consistent with the Lab 9 financing architecture.
        fcfe = fcfe_before_facility + net_facility_borrowing
        net_change_in_cash = fcfe - dividends - buyback
        # Cash is deliberately calculated last from the linked cash-flow statement.
        cash = opening["cash"] + net_change_in_cash

        income[year] = {
            "Revenue": revenue, "Gross profit": gross_profit, "SG&A": sga,
            "Depreciation": depreciation, "Impairment": impairment,
            "Operating income": operating_income, "Existing debt interest": debt_interest,
            "Liquidity-facility interest": facility_interest, "Interest expense": interest,
            "Pretax income": pretax_income, "Tax expense": tax, "Net income": net_income,
        }
        balance[year] = {
            "Cash": cash, "Inventory (commodity working capital)": inventory,
            "PP&E": ppe, "Other assets": other_assets,
            "Total assets": cash + inventory + ppe + other_assets,
            "Interest-bearing debt": debt, "Modeled liquidity facility": facility,
            "Other liabilities": other_liabilities,
            "Total liabilities": debt + facility + other_liabilities,
            "Equity": equity, "Total liabilities and equity": debt + facility + other_liabilities + equity,
        }
        cash_flow[year] = {
            "Net income": net_income, "Depreciation": depreciation, "Impairment": impairment,
            "Capex": -a["capex"][index], "Change in inventory": -change_inventory,
            "FCFE before facility borrowing": fcfe_before_facility,
            "Liquidity-facility draw": facility_draw,
            "Liquidity-facility repayment": -facility_repayment,
            "Net facility borrowing": net_facility_borrowing, "FCFE": fcfe,
            "Dividends": -dividends, "Share repurchases": -buyback,
            "Net change in cash": net_change_in_cash,
        }
        gap = balance[year]["Total assets"] - balance[year]["Total liabilities and equity"]
        checks[year] = {
            "Assets - liabilities - equity": gap,
            "Cash >= minimum": cash >= a["minimum_cash"] - 1e-6,
            "Facility <= limit": facility <= a["liquidity_facility_limit"] + 1e-6,
        }
        assert_valid_forecast(year, gap, cash, facility)

        opening = {
            "cash": cash, "inventory": inventory, "ppe": ppe,
            "other_assets": other_assets, "debt": debt,
            "liquidity_facility": facility, "other_liabilities": other_liabilities,
            "equity": equity,
        }
        prior_revenue = revenue
    return income, balance, cash_flow, checks


def print_table(title, statement):
    print("\n" + title)
    width = max(len(row) for year in YEARS for row in statement[year]) + 2
    print("Line item".ljust(width) + "".join(f"{year}E".rjust(14) for year in YEARS))
    for row in statement[YEARS[0]]:
        print(row.ljust(width) + "".join(f"{statement[year][row]:>14,.1f}" for year in YEARS))


def print_checks(checks):
    print("\nChecks")
    print("Check".ljust(34) + "".join(f"{year}E".rjust(14) for year in YEARS))
    print("Assets - liabilities - equity".ljust(34) + "".join(
        f"{checks[year]['Assets - liabilities - equity']:>14,.1f}" for year in YEARS
    ))
    print("Cash at or above minimum".ljust(34) + "".join(
        f"{'PASS' if checks[year]['Cash >= minimum'] else 'FAIL':>14}" for year in YEARS
    ))
    print("Facility at or below limit".ljust(34) + "".join(
        f"{'PASS' if checks[year]['Facility <= limit'] else 'FAIL':>14}" for year in YEARS
    ))


def value_equity(cash_flow):
    """Value FCFE only when the Gordon-growth terminal input is valid."""
    a = ASSUMPTIONS
    fcfe = [cash_flow[year]["FCFE"] for year in YEARS]
    present_value_fcfe = sum(flow / (1 + a["cost_of_equity"]) ** period for period, flow in enumerate(fcfe, 1))
    if fcfe[-1] <= 0:
        return present_value_fcfe, None, None, None
    terminal_value = fcfe[-1] * (1 + a["terminal_growth"]) / (a["cost_of_equity"] - a["terminal_growth"])
    present_value_terminal = terminal_value / (1 + a["cost_of_equity"]) ** 5
    equity_value = present_value_fcfe + present_value_terminal
    return equity_value, terminal_value, present_value_fcfe, present_value_terminal


def main():
    try:
        income, balance, cash_flow, checks = project()
    except (AssertionError, ValueError) as error:
        print(f"Balance-sheet validation failed: {error}")
        print("Valuation refused.")
        return
    print_table("Income Statement", income)
    print_table("Balance Sheet", balance)
    print_table("Cash Flow Statement / FCFE", cash_flow)
    print_checks(checks)
    equity_value, terminal_value, present_value_fcfe, present_value_terminal = value_equity(cash_flow)
    print("\nValuation")
    if terminal_value is None:
        print("Terminal value not calculated because terminal-year FCFE is negative.")
        print(f"Present value of five forecast FCFEs: {equity_value:,.2f}")
        print("Equity value and value per share: not calculated without a terminal value.")
        return
    print(f"Terminal value: {terminal_value:,.2f}")
    print(f"Present value of five forecast FCFEs: {present_value_fcfe:,.2f}")
    print(f"Present value of terminal value: {present_value_terminal:,.2f}")
    print(f"Total equity value: {equity_value:,.2f}")
    print(f"Value per share: {equity_value / ASSUMPTIONS['share_count']:,.2f}")


if __name__ == "__main__":
    main()
