"""Compare downloaded SEC reports with the course's expected answers.
AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
Educational purposes only. Not financial or investment advice.
These expected values are test assertions, never inputs to calculations.
"""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"buffett-sec-review"/"scripts"))
from sec_facts import NOTICE, run_ticker, audit_memo, render_report
EXPECTED=[
("2022-08-28",226954,5844,7392,3891,20642,28.3,3501),
("2023-09-03",242290,6292,11068,4323,25058,25.1,6745),
("2024-09-01",254453,7367,11339,4710,23622,31.2,6629),
("2025-08-31",275235,8099,13335,5498,29164,27.8,7837),
("2026-08-30",303154,9226,15817,6435,35803,25.8,9382)]
def main():
    print(NOTICE)
    cost=run_ticker("COST",ROOT,offline=True)
    jpm=run_ticker("JPM",ROOT,offline=True)
    failures=[]
    if len(cost["rows"])!=5:
        failures.append("COST does not have five fiscal periods.")
    for row,exp in zip(cost["rows"],EXPECTED):
        vals=[row["fy_end"]]
        vals += [None if row["fields"][m]["value"] is None else row["fields"][m]["value"]/1_000_000
                 for m in ("revenue","net_income","operating_cash_flow","capital_spending","equity")]
        vals += [None if row["roe_percent"] is None else round(row["roe_percent"],1),
                 None if row["owner_earnings"] is None else row["owner_earnings"]/1_000_000]
        if tuple(vals)!=exp:
            failures.append(f"COST source differs: calculated {vals}; course expectation {exp}.")
    if list(cost["checks"].values())!=["pass"]*3:
        failures.append("COST's three checks differ from the course expectation.")
    if len(jpm["rows"])!=5 or any(r["fields"]["capital_spending"]["value"] is not None or r["owner_earnings"] is not None for r in jpm["rows"]):
        failures.append("JPM capital-spending/owner-earnings probe differs from expectation.")
    if list(jpm["checks"].values())[1:]!=["not known","not known"]:
        failures.append("JPM owner-earnings checks differ from expectation.")
    if not audit_memo("Deliberately invented ROE: 40.0%.",render_report(cost)):
        failures.append("The unsupported 40.0% probe was not flagged.")
    if failures:
        print("\n".join(failures))
        print("Investigate filing dates, selected periods and tags. Never overwrite SEC values to force a match.")
        return 1
    print("PASS: COST five-year course table and all three checks.")
    print("PASS: JPM capital spending and owner earnings missing; both checks not known.")
    print("PASS: invented 40.0% flagged.")
    return 0
if __name__=="__main__":
    try:
        raise SystemExit(main())
    except (ValueError,OSError,KeyError) as error:
        print("LIVE VALIDATION NOT COMPLETE:",error)
        raise SystemExit(1)

