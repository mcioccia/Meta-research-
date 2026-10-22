"""Lab 14 portfolio engine: course-authored training inputs, not market estimates.

AI-use disclosure: Prepared with OpenAI Codex assistance; verify all results.
Educational purposes only. Not financial or investment advice.
"""

import argparse
import copy
import math
import csv
import io
import statistics
from datetime import date
from pathlib import Path


# EDITABLE INPUTS: annual returns/volatilities and weights use DECIMALS.
# Keep this sleeve order in the correlation matrix and benchmark weights.
SLEEVES = [
    {"name": "Treasury bills", "return": 0.035, "volatility": 0.005,
     "reserve_eligible": True},
    {"name": "Treasury 10-year note", "return": 0.043, "volatility": 0.070,
     "reserve_eligible": True},
    {"name": "Investment-grade bond fund", "return": 0.050, "volatility": 0.060,
     "reserve_eligible": False},
    {"name": "Global equity index fund", "return": 0.080, "volatility": 0.160,
     "reserve_eligible": False},
]
CORRELATIONS = [
    [1.00, 0.10, 0.05, 0.00],
    [0.10, 1.00, 0.80, -0.10],
    [0.05, 0.80, 1.00, 0.25],
    [0.00, -0.10, 0.25, 1.00],
]
CPI_ESTIMATE = 0.025  # Labelled course estimate, not an observed CPI reading.
REAL_RETURN_OBJECTIVE = 0.040
OBJECTIVE_RETURN = CPI_ESTIMATE + REAL_RETURN_OBJECTIVE  # Course convention.
BENCHMARK_WEIGHTS = [0.0, 0.0, 0.4, 0.6]

AI_NOTICE = "AI-use disclosure: Prepared with OpenAI Codex assistance; verify results."
EDUCATIONAL_NOTICE = "Educational purposes only. Not financial or investment advice."
TOLERANCE = 1e-12


def validate_correlations(correlations, count):
    """Refuse invalid entries and asymmetric tables before calculations."""
    if len(correlations) != count or any(len(row) != count for row in correlations):
        raise ValueError(f"Correlation table must be {count} by {count}.")
    for i in range(count):
        for j in range(count):
            value = correlations[i][j]
            if not math.isfinite(value) or not -1 <= value <= 1:
                raise ValueError(
                    f"Correlation [{i + 1},{j + 1}] = {value}: must be within -1 to 1."
                )
    for i in range(count):
        if not math.isclose(correlations[i][i], 1.0, abs_tol=TOLERANCE, rel_tol=0):
            raise ValueError(f"Correlation diagonal [{i + 1},{i + 1}] must be 1.")
        for j in range(i):
            if not math.isclose(correlations[i][j], correlations[j][i],
                                abs_tol=TOLERANCE, rel_tol=0):
                raise ValueError(
                    f"Correlation table is not symmetric at "
                    f"[{i + 1},{j + 1}] and [{j + 1},{i + 1}]."
                )


def build_covariance_matrix(volatilities, correlations):
    validate_correlations(correlations, len(volatilities))
    if not volatilities or any(not math.isfinite(v) or v <= 0 for v in volatilities):
        raise ValueError("Volatilities must be finite and positive.")
    return [
        [correlations[i][j] * volatilities[i] * volatilities[j]
         for j in range(len(volatilities))]
        for i in range(len(volatilities))
    ]


def validate_weights(weights, count):
    if len(weights) != count or any(not math.isfinite(w) or w < 0 for w in weights):
        raise ValueError("Supply one finite, nonnegative weight for each sleeve.")
    if not math.isclose(sum(weights), 1.0, abs_tol=TOLERANCE, rel_tol=0):
        raise ValueError("Decimal weights must sum to 1.")


def equal_weights(count):
    if count <= 0:
        raise ValueError("At least one sleeve is required.")
    return [1.0 / count] * count


def inverse_volatility_weights(volatilities):
    if not volatilities or any(not math.isfinite(v) or v <= 0 for v in volatilities):
        raise ValueError("Inverse volatility requires positive, finite volatilities.")
    inverse = [1.0 / v for v in volatilities]
    total = sum(inverse)
    return [value / total for value in inverse]


def portfolio_return(weights, expected_returns):
    validate_weights(weights, len(expected_returns))
    if any(not math.isfinite(r) for r in expected_returns):
        raise ValueError("Expected returns must be finite.")
    return sum(w * r for w, r in zip(weights, expected_returns))


def portfolio_volatility(weights, covariance):
    validate_weights(weights, len(covariance))
    if any(len(row) != len(weights) for row in covariance):
        raise ValueError("Covariance matrix dimensions must match the weights.")
    # Sum every ordered pair, including both (i,j) and (j,i).
    variance = sum(
        weights[i] * weights[j] * covariance[i][j]
        for i in range(len(weights))
        for j in range(len(weights))
    )
    if not math.isfinite(variance) or variance < -TOLERANCE:
        raise ValueError("Invalid portfolio variance; review the covariance inputs.")
    return math.sqrt(max(0.0, variance))


