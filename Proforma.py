"""ABG five-year three-statement projection and FCFE valuation.

All monetary inputs (including the balance sheet) and the share count are in
millions. Run with: python Proforma.py
"""

YEARS = [2026, 2027, 2028, 2029, 2030]

# Opening balance sheet at December 31, 2025 (USD millions).
OPENING = {
    "cash": 40.4,
    "inventory": 2_135.8,
    "floor_plan": 2_027.0,
    "ppe": 3_070.4,
    "other_assets": 6_371.6,
    "debt": 3_572.0,
    "revolver": 0.0,
    "other_liabilities": 2_127.5,
    "equity": 3_891.7,
}

# One entry per forecast year, in the order 2026 through 2030.
ASSUMPTIONS = {
    "revenue_2025": 17_999.0,
    "growth": [0.018] * 5,
    "gross_margin": [0.1705] * 5,
    "sga_as_pct_gross_profit": [0.665, 0.655, 0.645, 0.645, 0.645],
    # Exact FY2025 historical calculation: depreciation / ending PP&E.
    "depreciation_as_pct_opening_ppe": [82.4 / 3_070.4] * 5,
    "impairment": [120.0] * 5,
    # Exact FY2025 historical calculation: inventory / cost of sales * 365.
    "inventory_days": [2_135.8 / (17_999.0 - 3_071.7) * 365] * 5,
    "floor_plan_as_pct_inventory": [2_027.0 / 2_135.8] * 5,
    "capex": [250.0] * 5,
    "debt_repayment": [150.0] * 5,
    "buyback": [150.0] * 5,
    "floor_plan_interest_rate": 0.0467,
    "debt_interest_rate": 0.0544,
    "revolver_interest_rate": 0.060,
    "tax_rate": 0.255,
    "minimum_cash": 25.0,
    "revolver_limit": 850.0,
    "cost_of_equity": 0.100,
    "terminal_growth": 0.025,
    "share_count": 17.951349,
}


def assert_balanced(year, gap, cash, minimum_cash):
    """Raise an informative error if the balance-sheet or cash check fails."""
    tolerance = 1e-6
    problems = []
    if abs(gap) > tolerance:
        problems.append(f"balance-sheet gap {gap:.6f}")
    if cash < minimum_cash - tolerance:
        problems.append(f"cash shortfall {minimum_cash - cash:.6f}")
    if problems:
        raise AssertionError(f"{year}: " + "; ".join(problems))


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
    if ASSUMPTIONS["revolver_limit"] < OPENING["revolver"]:
        raise ValueError("revolver_limit cannot be below the opening revolver balance.")
    opening_gap = (
        OPENING["cash"] + OPENING["inventory"] + OPENING["ppe"] + OPENING["other_assets"]
        - OPENING["floor_plan"] - OPENING["debt"] - OPENING["revolver"]
        - OPENING["other_liabilities"] - OPENING["equity"]
    )
    if abs(opening_gap) > 1e-6:
        raise ValueError(f"Opening balance sheet does not balance; gap {opening_gap:.6f}.")


