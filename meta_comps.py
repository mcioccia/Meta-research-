"""Meta Lab 08. Standard library only; no downloads or packages.
See meta_lab08.md for the initial peer policy, sources and qualifications.
Fractions retain exact input precision; rounding occurs only for display.

AI-use disclosure: Prepared with OpenAI Codex assistance for research, coding,
and calculation checks. AI-generated content may contain errors. The student
is responsible for reviewing sources, calculations, and final judgments before
submission. Educational coursework; not personalized investment advice.
"""

# EDIT INPUTS HERE. USD per Class A share. None means missing/unresolved.
# Prices use January 29, 2026 close, not adjusted close or current prices.
# Each denominator is the latest full annual GAAP diluted EPS then public.
COMPARISON_DATE = "2026-01-29"
TARGET = {
    "ticker": "META", "name": "Meta Platforms Class A",
    "price": "738.31", "eps": "23.49",
    "fiscal_year_end": "2025-12-31", "eps_publication_date": "2026-01-28",
}
PEERS = [
    {
        "ticker": "GOOGL", "name": "Alphabet Class A",
        "price": "338.25", "eps": "8.05",
        "fiscal_year_end": "2024-12-31", "eps_publication_date": "2025-02-05",
        "decision": "qualify",
        "reason": "Advertising platform fit; qualify search, Cloud and other "
                  "business mix and older earnings period. Class A EPS, not consolidated EPS.",
    },
    {
        "ticker": "PINS", "name": "Pinterest Class A",
        "price": "22.35", "eps": "2.67",
        "fiscal_year_end": "2024-12-31", "eps_publication_date": "2025-02-06",
        "decision": "qualify",
        "reason": "Advertising platform fit; qualify smaller shopping-focused "
                  "business, older period and major one-time tax benefit in reported EPS.",
    },
]
# Both qualify decisions predate calculation; no policy revision was made.
# Only use/qualify peers enter the median. Missing/nonpositive input handling,
# ticker deduplication and target exclusion are retained from Lab 07.

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
    print("AI-use disclosure: Prepared with OpenAI Codex assistance for research, coding,")
    print("and calculation checks. AI-generated content may contain errors. The student")
    print("is responsible for reviewing sources, calculations, and final judgments before")
    print("submission. Educational coursework; not personalized investment advice.\n")
    target_id = ticker(target)
    if not target_id:
        print("Target ticker missing: peer exclusion cannot be verified; no estimate.")
        return
    print(f"META Lab 08: {COMPARISON_DATE} close; latest public annual GAAP diluted EPS")
    print("Price sources: opened secondary vendors; exchange confirmation unresolved.")
    print("META FY2025 versus peers FY2024; material tax and business qualifications.")
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
