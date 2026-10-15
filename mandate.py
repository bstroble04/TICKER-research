"""FIN 43900 Lab 13: Meridian Foundation portfolio mandate checker."""
from collections import defaultdict

RESERVE_SIZE = 100.0  # USD millions
QUARTERLY_DISTRIBUTION = 0.75  # USD millions
QUARTERS_TO_COVER = 4
LIQUIDITY_WINDOW = 5  # business days
MIN_LIQUID_SHARE = 90.0  # percent
ISSUER_LIMIT = 8.0  # percent

# name: (issuer, business days to redeem, reserve eligible)
HOLDINGS = {
    "Cash": (None, 0, True),
    "Treasury bills": ("U.S. Treasury", 1, True),
    "Treasury 10-year note": ("U.S. Treasury", 1, True),
    "Global equity index fund": ("diversified fund", 2, False),
    "Investment-grade bond fund": ("diversified fund", 3, False),
    "Private real estate fund": ("diversified fund", 90, False),
    "Acme Corp bonds": ("Acme Corp", 4, False),
    "Acme Corp stock": ("Acme Corp", 1, False),
}

CANDIDATES = {
    "A": [2, 2, 10, 60, 26, 0, 0, 0],
    "B": [1, 0, 0, 55, 20, 15, 5, 4],
    "C": [1, 1, 0, 70, 20, 0, 0, 8],
    "D": [3, 97, 0, 0, 0, 0, 0, 0],
    # Add candidate D after the AI challenge and test it yourself.
}

EXEMPT_ISSUERS = {None, "U.S. Treasury", "diversified fund"}


def check_candidate(name, weights, reserve_minimum):
    if len(weights) != len(HOLDINGS):
        raise ValueError(f"Candidate {name} must have {len(HOLDINGS)} weights")

    positions = list(zip(HOLDINGS.items(), weights))
    total = sum(weights)
    lowest = min(weights)
    reserve = sum(weight for (_, (_, _, eligible)), weight in positions if eligible)
    liquid = sum(weight for (_, (_, days, _)), weight in positions if days <= LIQUIDITY_WINDOW)

    issuer_weights = defaultdict(float)
    for (_, (issuer, _, _)), weight in positions:
        if issuer not in EXEMPT_ISSUERS:
            issuer_weights[issuer] += weight
    largest_company = max(issuer_weights.values(), default=0.0)

    checks = [
        ("Weights sum to 100%", total, abs(total - 100.0) < 1e-9),
        ("Long-only (lowest weight >= 0%)", lowest, lowest >= 0),
        (f"Reserve >= {reserve_minimum:.1f}%", reserve, reserve + 1e-9 >= reserve_minimum),
        (f"Redeemable within {LIQUIDITY_WINDOW} days >= {MIN_LIQUID_SHARE:.1f}%", liquid, liquid + 1e-9 >= MIN_LIQUID_SHARE),
        (f"Largest single company <= {ISSUER_LIMIT:.1f}%", largest_company, largest_company <= ISSUER_LIMIT + 1e-9),
    ]

    print(f"\nCandidate {name}")
    for label, value, passed in checks:
        print(f"  {label}: {value:.1f}% {'pass' if passed else 'FAIL'}")
    print("  Calendar-year loss: requires CIO clarification")
    failures = sum(not passed for _, _, passed in checks)
    print("  Verdict: " + ("passes every checkable rule" if failures == 0 else f"fails {failures} rule(s)"))


def main():
    reserve_minimum = QUARTERS_TO_COVER * QUARTERLY_DISTRIBUTION / RESERVE_SIZE * 100
    print(f"Reserve minimum: {reserve_minimum:.1f}%")
    for name, weights in CANDIDATES.items():
        check_candidate(name, weights, reserve_minimum)


if __name__ == "__main__":
    main()
