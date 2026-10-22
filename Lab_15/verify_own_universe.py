"""Reproduce the confirmed Lab 15 mandate and independently verify the grid minimum.
AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
Educational purposes only. Not financial or investment advice.
NumPy is used only for independent verification, not by portfolio.py.
"""
import copy
import csv
import hashlib
import itertools
import json
from pathlib import Path
import sys

import numpy as np
import portfolio as p

OBJECTIVE = 0.0749  # Student chose six-fund average, rounded to two percentage decimals.
RESERVE_MINIMUM = 0.03  # Student confirmed 3% in BIL only.
RESERVE_TICKERS = {"BIL"}
ROOT = Path(__file__).resolve().parent


def independent_check(path, recent, result):
    with path.open(encoding="utf-8-sig") as handle:
        rows = list(csv.reader(line for line in handle if not line.startswith("#")))
    prices = np.array([[float(v) for v in row[1:]] for row in rows[1:]])
    returns = prices[1:] / prices[:-1] - 1
    if recent:
        returns = returns[-36:]
    mean = returns.mean(axis=0) * 12
    covariance = np.cov(returns, rowvar=False, ddof=1) * 12
    # Independently enumerate via separator positions instead of engine recursion.
    weights = []
    n = len(mean)
    for separators in itertools.combinations(range(20+n-1), n-1):
        boundaries = (-1, *separators, 20+n-1)
        weights.append([(boundaries[i+1]-boundaries[i]-1)/20 for i in range(n)])
    weights = np.array(weights)
    expected = weights @ mean
    eligibility = np.array([ticker in RESERVE_TICKERS for ticker in rows[0][1:]])
    reserves = weights @ eligibility
    valid = (expected >= OBJECTIVE-1e-12) & (reserves >= RESERVE_MINIMUM-1e-12)
    variance = np.einsum("ij,jk,ik->i", weights, covariance, weights)
    assert len(weights) == 53130
    if not valid.any():
        assert result is None
        return {"status": "PASS", "feasible": 0, "tried": len(weights)}
    feasible_indices = np.flatnonzero(valid)
    best_index = feasible_indices[np.argmin(variance[valid])]
    assert result is not None
    np.testing.assert_allclose(result["weights"], weights[best_index], atol=1e-12, rtol=0)
    np.testing.assert_allclose(result["return"], expected[best_index], atol=1e-12, rtol=0)
    np.testing.assert_allclose(result["volatility"], np.sqrt(variance[best_index]), atol=1e-12, rtol=0)
    assert result["feasible"] == int(valid.sum())
    return {"status": "PASS", "feasible": int(valid.sum()), "tried": len(weights),
            "method": "NumPy sample covariance and independent separator enumeration"}


def main():
    path = ROOT / "prices.csv"
    result = {"ai_disclosure": p.AI_NOTICE, "educational_notice": p.EDUCATIONAL_NOTICE,
              "objective": OBJECTIVE, "reserve_minimum": RESERVE_MINIMUM,
              "reserve_eligible": sorted(RESERVE_TICKERS),
              "target_basis": "Student-selected all-month six-fund arithmetic average, rounded to 7.49%; fixed in both runs",
              "csv_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "partner_attack_status": "Pending: no actual changed estimate supplied",
              "student_call": "Pilot: use it provisionally; adopt only after the target and allocation hold up across other reasonable estimation windows",
              "runs": {}}
    for label, recent in [("all_months", False), ("last_36_months", True)]:
        estimates = p.estimate_from_csv(path, recent)
        for sleeve in estimates["sleeves"]:
            sleeve["reserve_eligible"] = sleeve["name"] in RESERVE_TICKERS
        mix = p.search_portfolios(estimates["sleeves"], estimates["correlations"], OBJECTIVE, RESERVE_MINIMUM)
        result["runs"][label] = {"estimates": estimates, "mix": mix,
                                  "independent_check": independent_check(path, recent, mix)}
    base = result["runs"]["all_months"]["mix"]
    recent = result["runs"]["last_36_months"]["mix"]
    result["weight_changes_points"] = [(b-a)*100 for a,b in zip(base["weights"],recent["weights"])] if base and recent else None
    result["largest_weight_change_points"] = max(abs(x) for x in result["weight_changes_points"]) if base and recent else None
    # An AI-assisted technical stress, explicitly not a claim of partner feedback.
    stressed = copy.deepcopy(result["runs"]["all_months"]["estimates"])
    stressed["sleeves"][0]["return"] -= .01
    result["ai_technical_stress"] = {
        "label": "QQQ expected return minus 1 percentage point; all-month window; all other inputs fixed",
        "old_value": result["runs"]["all_months"]["estimates"]["sleeves"][0]["return"],
        "new_value": stressed["sleeves"][0]["return"],
        "mix": p.search_portfolios(stressed["sleeves"], stressed["correlations"], OBJECTIVE, RESERVE_MINIMUM)}
    print(p.AI_NOTICE)
    print(p.EDUCATIONAL_NOTICE)
    print("Student mandate: objective 7.49%; reserve minimum 3.00%; BIL only.")
    print("Inputs are historical estimates, not guaranteed returns.")
    for label, run in result["runs"].items():
        print(f"\n{label}: {run['estimates']['return_count']} monthly returns")
        mix = run["mix"]
        if mix is None:
            print("no mix meets the objective")
            continue
        for sleeve, weight in zip(run["estimates"]["sleeves"], mix["weights"]):
            print(f"  {sleeve['name']}: {weight*100:.2f}%")
        print(f"  Return {mix['return']*100:.2f}%; volatility {mix['volatility']*100:.2f}%; reserve {mix['reserve']*100:.2f}%")
        print(f"  {mix['feasible']} feasible / {mix['tried']} tested")
        print("  Independent verification: PASS")
    print(f"\nLargest weight change: {result['largest_weight_change_points']:.2f} percentage points")
    print("Partner attack: pending; no change invented.")
    print("Student call:", result["student_call"])
    (ROOT / "Lab_15_own_universe_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