def project():
    """Build and return the income statement, balance sheet, and cash flow."""
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
        interest = (
            opening["floor_plan"] * a["floor_plan_interest_rate"]
            + opening["debt"] * a["debt_interest_rate"]
            + opening["revolver"] * a["revolver_interest_rate"]
        )
        pretax_income = operating_income - interest
        tax = max(0.0, pretax_income) * a["tax_rate"]
        net_income = pretax_income - tax

        inventory = (revenue - gross_profit) * a["inventory_days"][index] / 365.0
        floor_plan = inventory * a["floor_plan_as_pct_inventory"][index]
        ppe = opening["ppe"] + a["capex"][index] - depreciation
        other_assets = opening["other_assets"] + 0.008 * (revenue - prior_revenue) - impairment
        debt = opening["debt"] - a["debt_repayment"][index]
        other_liabilities = opening["other_liabilities"]
        equity = opening["equity"] + net_income - a["buyback"][index]

        change_inventory = inventory - opening["inventory"]
        # The supplied working-capital assumption is 0.8% of revenue change.
        # It excludes the non-cash impairment, which is separately added back.
        change_other_working_capital = 0.008 * (revenue - prior_revenue)
        fcfe = (
            net_income + depreciation + impairment - a["capex"][index]
            - change_inventory - change_other_working_capital + (floor_plan - opening["floor_plan"])
            - a["debt_repayment"][index]
        )

        cash_before_revolver = opening["cash"] + fcfe - a["buyback"][index]
        revolver_draw = 0.0
        revolver_repayment = 0.0
        if cash_before_revolver < a["minimum_cash"]:
            revolver_draw = a["minimum_cash"] - cash_before_revolver
            if opening["revolver"] + revolver_draw > a["revolver_limit"] + 1e-6:
                excess = opening["revolver"] + revolver_draw - a["revolver_limit"]
                raise AssertionError(f"{year}: revolver limit exceeded by {excess:.6f}")
        elif cash_before_revolver > a["minimum_cash"]:
            revolver_repayment = min(opening["revolver"], cash_before_revolver - a["minimum_cash"])
        revolver = opening["revolver"] + revolver_draw - revolver_repayment
        cash = cash_before_revolver + revolver_draw - revolver_repayment

        income[year] = {
            "Revenue": revenue, "Gross profit": gross_profit, "SG&A": sga,
            "Depreciation": depreciation, "Impairment": impairment,
            "Operating income": operating_income, "Interest expense": interest,
            "Pretax income": pretax_income, "Tax expense": tax, "Net income": net_income,
        }
        balance[year] = {
            "Cash": cash, "Inventory": inventory, "PP&E": ppe, "Other assets": other_assets,
            "Total assets": cash + inventory + ppe + other_assets,
            "Floor plan": floor_plan, "Debt": debt, "Revolver": revolver,
            "Other liabilities": other_liabilities,
            "Total liabilities": floor_plan + debt + revolver + other_liabilities,
            "Equity": equity, "Total liabilities and equity": floor_plan + debt + revolver + other_liabilities + equity,
        }
        cash_flow[year] = {
            "Net income": net_income, "Depreciation": depreciation, "Impairment": impairment,
            "Capex": -a["capex"][index], "Change in inventory": -change_inventory,
            "Change in other working capital": -change_other_working_capital,
            "Change in floor plan": floor_plan - opening["floor_plan"],
            "Debt repayment": -a["debt_repayment"][index], "FCFE": fcfe,
            "Buyback": -a["buyback"][index], "Revolver draw": revolver_draw,
            "Revolver repayment": -revolver_repayment, "Net change in cash": cash - opening["cash"],
        }
        gap = balance[year]["Total assets"] - balance[year]["Total liabilities and equity"]
        checks[year] = {"Assets - liabilities - equity": gap, "Cash >= minimum": cash >= a["minimum_cash"] - 1e-6}
        assert_balanced(year, gap, cash, a["minimum_cash"])

        opening = {"cash": cash, "inventory": inventory, "floor_plan": floor_plan, "ppe": ppe,
                   "other_assets": other_assets, "debt": debt, "revolver": revolver,
                   "other_liabilities": other_liabilities, "equity": equity}
        prior_revenue = revenue
    return income, balance, cash_flow, checks


def print_table(title, statement):
    print("\n" + title)
    width = max(len(row) for year in YEARS for row in statement[year]) + 2
    print("Line item".ljust(width) + "".join(f"{year:>14}" for year in YEARS))
    rows = list(statement[YEARS[0]])
    for row in rows:
        print(row.ljust(width) + "".join(f"{statement[year][row]:>14,.1f}" for year in YEARS))


def print_checks(checks):
    print("\nChecks")
    print("Check".ljust(34) + "".join(f"{year:>14}" for year in YEARS))
    print("Assets - liabilities - equity".ljust(34) + "".join(
        f"{checks[year]['Assets - liabilities - equity']:>14,.1f}" for year in YEARS
    ))
    print("Cash at or above minimum".ljust(34) + "".join(
        f"{'PASS' if checks[year]['Cash >= minimum'] else 'FAIL':>14}" for year in YEARS
    ))


def value_equity(cash_flow):
    a = ASSUMPTIONS
    fcfe = [cash_flow[year]["FCFE"] for year in YEARS]
    present_value_fcfe = sum(flow / (1 + a["cost_of_equity"]) ** period for period, flow in enumerate(fcfe, 1))
    terminal_value = (fcfe[-1] + a["debt_repayment"][-1]) * (1 + a["terminal_growth"]) / (a["cost_of_equity"] - a["terminal_growth"])
    present_value_terminal = terminal_value / (1 + a["cost_of_equity"]) ** 5
    equity_value = present_value_fcfe + present_value_terminal
    return equity_value, present_value_terminal / equity_value, equity_value / a["share_count"]


def main():
    income, balance, cash_flow, checks = project()
    print_table("Income Statement", income)
    print_table("Balance Sheet", balance)
    print_table("Cash Flow Statement", cash_flow)
    print_checks(checks)
    equity_value, after_2030_share, value_per_share = value_equity(cash_flow)
    print("\nValuation")
    print(f"Equity value: {equity_value:,.2f}")
    print(f"Share of value after 2030: {after_2030_share:.2%}")
    print(f"Value per share: {value_per_share:,.2f}")


if __name__ == "__main__":
    main()
