"""ADM five-year three-statement projection, FCFE valuation, and sensitivities.

All monetary amounts and the share count are in millions. The model uses
FY2025 as its opening balance sheet and forecasts FY2026 through FY2030.
"""

from copy import deepcopy

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

# Keep the Lab 10 base inputs separate from the active inputs used by a run.
# Scenario runs always start from a fresh deep copy of this snapshot.
BASE_ASSUMPTIONS = deepcopy(ASSUMPTIONS)

# These are one-at-a-time sensitivity cases, not new base-case assumptions.
# The unchanged base model uses 6.75% gross margin and $1,400 million CapEx.
# Only the named driver changes in each case.
SENSITIVITY_CASES = [
    ("Gross margin: lower (6.25%)", "gross_margin", [0.0625] * 5),
    ("Gross margin: higher (7.25%)", "gross_margin", [0.0725] * 5),
    ("Annual CapEx: lower ($1,200 million)", "capex", [1_200.0] * 5),
    ("Annual CapEx: higher ($1,600 million)", "capex", [1_600.0] * 5),
]

ROUNDING_TOLERANCE = 0.01  # $0.01 million / $0.01 per share, matching displayed valuation precision.


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


def project(strict=True):
    """Build linked forecasts; strict mode preserves the Lab 10 validation behavior."""
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
            "Ending facility balance": facility,
        }
        if strict:
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


def valuation_result(cash_flow):
    """Return valuation fields without treating an ineligible terminal value as a value."""
    equity_value, terminal_value, present_value_fcfe, present_value_terminal = value_equity(cash_flow)
    if terminal_value is None:
        return {"available": False, "reason": "Terminal-year FCFE is negative.", "equity_value": None,
                "value_per_share": None}
    return {"available": True, "reason": None, "equity_value": equity_value,
            "value_per_share": equity_value / ASSUMPTIONS["share_count"],
            "terminal_value": terminal_value, "pv_fcfe": present_value_fcfe,
            "pv_terminal": present_value_terminal}


def accounting_checks_pass(checks):
    """Require every year and every existing accounting/liquidity check to pass."""
    return all(
        abs(checks[year]["Assets - liabilities - equity"]) <= 1e-6
        and checks[year]["Cash >= minimum"]
        and checks[year]["Facility <= limit"]
        for year in YEARS
    )


def failed_accounting_conditions(checks):
    """Identify each exact year and existing validation condition that failed."""
    failures = []
    for year in YEARS:
        gap = checks[year]["Assets - liabilities - equity"]
        if abs(gap) > 1e-6:
            failures.append(f"{year}E: balance-sheet gap = {gap:.6f}")
        if not checks[year]["Cash >= minimum"]:
            failures.append(f"{year}E: cash is below the ${ASSUMPTIONS['minimum_cash']:,.1f}m minimum")
        if not checks[year]["Facility <= limit"]:
            failures.append(
                f"{year}E: modeled liquidity facility exceeds its ${ASSUMPTIONS['liquidity_facility_limit']:,.1f}m limit "
                f"(ending balance ${checks[year]['Ending facility balance']:,.1f}m)"
            )
    return failures


def load_run_assumptions(run_assumptions):
    """Load an independent input copy into the existing Lab 10 model."""
    ASSUMPTIONS.clear()
    ASSUMPTIONS.update(deepcopy(run_assumptions))


def restore_base_assumptions():
    """Restore a fresh copy, so no scenario object can alter the base inputs."""
    load_run_assumptions(BASE_ASSUMPTIONS)


def run_scenario(name, assumption_name, scenario_value):
    """Run one changed input and preserve its linked statements and validation result."""
    # Each scenario starts independently from the dedicated base input set.
    run_assumptions = deepcopy(BASE_ASSUMPTIONS)
    run_assumptions[assumption_name] = deepcopy(scenario_value)
    try:
        load_run_assumptions(run_assumptions)
        # Non-strict mode retains all five years so a failed accounting check is
        # traceable in the same linked statements.  It does not make the run valid.
        income, balance, cash_flow, checks = project(strict=False)
        accounting_pass = accounting_checks_pass(checks)
        valuation = valuation_result(cash_flow) if accounting_pass else None
        return {
            "name": name, "input": assumption_name, "value": scenario_value,
            "valid": accounting_pass, "accounting_pass": accounting_pass,
            "income": income, "balance": balance, "cash_flow": cash_flow,
            "checks": checks, "valuation": valuation, "error": None,
            "validation_failures": failed_accounting_conditions(checks),
        }
    except (AssertionError, ValueError) as error:
        # The model's own checks, rather than a replacement calculation, decide invalidity.
        return {
            "name": name, "input": assumption_name, "value": scenario_value,
            "valid": False, "accounting_pass": False, "income": None, "balance": None,
            "cash_flow": None, "checks": None, "valuation": None, "error": str(error),
            "validation_failures": [str(error)],
        }
    finally:
        restore_base_assumptions()


