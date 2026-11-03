"""Temporary synthetic app tests; not evidence of real COST/JPM results.
AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
Educational purposes only. Not financial or investment advice.
"""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

TEST_TEMP=Path(__file__).resolve().parent/".test_tmp"
TEST_TEMP.mkdir(exist_ok=True)
tempfile.tempdir=str(TEST_TEMP)
from streamlit.testing.v1 import AppTest
from test_sec_facts import fixture, s
ROOT=Path(__file__).resolve().parent

class AppTests(unittest.TestCase):
    def test_report_memo_and_invented_number(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td).resolve()
            assert TEST_TEMP.resolve() in root.parents
            sources=root/"sources"
            sources.mkdir()
            def cache(name,url,data):
                (sources/name).write_text(json.dumps({"ai_disclosure":s.NOTICE,"url":url,
                    "downloaded_at":"SYNTHETIC TEST, not downloaded","sha256":s.digest(data),"data":data}),encoding="utf-8")
            cache("company_tickers.json",s.TICKERS_URL,{"0":{"cik_str":123,"ticker":"TEST"}})
            cache("TEST_companyfacts.json","https://data.sec.gov/api/xbrl/companyfacts/CIK0000000123.json",fixture())
            report=s.run_ticker("TEST",root,offline=True)
            memo=root/"runs"/"TEST"/"memo.md"
            memo.write_text(s.NOTICE+"\nSynthetic test: ROE 20.0%.",encoding="utf-8")
            memo.with_name("memo_meta.json").write_text(json.dumps({
                "ticker":"TEST","report_id":report["report_id"],
                "memo_sha256":hashlib.sha256(memo.read_bytes()).hexdigest(),"ai_disclosure":s.NOTICE}),encoding="utf-8")
            code=(ROOT/"app.py").read_text(encoding="utf-8-sig")
            code=code.replace("ROOT = Path(__file__).resolve().parent",f"ROOT = Path({str(root)!r})")
            code=code.replace('st.text_input("Company ticker", "COST")','st.text_input("Company ticker", "TEST")')
            at=AppTest.from_string(code).run(timeout=30)
            self.assertEqual(len(at.exception),0)
            self.assertEqual(len(at.error),0)
            self.assertEqual(len(at.metric),3)
            self.assertTrue(any("All numeric literals" in x.value for x in at.success))
            self.assertEqual(len(at.get("vega_lite_chart")),1)
            at.text_area[0].set_value(memo.read_text()+"\nUnsupported ROE 40.0%.").run(timeout=30)
            self.assertEqual(len(at.exception),0)
            self.assertTrue(any("Unsupported numbers" in x.value for x in at.error))
            self.assertTrue(any("40.0%" in str(x.value) for x in at.dataframe))
            at.text_input[0].set_value("???").run(timeout=30)
            self.assertEqual(len(at.exception),0)
            self.assertTrue(any("Enter a ticker" in x.value for x in at.error))

if __name__=="__main__":
    print(s.NOTICE)
    unittest.main(verbosity=2)