def reserve_eligible_weight(weights, sleeves):
    validate_weights(weights, len(sleeves))
    return sum(w for w, sleeve in zip(weights, sleeves) if sleeve["reserve_eligible"])


def meets_objective(expected_return, objective):
    if not math.isfinite(objective):
        raise ValueError("Objective return must be finite.")
    return expected_return >= objective - TOLERANCE


def evaluate_portfolios(sleeves, correlations, benchmark_weights, objective):
    """Reusable entry point; all inputs are explicit, with no printing or mutation."""
    volatilities = [s["volatility"] for s in sleeves]
    returns = [s["return"] for s in sleeves]
    covariance = build_covariance_matrix(volatilities, correlations)
    portfolios = {
        "Benchmark": list(benchmark_weights),
        "Equal weight": equal_weights(len(sleeves)),
        "Inverse volatility": inverse_volatility_weights(volatilities),
    }
    results = {}
    for name, weights in portfolios.items():
        expected_return = portfolio_return(weights, returns)
        results[name] = {
            "weights": weights,
            "return": expected_return,
            "volatility": portfolio_volatility(weights, covariance),
            "reserve": reserve_eligible_weight(weights, sleeves),
            "meets_objective": meets_objective(expected_return, objective),
        }
    return results


def print_results(results, sleeves, objective):
    print(f"\nAnnual expected-return objective: {objective * 100:.2f}%")
    print("Weights order: " + " / ".join(s["name"] for s in sleeves))
    for name, result in results.items():
        print(f"\n{name}")
        print("  Weights (%): " + " / ".join(f"{w * 100:.1f}" for w in result["weights"]))
        print(f"  Expected return: {result['return'] * 100:.2f}%")
        print(f"  Volatility: {result['volatility'] * 100:.2f}%")
        print(f"  Reserve-eligible weight: {result['reserve'] * 100:.1f}%")
        print(f"  Meets objective: {'yes' if result['meets_objective'] else 'no'}")


def self_test():
    """Known-answer and deliberate-break tests; never change saved inputs."""
    original = copy.deepcopy(CORRELATIONS)
    base = evaluate_portfolios(SLEEVES, CORRELATIONS, BENCHMARK_WEIGHTS, OBJECTIVE_RETURN)
    expected = {
        "Benchmark": (["0.0", "0.0", "40.0", "60.0"], "6.80", "10.46", "0.0", True),
        "Equal weight": (["25.0"] * 4, "5.20", "5.21", "50.0", False),
        "Inverse volatility": (["84.3", "6.0", "7.0", "2.6"], "3.77", "1.05", "90.3", False),
    }
    for name, result in base.items():
        actual = (
            [f"{w * 100:.1f}" for w in result["weights"]],
            f"{result['return'] * 100:.2f}", f"{result['volatility'] * 100:.2f}",
            f"{result['reserve'] * 100:.1f}", result["meets_objective"],
        )
        assert actual == expected[name], (name, actual)
    print("\nPASS: every displayed baseline value matches the course answer.")

    probe = copy.deepcopy(CORRELATIONS)
    probe[2][3] = probe[3][2] = 0.50
    changed = evaluate_portfolios(SLEEVES, probe, BENCHMARK_WEIGHTS, OBJECTIVE_RETURN)
    volatility = changed["Benchmark"]["volatility"] * 100
    assert f"{volatility:.2f}" == "11.00"
    print(f"PASS: IG-equity correlation 0.50 in both cells -> benchmark volatility {volatility:.2f}%.")

    for label, matrix, message in [
        ("out-of-range correlation", copy.deepcopy(CORRELATIONS), "within -1 to 1"),
        ("asymmetric correlation", copy.deepcopy(CORRELATIONS), "not symmetric"),
    ]:
        matrix[2][3] = 1.3 if "out-of-range" in label else 0.50
        try:
            evaluate_portfolios(SLEEVES, matrix, BENCHMARK_WEIGHTS, OBJECTIVE_RETURN)
        except ValueError as error:
            assert message in str(error), str(error)
            print(f"PASS: refused {label}: {error}")
        else:
            raise AssertionError(f"Did not refuse {label}.")
    assert CORRELATIONS == original
    restored = evaluate_portfolios(SLEEVES, CORRELATIONS, BENCHMARK_WEIGHTS, OBJECTIVE_RETURN)
    assert restored == base
    print("PASS: original inputs unchanged; restored base rerun matches exactly.")


