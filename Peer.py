"""Peer P/E valuation template.  Edit only the INPUTS section, then run this file."""

from math import isfinite
from statistics import median


# ================================ INPUTS =================================
# Frozen case inputs as of December 31, 2024.
TARGET_NAME = "Archer-Daniels-Midland Company"
TARGET_TICKER = "ADM"
TARGET_CLOSING_PRICE = 86.91
TARGET_DILUTED_EPS = 2.23

# Each entry is (ticker, share_price, diluted_eps).  Tickers are deduplicated
# case-insensitively, and an entry matching TARGET_TICKER is excluded.
PEERS = [
    ("BG", 124.59, 4.91),
    ("INGR", 101.13, 11.18),
]
# ===========================================================================


def money(value):
    """Format only at display time; calculations always use the raw float."""
    return f"${value:,.2f}"


def valid_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and isfinite(value)
    )


def prepare_peers(target_ticker, peer_rows):
    """Return deduplicated peers, preserving the first occurrence of each ticker."""
    target_key = str(target_ticker).strip().upper()
    seen = set()
    peers = []
    for row in peer_rows:
        try:
            ticker, price, eps = row
        except (TypeError, ValueError):
            print(f"Skipped malformed peer entry: {row!r}")
            continue
        key = str(ticker).strip().upper()
        if not key:
            print(f"Skipped peer with no ticker: {row!r}")
        elif key == target_key:
            print(f"Excluded target from peers: {ticker}")
        elif key in seen:
            print(f"Excluded duplicate peer: {ticker}")
        else:
            seen.add(key)
            peers.append((str(ticker).strip(), price, eps))
    return peers


def usable_pe(peer):
    """Return raw P/E, or None when price or EPS makes it not meaningful."""
    _, price, eps = peer
    if not valid_number(price) or not valid_number(eps) or price <= 0 or eps <= 0:
        return None
    return price / eps


def print_estimate(label, multiples, target_eps):
    if not multiples:
        print(f"{label}: no estimate")
        return None
    if not valid_number(target_eps) or target_eps <= 0:
        print(f"{label}: not meaningful (target diluted EPS must be positive)")
        return None

    low, middle, high = min(multiples), median(multiples), max(multiples)
    if len(multiples) == 1:
        print(f"{label}: reference estimate (one usable peer)")
        print(f"  P/E: {middle:.6f}x")
        print(f"  Implied price: {money(middle * target_eps)}")
    else:
        print(f"{label}:")
        print(f"  P/E (min / median / max): {low:.6f}x / {middle:.6f}x / {high:.6f}x")
        print(
            "  Implied price (min / median / max): "
            f"{money(low * target_eps)} / {money(middle * target_eps)} / {money(high * target_eps)}"
        )
    return middle * target_eps


def main():
    peers = prepare_peers(TARGET_TICKER, PEERS)
    print(
        f"Target: {TARGET_NAME} ({TARGET_TICKER}) | "
        f"closing price: {money(TARGET_CLOSING_PRICE)} | "
        f"diluted EPS: {TARGET_DILUTED_EPS}"
    )
    print("\nPeer P/E calculations:")

    peer_pes = []
    for peer in peers:
        pe = usable_pe(peer)
        if pe is None:
            print(f"  {peer[0]}: not meaningful (price and diluted EPS must both be positive)")
        else:
            peer_pes.append((peer, pe))
            print(f"  {peer[0]}: {pe:.6f}x")

    print()
    if peer_pes:
        full_estimate = print_estimate(
            "Full-peer estimate", [pe for _, pe in peer_pes], TARGET_DILUTED_EPS
        )
    else:
        print("Full-peer estimate: no usable peers")
        full_estimate = None

    print("\nPeer-removal sensitivity (remaining median-implied price):")
    if not peers:
        print("  No usable peers")
        return
    for removed_peer in peers:
        remaining_pes = [pe for peer, pe in peer_pes if peer[0] != removed_peer[0]]
        removed_estimate = print_estimate(f"  Remove {removed_peer[0]}", remaining_pes, TARGET_DILUTED_EPS)
        if removed_estimate is not None and full_estimate is not None:
            # This difference uses unrounded estimates; cents are display-only.
            change = removed_estimate - full_estimate
            sign = "+" if change >= 0 else "-"
            print(f"    Change from full-peer estimate: {sign}${abs(change):,.2f}")


if __name__ == "__main__":
    main()
