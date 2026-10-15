"""Lab 13: Meridian Foundation Reserve mandate checker (standard library only).

AI-use disclosure: Prepared with OpenAI Codex assistance. Verify the code,
inputs and conclusions. Educational purposes only. Not financial or investment
advice, and not a recommendation to buy, sell or hold any security.
"""

import argparse
import copy
import math


# EDITABLE INPUTS: money is USD millions; weights and limits are percentages.
RESERVE_SIZE = 100.0
QUARTERLY_DISTRIBUTION = 0.75
QUARTERS_TO_COVER = 4
LIQUIDITY_WINDOW = 5  # business days
MINIMUM_LIQUID_SHARE = 90.0
ISSUER_LIMIT = 8.0
EXEMPT_ISSUERS = {"none", "U.S. Treasury", "diversified fund"}

HOLDINGS = {
    "Cash": {"issuer": "none", "days": 0, "reserve_eligible": True},
    "Treasury bills": {
        "issuer": "U.S. Treasury", "days": 1, "reserve_eligible": True,
    },
    "Treasury 10-year note": {
        "issuer": "U.S. Treasury", "days": 1, "reserve_eligible": True,
    },
    "Global equity index fund": {
        "issuer": "diversified fund", "days": 2, "reserve_eligible": False,
    },
    "Investment-grade bond fund": {
        "issuer": "diversified fund", "days": 3, "reserve_eligible": False,
    },
    "Private real estate fund": {
        "issuer": "diversified fund", "days": 90, "reserve_eligible": False,
    },
    "Acme Corp bonds": {
        "issuer": "Acme Corp", "days": 4, "reserve_eligible": False,
    },
    "Acme Corp stock": {
        "issuer": "Acme Corp", "days": 1, "reserve_eligible": False,
    },
}

CANDIDATES = {
    "A": {
        "Cash": 2, "Treasury bills": 2, "Treasury 10-year note": 10,
        "Global equity index fund": 60, "Investment-grade bond fund": 26,
        "Private real estate fund": 0, "Acme Corp bonds": 0,
        "Acme Corp stock": 0,
    },
    "B": {
        "Cash": 1, "Treasury bills": 0, "Treasury 10-year note": 0,
        "Global equity index fund": 55, "Investment-grade bond fund": 20,
        "Private real estate fund": 15, "Acme Corp bonds": 5,
        "Acme Corp stock": 4,
    },
    "C": {
        "Cash": 1, "Treasury bills": 1, "Treasury 10-year note": 0,
        "Global equity index fund": 70, "Investment-grade bond fund": 20,
        "Private real estate fund": 0, "Acme Corp bonds": 0,
        "Acme Corp stock": 8,
    },
    # AI-proposed attack, using only a holding permitted by the case table.
    "D": {
        "Cash": 0, "Treasury bills": 0, "Treasury 10-year note": 100,
        "Global equity index fund": 0, "Investment-grade bond fund": 0,
        "Private real estate fund": 0, "Acme Corp bonds": 0,
        "Acme Corp stock": 0,
    },
}

AI_NOTICE = "AI-use disclosure: Prepared with OpenAI Codex assistance; verify results."
EDUCATIONAL_NOTICE = (
    "Educational purposes only. Not financial or investment advice, "
    "and not a recommendation to buy, sell or hold any security."
)
TOLERANCE = 1e-9  # For percentage-sum rounding, not for ignoring negative weights.


def validate_inputs():
    """Reject malformed inputs; an actual negative weight must reach the checker."""
    numbers = (RESERVE_SIZE, QUARTERLY_DISTRIBUTION, MINIMUM_LIQUID_SHARE, ISSUER_LIMIT)
    if not all(math.isfinite(x) for x in numbers):
        raise ValueError("Reserve inputs and limits must be finite numbers.")
    if RESERVE_SIZE <= 0 or QUARTERLY_DISTRIBUTION < 0:
        raise ValueError("Reserve size must be positive; distributions cannot be negative.")
    if type(QUARTERS_TO_COVER) is not int or QUARTERS_TO_COVER <= 0:
        raise ValueError("Quarters to cover must be a positive integer.")
    if type(LIQUIDITY_WINDOW) is not int or LIQUIDITY_WINDOW < 0:
        raise ValueError("Liquidity window must be a nonnegative number of business days.")
    if not (0 <= MINIMUM_LIQUID_SHARE <= 100 and 0 <= ISSUER_LIMIT <= 100):
        raise ValueError("Percentage limits must be between 0 and 100.")
    if not HOLDINGS:
        raise ValueError("The holdings table cannot be empty.")
    for name, holding in HOLDINGS.items():
        if not isinstance(holding["issuer"], str) or not holding["issuer"]:
            raise ValueError(f"{name}: supply an issuer.")
        if type(holding["days"]) is not int or holding["days"] < 0:
            raise ValueError(f"{name}: redemption days must be a nonnegative integer.")
        if type(holding["reserve_eligible"]) is not bool:
            raise ValueError(f"{name}: reserve eligibility must be True or False.")


def reserve_minimum():
    return QUARTERS_TO_COVER * QUARTERLY_DISTRIBUTION / RESERVE_SIZE * 100