def search_portfolios(sleeves, correlations, objective, reserve_minimum):
    """Exhaust every long-only 5-point mix; return the lowest volatility or None.

    Decimal inputs; no borrowing. A tie keeps the first mix in sleeve order.
    This is a grid minimum, not a continuous optimum or full mandate approval.
    """
    count = len(sleeves)
    if not 1 <= count <= 6:
        raise ValueError("The search supports one to six assets (coursework asks for 3-6 funds).")
    if not math.isfinite(objective):
        raise ValueError("Objective must be finite.")
    if not math.isfinite(reserve_minimum) or not 0 <= reserve_minimum <= 1:
        raise ValueError("Reserve minimum must be between 0 and 1.")
    returns = [s["return"] for s in sleeves]
    if any(not math.isfinite(r) for r in returns):
        raise ValueError("Expected returns must be finite.")
    covariance = build_covariance_matrix([s["volatility"] for s in sleeves], correlations)

    def allocations(remaining, places, prefix=()):
        if places == 1:
            yield prefix + (remaining,)
        else:
            for units in range(remaining + 1):
                yield from allocations(remaining - units, places - 1, prefix + (units,))

    best = None
    tried = feasible = 0
    for units in allocations(20, count):
        tried += 1
        weights = [unit / 20 for unit in units]
        expected = portfolio_return(weights, returns)
        reserve = reserve_eligible_weight(weights, sleeves)
        if not meets_objective(expected, objective) or reserve < reserve_minimum - TOLERANCE:
            continue
        feasible += 1
        volatility = portfolio_volatility(weights, covariance)
        if best is None or volatility < best["volatility"] - TOLERANCE:
            best = {"weights": weights, "return": expected,
                    "volatility": volatility, "reserve": reserve}
    if best is not None:
        best.update(tried=tried, feasible=feasible)
    return best


def estimate_from_csv(source, last_36_months=False):
    """Read a path or file-like CSV. Estimate on all or the last 36 RETURNS.

    Simple monthly returns; arithmetic mean x12, sample stdev x sqrt(12),
    Pearson correlations on the same complete months. No filling or sorting.
    Last 36 returns need the last 37 prices. Header comments starting # allowed.
    Reserve eligibility is a mandate input, never inferred from ticker symbols.
    """
    raw = source.read() if hasattr(source, "read") else Path(source).read_text(encoding="utf-8-sig")
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8-sig")
    raw = raw.lstrip("\ufeff")
    rows = list(csv.reader(io.StringIO("\n".join(
        line for line in raw.splitlines() if line.strip() and not line.lstrip().startswith("#")
    ))))
    if not rows or len(rows[0]) < 2:
        raise ValueError("CSV needs a date column followed by ticker price columns.")
    names = [name.strip() for name in rows[0][1:]]
    if not 1 <= len(names) <= 6 or any(not n for n in names) or len(set(names)) != len(names):
        raise ValueError("CSV must have one to six unique, nonempty ticker columns.")
    dates, prices = [], []
    for line_number, row in enumerate(rows[1:], start=2):
        if len(row) != len(names) + 1:
            raise ValueError(f"CSV row {line_number}: wrong number of columns.")
        try:
            observation = date.fromisoformat(row[0].strip())
            values = [float(value) for value in row[1:]]
        except ValueError as error:
            raise ValueError(f"CSV row {line_number}: use YYYY-MM-DD dates and numeric prices.") from error
        if any(not math.isfinite(p) or p <= 0 for p in values):
            raise ValueError(f"CSV row {line_number}: prices must be finite and positive; missing values are refused.")
        if dates:
            months_apart = (observation.year - dates[-1].year) * 12 + observation.month - dates[-1].month
            if months_apart != 1:
                raise ValueError(f"CSV row {line_number}: months must be consecutive, unique, and oldest first.")
        dates.append(observation)
        prices.append(values)
    if len(prices) < 3:
        raise ValueError("At least three monthly prices are needed for sample volatility.")
    returns = [[current[i] / prior[i] - 1 for i in range(len(names))]
               for prior, current in zip(prices, prices[1:])]
    if last_36_months and len(returns) < 36:
        raise ValueError("Last-36-months estimates require at least 37 monthly prices.")
    selected = returns[-36:] if last_36_months else returns
    series = list(zip(*selected))
    means = [statistics.mean(column) for column in series]
    deviations = [statistics.stdev(column) for column in series]
    for name, deviation in zip(names, deviations):
        if deviation <= TOLERANCE:
            raise ValueError(f"{name}: zero monthly-return variation; correlation is undefined.")
    correlations = [[1.0 if i == j else max(-1.0, min(1.0, statistics.correlation(series[i], series[j])))
                     for j in range(len(names))] for i in range(len(names))]
    sleeves = [{"name": name, "return": means[i] * 12,
                "volatility": deviations[i] * math.sqrt(12), "reserve_eligible": False}
               for i, name in enumerate(names)]
    validate_correlations(correlations, len(names))
    return {"sleeves": sleeves, "correlations": correlations, "label": "estimate",
            "price_count": len(prices), "return_count": len(selected),
            "price_start": dates[0].isoformat(), "price_end": dates[-1].isoformat(),
            "return_start": dates[-len(selected)].isoformat(),
            "return_end": dates[-1].isoformat()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Verify course answers and correlation probes.")
    args = parser.parse_args()
    print(AI_NOTICE)
    print(EDUCATIONAL_NOTICE)
    print("Course-authored annual training values; not market estimates.")
    try:
        results = evaluate_portfolios(SLEEVES, CORRELATIONS, BENCHMARK_WEIGHTS, OBJECTIVE_RETURN)
        print_results(results, SLEEVES, OBJECTIVE_RETURN)
        if args.self_test:
            self_test()
    except ValueError as error:
        parser.exit(1, f"REFUSED: {error}\n")


if __name__ == "__main__":
    main()
