"""Synthetic calculation tests, not company data.
AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
Educational purposes only. Not financial or investment advice.
"""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent/"buffett-sec-review"/"scripts"))
import sec_facts as s

def fixture():
    facts = {"cik":123,"entityName":"SYNTHETIC TEST COMPANY","facts":{"us-gaap":{}}}
    for metric,tags in s.TAGS.items():
        data = []
        for year in range(2022,2027):
            value = {"revenue":1000,"net_income":20,"operating_cash_flow":30+year-2022,
                     "capital_spending":10,"equity":100,"liabilities":40}[metric] * 1_000_000
            f = {"end":f"{year}-12-31","filed":f"{year+1}-02-01","form":"10-K",
                 "val":value,"accn":f"0000000123-{year%100+1:02d}-000001","fy":year+2}
            if metric in s.FLOWS:
                f["start"] = f"{year}-01-01"
            data.append(f)
        facts["facts"]["us-gaap"][tags[0]] = {"units":{"USD":data}}
    return facts

class FactsTests(unittest.TestCase):
    def test_periods_and_calculations(self):
        r = s.analyze(fixture(),"TEST")
        self.assertEqual([x["fy_end"] for x in r["rows"]],[f"{y}-12-31" for y in range(2022,2027)])
        self.assertEqual(r["rows"][0]["owner_earnings"],20_000_000)
        self.assertEqual(r["rows"][0]["roe_percent"],20)
        self.assertEqual(list(r["checks"].values()),["pass"]*3)

    def test_latest_revision_annual_and_10k_only(self):
        f=fixture()
        data=f["facts"]["us-gaap"][s.TAGS["net_income"][0]]["units"]["USD"]
        original=deepcopy(data[0])
        data += [{**original,"val":25_000_000,"filed":"2029-02-01","accn":"later"},
                 {**original,"val":999,"filed":"2030-01-01","form":"10-Q"},
                 {**original,"val":888,"filed":"2030-01-01","form":"10-K/A"},
                 {**original,"val":777,"filed":"2030-01-01","start":"2022-10-01"}]
        self.assertEqual(s.choose_fact(f,"net_income","2022-12-31","2022-01-01")["value"],25_000_000)

    def test_tag_fallback_and_latest_filing(self):
        f=fixture(); g=f["facts"]["us-gaap"]
        old=g.pop(s.TAGS["capital_spending"][0])
        g[s.TAGS["capital_spending"][1]]=old
        self.assertEqual(s.year_row(f,"2022-01-01","2022-12-31")["fields"]["capital_spending"]["tag"],s.TAGS["capital_spending"][1])
        revenue=deepcopy(g[s.TAGS["revenue"][0]])
        for x in revenue["units"]["USD"]:
            x.update(filed="2030-02-01",accn="latest",val=42)
        g[s.TAGS["revenue"][1]]=revenue
        self.assertEqual(s.choose_fact(f,"revenue","2022-12-31","2022-01-01")["value"],42)

    def test_missing_capex_is_unknown(self):
        f=fixture()
        del f["facts"]["us-gaap"][s.TAGS["capital_spending"][0]]
        r=s.analyze(f,"TEST")
        self.assertTrue(all(x["owner_earnings"] is None for x in r["rows"]))
        self.assertEqual(list(r["checks"].values()),["pass","not known","not known"])
        self.assertIn("capital_spending: not found",s.render_report(r))

    def test_nonpositive_equity_and_missing_net_income(self):
        for eq in (0,-1):
            f=fixture()
            f["facts"]["us-gaap"]["StockholdersEquity"]["units"]["USD"][0]["val"]=eq
            r=s.analyze(f,"TEST")
            self.assertIsNone(r["rows"][0]["roe_percent"])
            self.assertIsNone(r["rows"][0]["liabilities_to_equity"])
            self.assertEqual(list(r["checks"].values())[0],"not known")
        f=fixture(); del f["facts"]["us-gaap"]["NetIncomeLoss"]
        self.assertIsNone(s.analyze(f,"TEST")["rows"][0]["roe_percent"])

    def test_retail_years_and_conflicts(self):
        self.assertTrue(s.annual({"start":"2022-08-29","end":"2023-09-03"}))
        self.assertFalse(s.annual({"start":"2023-06-01","end":"2023-09-03"}))
        f=fixture(); data=f["facts"]["us-gaap"]["NetIncomeLoss"]["units"]["USD"]
        data.append({**data[0],"val":21})
        self.assertIsNone(s.choose_fact(f,"net_income","2022-12-31","2022-01-01")["value"])

    def test_boundary_checks_and_incomplete_history(self):
        r=s.analyze(fixture(),"TEST")
        r["rows"][0]["roe_percent"]=15
        self.assertEqual(list(s.checks(r["rows"]).values())[0],"pass")
        r["rows"][0]["owner_earnings"]=0
        self.assertEqual(list(s.checks(r["rows"]).values())[1],"fail")
        r["rows"][-1]["owner_earnings"]=0
        self.assertEqual(list(s.checks(r["rows"]).values())[2],"fail")
        self.assertEqual(list(s.checks(r["rows"][:4]).values()),["not known"]*3)

    def test_numeric_probe(self):
        printed="2026-08-30 ROE 28.3% Owner earnings 9,382. Threshold 15.0%."
        self.assertEqual(s.audit_memo("ROE 28.30%, owner earnings 9382 on 2026-08-30.",printed),[])
        flags=s.audit_memo("ROE 40.0%. Again 40.0%. Also 4.0e1%.",printed)
        self.assertEqual(len(flags),3)
        self.assertEqual(flags[0]["number"],"40.0%")
        self.assertTrue(s.audit_memo("ROE .5%",printed))

if __name__=="__main__":
    print(s.NOTICE)
    unittest.main(verbosity=2)

