"""FIN 43900 Lab 16 — Provenance Gate.

Change DECISION_DATE to reproduce the panel that would have been available on
another decision date.  This program uses only the Python standard library.
"""

from collections import defaultdict
from datetime import date


# Editable decision date for the as-of panel.
DECISION_DATE = "2026-03-31"

# Training data: (original row, ticker, month measured, published on, index).
TRAINING_DATA = [
    (1, "AAA", "2026-01", "2026-02-10", 101.0),
    (2, "AAA", "2026-02", "2026-03-10", 104.0),
    (3, "AAA", "2026-03", "2026-04-10", 109.0),
    (4, "AAA", "2026-02", "2026-03-25", 103.0),
    (5, "BBB", "2026-01", "2026-02-10", 98.0),
    (6, "BBB", "2026-02", "2026-03-10", 97.0),
    (7, "BBB", "2026-02", "2026-03-10", 97.0),
    (8, "BBB", "2026-03", "2026-04-10", 92.0),
    (9, "CCC", "2026-01", "2026-02-10", 110.0),
    (10, "CCC", "2026-02", "2026-04-05", 112.0),
    (11, "", "2026-02", "2026-03-10", 99.0),
    (12, "CCC", "2026-02", "2026-03-10", 111.0),
]


def parse_rows(data):
    """Convert input strings to dates once, keeping each original row number."""
    return [
        {
            "row": row_number,
            "ticker": ticker,
            "month": month,
            "published": date.fromisoformat(published),
            "index": index_value,
        }
        for row_number, ticker, month, published, index_value in data
    ]


def remove_exact_duplicates(rows):
    """Keep the first occurrence of identical data, excluding original row number."""
    kept, removed, seen = [], [], set()
    for row in rows:
        signature = (row["ticker"], row["month"], row["published"], row["index"])
        if signature in seen:
            removed.append(row)
        else:
            seen.add(signature)
            kept.append(row)
    return kept, removed


def keep_latest_revision(rows):
    """For every ticker/month, retain the row with the latest publication date."""
    latest = {}
    for row in rows:
        key = (row["ticker"], row["month"])
        if key not in latest or row["published"] > latest[key]["published"]:
            latest[key] = row
    kept = sorted(latest.values(), key=lambda row: row["row"])
    kept_numbers = {row["row"] for row in kept}
    removed = [row for row in rows if row["row"] not in kept_numbers]
    return kept, removed


def format_rows(rows):
    return ", ".join(str(row["row"]) for row in rows) or "none"


def calculate_signals(rows):
    """Return each ticker's final observed month and percent change from prior month."""
    by_ticker = defaultdict(list)
    for row in rows:
        by_ticker[row["ticker"]].append(row)

    signals = {}
    for ticker, ticker_rows in by_ticker.items():
        ticker_rows.sort(key=lambda row: row["month"])
        previous, latest = ticker_rows[-2:]
        change = (latest["index"] / previous["index"] - 1) * 100
        signals[ticker] = (latest, change)
    return signals


def month_name(month):
    return date.fromisoformat(f"{month}-01").strftime("%B")


def print_signals(label, signals, revised_rows=None):
    print(f"{label} signals:")
    for ticker in sorted(signals):
        latest, change = signals[ticker]
        suffix = ""
        if revised_rows is not None and (ticker, latest["month"]) in revised_rows:
            suffix = ", revised"
        print(f"{ticker}: {change:+.2f}% ({month_name(latest['month'])}{suffix})")


def main():
    decision_date = date.fromisoformat(DECISION_DATE)
    rows = parse_rows(TRAINING_DATA)

    # Rule 1: quarantine records that cannot be assigned to a ticker.
    rows, missing_ticker = ([row for row in rows if row["ticker"]],
                            [row for row in rows if not row["ticker"]])

    # Rule 2: remove duplicate observations, without using their row numbers.
    rows, exact_duplicate = remove_exact_duplicates(rows)

    # Rule 3: exclude publications not yet available on the decision date.
    rows, published_after = (
        [row for row in rows if row["published"] <= decision_date],
        [row for row in rows if row["published"] > decision_date],
    )

    # Rule 4: within a ticker/month, retain the newest available revision.
    asof_panel, older_revision = keep_latest_revision(rows)

    # Naive panel applies the same data-quality rules but deliberately ignores Rule 3.
    quality_rows = [row for row in parse_rows(TRAINING_DATA) if row["ticker"]]
    quality_rows, _ = remove_exact_duplicates(quality_rows)
    naive_panel, _ = keep_latest_revision(quality_rows)
    naive_revisions = {
        (row["ticker"], row["month"])
        for row in naive_panel
        if any(
            other["ticker"] == row["ticker"]
            and other["month"] == row["month"]
            and other["row"] != row["row"]
            for other in quality_rows
        )
    }

    print(f"Decision date: {DECISION_DATE}")
    print("Row funnel:")
    print(f"Missing ticker: {format_rows(missing_ticker)}")
    print(f"Exact duplicate: {format_rows(exact_duplicate)}")
    print(f"Published after decision date: {format_rows(published_after)}")
    print(f"Older revision: {format_rows(older_revision)}")
    print("Remaining as-of panel:")
    for row in asof_panel:
        print(
            f"Row {row['row']}: {row['ticker']} {row['month']} "
            f"published {row['published'].isoformat()} index {row['index']:.1f}"
        )

    print_signals("As-of", calculate_signals(asof_panel))
    print_signals("Naive", calculate_signals(naive_panel), naive_revisions)


if __name__ == "__main__":
    main()
