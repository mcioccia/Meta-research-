"""AI-use disclosure: Prepared with OpenAI Codex assistance.
Educational purposes only. Not financial or investment advice.
Synthetic fixtures test software; they are not market observations.
"""
from datetime import date
from io import BytesIO
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse
from urllib.error import HTTPError
from pathlib import Path
import tempfile
# Keep test temporary files in this writable workspace.
_test_tmp = Path(__file__).resolve().parent / ".test_tmp"
_test_tmp.mkdir(exist_ok=True)
tempfile.tempdir = str(_test_tmp)

import streamlit as st
from streamlit.testing.v1 import AppTest
from pathlib import Path
import asof_app as app

class Tests(unittest.TestCase):
    def test_missing_day_and_vintage_identity(self):
        data=app.parse_csv("observation_date,DGS10_20261005\n2026-10-01,5.2\n2026-10-02,.\n","DGS10","2026-10-05")
        self.assertIsNone(data[-1]["value"])
        with self.assertRaises(ValueError):
            app.parse_csv("observation_date,DGS10\n2026-10-01,5.2\n","DGS10","2026-10-05")

    def test_returned_vintage_guard(self):
        data=app.parse_csv("observation_date,DGS10_20261028\n2026-10-27,4.99\n", "DGS10", "2026-10-29")
        self.assertEqual(data[0]["value"],4.99)
        with self.assertRaises(ValueError):
            app.parse_csv("observation_date,DGS10_20261030\n2026-10-29,4.99\n", "DGS10", "2026-10-29")

    def test_revisions_and_counts(self):
        now={"data":[{"date":"2020-01-01","value":2.0},{"date":"2020-02-01","value":None},
                     {"date":"2020-03-01","value":4.0},{"date":"2020-04-01","value":5.0}]}
        old={"data":[{"date":"2020-01-01","value":1.0},{"date":"2020-02-01","value":None},
                     {"date":"2020-03-01","value":4.0}]}
        result=app.compare_series(now,old,"2020-01-01")
        self.assertEqual(result["revised_count"],1)
        self.assertEqual(result["values_after_last_known"],1)
        self.assertEqual(result["last_known_date"],"2020-03-01")
        self.assertEqual(app.compare_series(now,old,"2020-03-01")["revised_count"],0)
        empty=app.compare_series(now,{"data":[]},"2020-01-01")
        self.assertIsNone(empty["last_known_date"])
        self.assertIsNone(empty["values_after_last_known"])


    def test_finance_changes_and_overlay(self):
        records={
            "BAA":{"data":[{"date":"2020-01-01","value":2.0},{"date":"2020-02-01","value":3.0}]},
            "DGS10":{"data":[{"date":"2020-01-02","value":1.0},{"date":"2020-01-03","value":3.0},
                             {"date":"2020-02-03","value":4.0},{"date":"2020-03-01","value":None}]}}
        last,prior,move=app.latest_move(records["DGS10"])
        self.assertEqual(last["date"],"2020-02-03")
        self.assertEqual(move*100,100)
        rows,base=app.overlay_data(records,"2020-01-01",False)
        self.assertIsNone(base)
        self.assertEqual(next(r["Value"] for r in rows if r["Series"]=="DGS10" and r["Month"].month==1),2)
        rows,base=app.overlay_data(records,"2020-01-01",True)
        self.assertEqual(base,"2020-01")
        self.assertEqual(next(r["Value"] for r in rows if r["Series"]=="DGS10" and r["Month"].month==2),200)
        records["BAA"]["data"]=[{"date":"2020-02-01","value":3.0},{"date":"2020-04-01","value":6.0}]
        rows,base=app.overlay_data(records,"2020-01-01",True)
        self.assertEqual(base,"2020-02")
        self.assertTrue(all(r["Value"] is None for r in rows if r["Month"].month==3))
        records["BAA"]["data"]=[{"date":"2021-01-01","value":3.0}]
        with self.assertRaises(ValueError):
            app.overlay_data(records,"2020-01-01",True)

    def test_download_cache_and_request_urls(self):
        st.cache_data.clear()
        urls=[]
        def fake(request,timeout):
            urls.append(request.full_url)
            query=parse_qs(urlparse(request.full_url).query)
            name=query["id"][0]
            if "vintage_date" in query:
                name+="_"+query["vintage_date"][0].replace("-","")
            return BytesIO(f"observation_date,{name}\n2020-01-01,1.0\n".encode())
        with patch.object(app,"urlopen",side_effect=fake):
            for _ in range(2):
                app.download_current("BAA","2026-10-29")
                app.download_asof("BAA","2026-10-05","2026-10-29")
        self.assertEqual(len(urls),2)
        self.assertIn("fredgraph.csv",urls[0])
        self.assertIn("vintage_date=2026-10-05",urls[1])
        st.cache_data.clear()

    def test_app_controls_and_unknown_id_isolation(self):
        st.cache_data.clear()
        def fake(request,timeout):
            query=parse_qs(urlparse(request.full_url).query)
            name=query["id"][0]
            if name=="NOT_A_REAL_SERIES":
                raise HTTPError(request.full_url,404,"Not found",None,None)
            if "vintage_date" in query:
                name+="_"+query["vintage_date"][0].replace("-","")
            return BytesIO(f"observation_date,{name}\n2020-01-01,1\n2020-02-01,2\n".encode())
        with patch("urllib.request.urlopen",side_effect=fake):
            at=AppTest.from_file(str(Path(__file__).with_name("asof_app.py"))).run(timeout=120)
            self.assertEqual(len(at.exception),0)
            self.assertEqual(at.multiselect[0].value,app.DEFAULT_SERIES)
            self.assertEqual(at.date_input(key="start").value,date(2020,1,1))
            self.assertEqual(len(at.metric),4)
            at.radio(key="overlay_scale").set_value("Indexed levels (start = 100)").run(timeout=120)
            self.assertEqual(len(at.exception),0)
            at.text_input(key="custom").set_value("CPIAUCSL").run(timeout=120)
            self.assertEqual(len(at.exception),0)
            self.assertTrue(any("Mixed units" in item.value for item in at.info))
            at.radio(key="overlay_source").set_value("As known on the selected date").run(timeout=120)
            self.assertEqual(len(at.exception),0)
            at.text_input(key="custom").set_value("NOT_A_REAL_SERIES").run(timeout=120)
            self.assertEqual(len(at.exception),0)
            self.assertGreaterEqual(len(at.error),1)
            table=at.dataframe[-1].value
            self.assertEqual((table["Status"]=="OK").sum(),4)
            self.assertEqual((table["Status"]=="Download error").sum(),1)
        st.cache_data.clear()

if __name__=="__main__":
    print(app.AI_NOTICE)
    unittest.main(verbosity=2)



