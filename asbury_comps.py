"""Frozen FY2024 training comparison. Standard library only; no data fetching.

Prices: December 31, 2024 closes. EPS: subsequently reported FY2024 total
GAAP diluted EPS, on the same stock-split basis. This is retrospective.
Source: https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-04/teach-comps-worked-example.md
"""

# EDIT INPUTS HERE. Decimal strings preserve the exact entered amounts.
# Use None for missing values. Decisions: "use", "qualify", or "exclude".
# Both "use" and "qualify" enter the calculation if their numbers are valid.
TARGET = {"ticker": "ABG", "name": "Asbury Automotive",
          "price": "243.03", "eps": "21.50"}
PEERS = [
    {"ticker": "AN", "name": "AutoNation", "price": "169.84", "eps": "16.92",
     "decision": "qualify",
     "reason": "Similar vehicle sales, service and finance/insurance activities; "
               "AutoNation Finance merits a financing-risk qualification."},
    {"ticker": "GPI", "name": "Group 1 Automotive", "price": "421.48", "eps": "36.81",
     "decision": "qualify",
     "reason": "Fits franchised vehicle retail; U.K. exposure and the 2024 "
               "acquisition of 54 Inchcape dealerships qualify comparability."},
]

from decimal import Decimal, localcontext
from fractions import Fraction
from statistics import median


def positive(value):
    """Return an exact positive rational, or None for unusable inputs."""
    if value is None or isinstance(value, bool):
        return None
    try:
        number = Fraction(str(value))
    except (ValueError, TypeError, ZeroDivisionError, OverflowError):
        return None
    return number if number > 0 else None


def display(value, places):
    """Round only at display time; all valuation arithmetic uses Fraction."""
    with localcontext() as context:
        context.prec = max(50, len(str(abs(value.numerator)))
                           + len(str(value.denominator)) + places + 10)
        return format(Decimal(value.numerator) / Decimal(value.denominator),
                      f",.{places}f")


def money(value):
    return "$" + display(value, 2)


def change(value):
    return ("-" if value < 0 else "+") + money(abs(value))


def ticker(record):
    return str(record.get("ticker") or "").strip().upper()


def pe(record):
    price, eps = positive(record.get("price")), positive(record.get("eps"))
    reasons = []
    if price is None:
        reasons.append("price missing, nonnumeric, nonfinite or nonpositive")
    if eps is None:
        reasons.append("EPS missing, nonnumeric, nonfinite or nonpositive")
    return (price / eps if not reasons else None), "; ".join(reasons)


def report(target, peers):
    target_id = ticker(target)
    if not target_id:
        print("Target ticker missing: peer exclusion cannot be verified; no estimate.")
        return
    print("FY2024 retrospective P/E comparison (total GAAP diluted EPS)")
    print("Business decisions (set before reviewing valuation results):")
    seen = set()
    selected = []
    for peer in peers:
        symbol = ticker(peer)
        if not symbol:
            print("  Peer excluded: missing ticker; cannot deduplicate reliably.")
            continue
        if symbol == target_id:
            print(f"  {symbol}: excluded -- target cannot be its own peer.")
            continue
        if symbol in seen:
            print(f"  {symbol}: duplicate ignored (first occurrence retained).")
            continue
        seen.add(symbol)
        decision = str(peer.get("decision", "use")).strip().lower()
        if decision not in {"use", "qualify", "exclude"}:
            print(f"  {symbol}: excluded -- unrecognized decision {decision!r}.")
            continue
        print(f"  {symbol}: {decision} -- {peer.get('reason', 'No rationale entered.')}")
        if decision != "exclude":
            selected.append((symbol, peer))

    target_eps = positive(target.get("eps"))
    observed, issue = pe(target)
    print("\nTarget observed P/E (excluded from peer set):")
    print(f"  {target_id}: " + (display(observed, 6) + "x" if observed is not None
                              else "not meaningful -- " + issue))
    print("\nPeer calculations:")
    valid = {}
    for symbol, peer in selected:
        multiple, issue = pe(peer)
        if multiple is None:
            print(f"  {symbol} P/E and implied price: not meaningful -- {issue}.")
            continue
        valid[symbol] = multiple
        implied = (money(multiple * target_eps) if target_eps is not None
                   else "not meaningful -- invalid target EPS")
        print(f"  {symbol} P/E: {display(multiple, 6)}x; implied price: {implied}")

    print("\nFull-peer estimate:")
    full_estimate = None
    if not valid:
        print("  No usable peers; peer median, implied prices and range unavailable.")
    else:
        multiples = list(valid.values())
        middle = median(multiples)
        print(f"  Valid peers: {len(valid)}; median P/E: {display(middle, 6)}x")
        if target_eps is None:
            print("  All target implied prices: not meaningful -- invalid target EPS.")
        else:
            full_estimate = middle * target_eps
            if len(valid) == 1:
                print(f"  Reference estimate: {money(full_estimate)}; no range (one valid peer).")
            else:
                print(f"  Minimum-implied price: {money(min(multiples) * target_eps)}")
                print(f"  Median-implied price: {money(full_estimate)}")
                print(f"  Maximum-implied price: {money(max(multiples) * target_eps)}")
                print(f"  Peer-implied range: {money(min(multiples) * target_eps)}"
                      f" to {money(max(multiples) * target_eps)}")

    print("\nLeave-one-out sensitivity (change from unrounded full-peer estimate):")
    if not selected:
        print("  No included peers to remove.")
    for symbol, _ in selected:
        remaining = [multiple for name, multiple in valid.items() if name != symbol]
        if not remaining:
            print(f"  Remove {symbol}: no estimate -- no usable peers remain; change unavailable.")
        elif target_eps is None:
            print(f"  Remove {symbol}: estimate and change not meaningful -- invalid target EPS.")
        else:
            estimate = median(remaining) * target_eps
            label = "reference estimate; no range" if len(remaining) == 1 else "median-implied price"
            print(f"  Remove {symbol}: {money(estimate)} ({label}); "
                  f"change {change(estimate - full_estimate)}")
    print("\nP/E directly implies an equity price per share; no cash/debt bridge is applied.")


if __name__ == "__main__":
    report(TARGET, PEERS)
