"""AI-use disclosure: Prepared with OpenAI Codex assistance.
Educational purposes only. Not financial or investment advice.
Save live Lab 17 evidence; never substitute course answers for provider data.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo
import asof_app as app

ROOT=Path(__file__).resolve().parent
TODAY=datetime.now(ZoneInfo("America/New_York")).date().isoformat()
START="2020-01-01"
LAST_MONTH=(datetime.fromisoformat(TODAY).replace(day=1).date())
from datetime import timedelta
LAST_MONTH=(LAST_MONTH-timedelta(days=1)).isoformat()

def main():
    jobs=[(s,None) for s in app.DEFAULT_SERIES+["PAYEMS","CPIAUCSL"]]
    jobs += [(s,"2026-10-05") for s in app.DEFAULT_SERIES]
    jobs += [("PAYEMS","2025-01-15"),("CPIAUCSL",LAST_MONTH),("CPIAUCSL",TODAY)]
    jobs += [(s,TODAY) for s in app.DEFAULT_SERIES]
    previous_path=ROOT/"Lab_17_source_snapshots.json"
    previous=json.loads(previous_path.read_text(encoding="utf-8")) if previous_path.exists() else {}
    saved=previous.get("records",{}) if previous.get("download_day")==TODAY else {}
    def fetch(job):
        s,v=job
        key=s+"|"+(v or "current")
        if key in saved and not saved[key].get("error"):
            r=saved[key]
            if v and "effective_vintage" not in r:
                r["effective_vintage"]=datetime.strptime(r["raw_csv"].splitlines()[0].split(",")[1][-8:],"%Y%m%d").date().isoformat()
            return key,r
        r=app.download_current(s,TODAY) if v is None else app.download_asof(s,v,TODAY)
        return s+"|"+(v or "current"),r
    with ThreadPoolExecutor(max_workers=4) as pool:
        records=dict(pool.map(fetch,jobs))
    payload={"ai_disclosure":app.AI_NOTICE,"educational_notice":"Educational purposes only. Not financial or investment advice.",
             "download_day":TODAY,"count_start":START,"records":records}
    (ROOT/"Lab_17_source_snapshots.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    failures=[key+": "+r["error"] for key,r in records.items() if r.get("error")]
    if failures:
        raise RuntimeError("\n".join(failures))
    tests=[]
    audits={}
    expected={"BAA":("2026-09-01",6.47),"FEDFUNDS":("2026-09-01",3.75),
              "DGS10":("2026-10-02",5.28),"MORTGAGE30US":("2026-10-01",7.28)}
    for s,(day,value) in expected.items():
        audit=app.compare_series(records[s+"|current"],records[s+"|2026-10-05"],START)
        audits[s+"|2026-10-05"]=audit
        passed=audit["last_known_date"]==day and abs(audit["known_value"]-value)<1e-9
        tests.append({"test":s+" October 5 known answer","pass":passed,
                      "actual_date":audit["last_known_date"],"actual_value":audit["known_value"]})
    payroll=app.compare_series(records["PAYEMS|current"],records["PAYEMS|2025-01-15"],START)
    audits["PAYEMS|2025-01-15"]=payroll
    dec_current=next(r["value"] for r in records["PAYEMS|current"]["data"] if r["date"]=="2024-12-01")
    tests.append({"test":"PAYEMS January 15 probe","pass":payroll["last_known_date"]=="2024-12-01" and
        payroll["known_value"]==159536 and dec_current<159536 and payroll["revised_count"]>0,
        "known_value":payroll["known_value"],"current_December_2024":dec_current,
        "revised_count":payroll["revised_count"]})
    for v in [LAST_MONTH,TODAY]:
        audits["CPIAUCSL|"+v]=app.compare_series(records["CPIAUCSL|current"],records["CPIAUCSL|"+v],START)
    for s in app.DEFAULT_SERIES:
        audits[s+"|"+TODAY]=app.compare_series(records[s+"|current"],records[s+"|"+TODAY],START)
    for key,audit in audits.items():
        audit["requested_vintage"]=records[key]["vintage"]
        audit["returned_vintage"]=records[key]["effective_vintage"]
    output={"ai_disclosure":app.AI_NOTICE,"tests":tests,"audits":audits,"today":TODAY,"last_month_end":LAST_MONTH}
    (ROOT/"Lab_17_audit_results.json").write_text(json.dumps(output,indent=2),encoding="utf-8")
    lines=[app.AI_NOTICE,"Live source results; counts start at "+START,""]
    for test in tests:
        lines.append(("PASS" if test["pass"] else "FAIL")+": "+str(test))
    for key,audit in audits.items():
        lines += ["",key,json.dumps(audit)]
    text="\n".join(lines)+"\n"
    (ROOT/"Lab_17_live_test_output.txt").write_text(text,encoding="utf-8")
    print(text)
    if not all(t["pass"] for t in tests):
        raise AssertionError("Live known-answer mismatch; inspect saved source, do not type in expected values.")

if __name__=="__main__":
    main()