def check_candidate(weights):
    validate_inputs()
    if set(weights) != set(HOLDINGS):
        raise ValueError("Candidate must have exactly one weight for each listed holding.")
    if not all(isinstance(w, (int, float)) and not isinstance(w, bool)
               and math.isfinite(w) for w in weights.values()):
        raise ValueError("Weights must be finite numeric percentages.")

    total = sum(weights.values())
    lowest = min(weights.values())
    reserve_weight = sum(w for name, w in weights.items()
                         if HOLDINGS[name]["reserve_eligible"])
    liquid_weight = sum(w for name, w in weights.items()
                        if HOLDINGS[name]["days"] <= LIQUIDITY_WINDOW)
    company_weights = {}
    for name, weight in weights.items():
        issuer = HOLDINGS[name]["issuer"]
        if issuer not in EXEMPT_ISSUERS:
            company_weights[issuer] = company_weights.get(issuer, 0.0) + weight
    largest_company = max(company_weights.values(), default=0.0)

    # Each item is (label, measured percentage, passes).
    checks = [
        ("Weights sum to 100", total,
         math.isclose(total, 100.0, rel_tol=0.0, abs_tol=TOLERANCE)),
        ("Long-only (lowest weight)", lowest, lowest >= 0),
        (f"Reserve >= {reserve_minimum():.1f}%", reserve_weight,
         reserve_weight >= reserve_minimum() - TOLERANCE),
        (f"Redeemable in {LIQUIDITY_WINDOW} days >= {MINIMUM_LIQUID_SHARE:.1f}%",
         liquid_weight, liquid_weight >= MINIMUM_LIQUID_SHARE - TOLERANCE),
        (f"Largest single company <= {ISSUER_LIMIT:.1f}%", largest_company,
         largest_company <= ISSUER_LIMIT + TOLERANCE),
    ]
    return checks


def print_candidate(name, weights):
    checks = check_candidate(weights)
    print(f"\nCandidate {name}")
    for label, measured, passed in checks:
        print(f"  {label}: {measured:.1f} {'pass' if passed else 'FAIL'}")
    print("  Calendar-year loss: requires CIO clarification")
    failures = sum(not passed for _, _, passed in checks)
    verdict = "passes every checkable rule" if failures == 0 else f"fails {failures} rule(s)"
    print(f"  Verdict: {verdict}")


def self_test():
    """Known answers are test expectations only; displayed results are computed."""
    expected = {
        "A": ([100, 0, 14, 100, 0], [True, True, True, True, True]),
        "B": ([100, 0, 1, 85, 9], [True, True, False, False, False]),
        "C": ([100, 0, 2, 100, 8], [True, True, False, True, True]),
        "D": ([100, 0, 100, 100, 0], [True, True, True, True, True]),
    }
    assert math.isclose(reserve_minimum(), 3.0, rel_tol=0, abs_tol=TOLERANCE)
    for name, (measurements, verdicts) in expected.items():
        actual = check_candidate(CANDIDATES[name])
        assert all(math.isclose(row[1], value, rel_tol=0, abs_tol=TOLERANCE)
                   for row, value in zip(actual, measurements)), name
        assert [row[2] for row in actual] == verdicts, name

    original = copy.deepcopy(CANDIDATES)
    probe = copy.deepcopy(CANDIDATES["A"])
    probe["Cash"] = -2
    probe["Global equity index fund"] = 64
    checked = check_candidate(probe)
    assert [row[1] for row in checked] == [100, -2, 10, 100, 0]
    assert [row[2] for row in checked] == [True, False, True, True, True]
    assert CANDIDATES == original, "Probe changed the saved base inputs."
    # Additional issuer and liquidity boundaries: keep total weight at 100.
    over_limit = copy.deepcopy(CANDIDATES["C"])
    over_limit["Acme Corp stock"] += 0.1
    over_limit["Global equity index fund"] -= 0.1
    assert not check_candidate(over_limit)[4][2]
    boundary = {name: 0 for name in HOLDINGS}
    boundary["Cash"] = 3
    boundary["Global equity index fund"] = 87
    boundary["Private real estate fund"] = 10
    assert all(row[2] for row in check_candidate(boundary))
    boundary["Global equity index fund"] -= 0.1
    boundary["Private real estate fund"] += 0.1
    assert not check_candidate(boundary)[3][2]
    print("\nSELF-TEST PASS: known answers A-C; D; negative-weight probe; "
          "issuer/liquidity boundaries; base inputs unchanged.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", action="store_true", help="Show the negative-weight A probe and restored A.")
    parser.add_argument("--self-test", action="store_true", help="Check the supplied case's known answers and boundaries.")
    args = parser.parse_args()
    validate_inputs()
    print(f"Reserve minimum: {reserve_minimum():.1f}% of the portfolio")
    print(AI_NOTICE)
    print(EDUCATIONAL_NOTICE)
    if args.probe:
        probe = copy.deepcopy(CANDIDATES["A"])
        probe["Cash"] = -2
        probe["Global equity index fund"] = 64
        print_candidate("A (temporary negative-weight probe)", probe)
        print_candidate("A (restored base; saved inputs unchanged)", CANDIDATES["A"])
    else:
        for name, weights in CANDIDATES.items():
            print_candidate(name, weights)
    print("\nScope: these are static checks, not full mandate approval. Turnover and "
          "rebalancing need trade/history data; return and loss outcomes are not tested.")
    if args.self_test:
        self_test()


if __name__ == "__main__":
    main()