def print_scenario_result(result):
    """Print the full statement trail for one scenario; never hide negative cash flows."""
    print(f"\nSensitivity scenario: {result['name']}")
    print(f"Changed input only: {result['input']} = {result['value']}")
    if result["error"] is not None:
        print(f"INVALID MODEL RUN — accounting/validation unavailable: {result['error']}")
        print("Valuation: UNAVAILABLE")
        return
    print_table("Income Statement", result["income"])
    print_table("Balance Sheet", result["balance"])
    print_table("Cash Flow Statement / FCFE", result["cash_flow"])
    print_checks(result["checks"])
    print("Accounting status: " + ("PASS" if result["accounting_pass"] else "INVALID MODEL RUN"))
    if not result["accounting_pass"]:
        print("Failed condition(s): " + "; ".join(result["validation_failures"]))
        print("Valuation: UNAVAILABLE — accounting/liquidity validation failed.")
    elif result["valuation"]["available"]:
        print(f"Valuation: ${result['valuation']['equity_value']:,.2f} million; "
              f"${result['valuation']['value_per_share']:,.2f} per share")
    else:
        print(f"Valuation: UNAVAILABLE — {result['valuation']['reason']}")


def format_sensitivity_input(assumption_name, value):
    """Show the actual repeated annual input once, with its units."""
    annual_value = value[0] if isinstance(value, list) else value
    if assumption_name == "gross_margin":
        return f"{annual_value:.2%}"
    if assumption_name == "capex":
        return f"${annual_value:,.0f}m annually"
    return str(annual_value)


def operating_metrics(result):
    """Return linked final-year operating outputs when statements were calculated."""
    if result["income"] is None or result["cash_flow"] is None:
        return None
    return {
        "operating_profit": result["income"][2030]["Operating income"],
        "fcfe": result["cash_flow"][2030]["FCFE"],
    }


def format_metric(value, difference=None):
    if value is None:
        return "UNAVAILABLE"
    if difference is None:
        return f"{value:,.2f}"
    return f"{value:,.2f} ({difference:+,.2f})"


def print_sensitivity_summary(baseline, scenario_results):
    """Show lower/base/higher final-year metrics and valid-run spans by driver."""
    print("\nSensitivity summary — final-year outputs")
    print("Parentheses are signed differences from base. $m applies to operating profit and FCFE.")
    base_metrics = operating_metrics(baseline)
    drivers = (("Gross margin", "gross_margin"), ("Annual CapEx", "capex"))
    for driver_label, assumption_name in drivers:
        related = [result for result in scenario_results if result["input"] == assumption_name]
        base_row = {
            **baseline, "name": "Base", "input": assumption_name,
            "value": deepcopy(BASE_ASSUMPTIONS[assumption_name]),
        }
        rows = [related[0], base_row, related[1]]
        print(f"\n{driver_label}")
        print("Scenario".ljust(34) + "Input".ljust(22) + "2030E operating profit".rjust(28)
              + "2030E FCFE".rjust(22) + "Value / share".rjust(22))
        valid_metrics = []
        for row in rows:
            metrics = operating_metrics(row)
            valuation_available = row["valid"] and row["valuation"] and row["valuation"]["available"]
            if metrics is not None and valuation_available:
                valid_metrics.append({**metrics, "value_per_share": row["valuation"]["value_per_share"]})
            operating_difference = None if metrics is None else metrics["operating_profit"] - base_metrics["operating_profit"]
            fcfe_difference = None if metrics is None else metrics["fcfe"] - base_metrics["fcfe"]
            value = row["valuation"]["value_per_share"] if valuation_available else None
            value_difference = None if value is None else value - baseline["valuation"]["value_per_share"]
            print(row["name"].ljust(34) + format_sensitivity_input(row["input"], row["value"]).ljust(22)
                  + format_metric(None if metrics is None else metrics["operating_profit"], operating_difference).rjust(28)
                  + format_metric(None if metrics is None else metrics["fcfe"], fcfe_difference).rjust(22)
                  + format_metric(value, value_difference).rjust(22))
        if len(valid_metrics) == 3:
            operating_span = max(item["operating_profit"] for item in valid_metrics) - min(item["operating_profit"] for item in valid_metrics)
            fcfe_span = max(item["fcfe"] for item in valid_metrics) - min(item["fcfe"] for item in valid_metrics)
            value_span = max(item["value_per_share"] for item in valid_metrics) - min(item["value_per_share"] for item in valid_metrics)
            print("Span (maximum − minimum)".ljust(56) + f"{operating_span:>28,.2f}{fcfe_span:>22,.2f}{value_span:>22,.2f}")
        else:
            print(f"Span: UNAVAILABLE — all three scenarios must have valid accounting and valuation ({len(valid_metrics)}/3 valid).")


def compare_base_results(baseline, restored):
    """Compare all retained numeric statement/check results to displayed-value tolerance."""
    maximum_difference = 0.0
    for baseline_statement, restored_statement in zip(baseline[:3], restored[:3]):
        for year in YEARS:
            for line_item, baseline_value in baseline_statement[year].items():
                maximum_difference = max(maximum_difference, abs(baseline_value - restored_statement[year][line_item]))
    baseline_value = valuation_result(baseline[2])
    restored_value = valuation_result(restored[2])
    if baseline_value["available"] != restored_value["available"]:
        return False, float("inf")
    if baseline_value["available"]:
        maximum_difference = max(maximum_difference, abs(
            baseline_value["value_per_share"] - restored_value["value_per_share"]
        ))
    return (maximum_difference <= ROUNDING_TOLERANCE and baseline[3] == restored[3]), maximum_difference


def run_sensitivity_analysis(baseline):
    """Run the configured OAT cases, restore inputs, and prove the base model is unchanged."""
    print("\nOne-at-a-time sensitivity analysis")
    print("Every case changes one existing input; all other base assumptions remain unchanged.")
    scenario_results = []
    for name, assumption_name, scenario_value in SENSITIVITY_CASES:
        result = run_scenario(name, assumption_name, scenario_value)
        scenario_results.append(result)
        print_scenario_result(result)

    base_income, base_balance, base_cash_flow, base_checks = baseline
    base_result = {
        "name": "Base", "input": None, "value": None,
        "valid": accounting_checks_pass(base_checks), "accounting_pass": accounting_checks_pass(base_checks),
        "income": base_income, "balance": base_balance, "cash_flow": base_cash_flow,
        "checks": base_checks, "valuation": valuation_result(base_cash_flow), "error": None,
        "validation_failures": [],
    }
    print_sensitivity_summary(base_result, scenario_results)

    # A fresh base run after all scenarios is the restoration test, not a reused result.
    restore_base_assumptions()
    restored = project()
    matches, maximum_difference = compare_base_results(baseline, restored)
    print("\nBase-assumption restoration check")
    print(f"Rerun tolerance: ${ROUNDING_TOLERANCE:.2f} million / ${ROUNDING_TOLERANCE:.2f} per share.")
    if matches:
        print(f"PASS — restored base results match the initial baseline; maximum difference: {maximum_difference:.6f}.")
    else:
        print(f"FAIL — restored base results differ by {maximum_difference:.6f}; review assumptions before using outputs.")


def main():
    # The initial baseline also uses an independent copy of the saved base inputs.
    restore_base_assumptions()
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
    else:
        print(f"Terminal value: {terminal_value:,.2f}")
        print(f"Present value of five forecast FCFEs: {present_value_fcfe:,.2f}")
        print(f"Present value of terminal value: {present_value_terminal:,.2f}")
        print(f"Total equity value: {equity_value:,.2f}")
        print(f"Value per share: {equity_value / ASSUMPTIONS['share_count']:,.2f}")
    run_sensitivity_analysis((income, balance, cash_flow, checks))


if __name__ == "__main__":
    main()
