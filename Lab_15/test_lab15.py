"""Lab 15 verification. Synthetic prices below are test fixtures, not company data.
AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
Educational purposes only. Not financial or investment advice.
"""
import copy
import io
import math
from pathlib import Path
import statistics
import subprocess
import sys
import unittest

import portfolio as p


class EngineTests(unittest.TestCase):
    def test_old_output_identical(self):
        old = Path(__file__).resolve().parent.parent / "Lab_14" / "portfolio.py"
        if not old.exists():
            self.skipTest("Lab_14 comparison file not present in this checkout")
        for args in ([], ["--self-test"]):
            first = subprocess.check_output([sys.executable, "-B", str(old), *args])
            new = subprocess.check_output([sys.executable, "-B", str(Path(p.__file__)), *args])
            self.assertEqual(first, new)

    def test_meridian_minimum_and_one_point(self):
        original = copy.deepcopy(p.SLEEVES)
        base = p.search_portfolios(p.SLEEVES, p.CORRELATIONS, .065, .03)
        self.assertEqual(base["weights"], [0, .20, .25, .55])
        self.assertEqual(base["tried"], math.comb(23, 3))
        # Independent direct double-sum confirms this returned portfolio's risk.
        w = base["weights"]
        variance = sum(w[i]*w[j]*p.SLEEVES[i]["volatility"]*p.SLEEVES[j]["volatility"]*p.CORRELATIONS[i][j]
                       for i in range(4) for j in range(4))
        self.assertAlmostEqual(base["volatility"], math.sqrt(variance))
        changed = copy.deepcopy(p.SLEEVES)
        changed[3]["return"] -= .01
        stress = p.search_portfolios(changed, p.CORRELATIONS, .065, .03)
        self.assertEqual(stress["weights"], [0, .10, .10, .80])
        self.assertGreater(stress["volatility"], base["volatility"])
        self.assertEqual(p.SLEEVES, original)

    def test_infeasible_and_reserve_boundaries(self):
        self.assertIsNone(p.search_portfolios(p.SLEEVES, p.CORRELATIONS, .09, .03))
        assets = copy.deepcopy(p.SLEEVES)
        for s in assets:
            s["reserve_eligible"] = False
        self.assertIsNone(p.search_portfolios(assets, p.CORRELATIONS, .065, .03))
        self.assertIsNotNone(p.search_portfolios(assets, p.CORRELATIONS, .065, 0))
        only_reserves = p.search_portfolios(p.SLEEVES, p.CORRELATIONS, .035, 1)
        self.assertAlmostEqual(only_reserves["reserve"], 1)

    def test_small_grid_global_minimum_independent(self):
        assets = copy.deepcopy(p.SLEEVES[:2])
        corr = [[1, .1], [.1, 1]]
        result = p.search_portfolios(assets, corr, .04, 0)
        independently_feasible = []
        for units in range(21):
            a, b = units/20, 1-units/20
            if a*.035+b*.043 >= .04-1e-12:
                independently_feasible.append((math.sqrt((a*.005)**2+(b*.07)**2+2*a*b*.005*.07*.1), [a,b]))
        risk, weights = min(independently_feasible)
        self.assertAlmostEqual(result["volatility"], risk)
        for actual, expected in zip(result["weights"], weights):
            self.assertAlmostEqual(actual, expected)

    def test_estimator_known_sample(self):
        text = "# AI test fixture, not market data\nDate,A,B\n2024-01-31,100,100\n2024-02-29,110,120\n2024-03-31,99,108\n2024-04-30,118.8,113.4\n"
        result = p.estimate_from_csv(io.StringIO(text))
        a, b = [.1,-.1,.2], [.2,-.1,.05]
        self.assertAlmostEqual(result["sleeves"][0]["return"], statistics.mean(a)*12)
        self.assertAlmostEqual(result["sleeves"][0]["volatility"], statistics.stdev(a)*math.sqrt(12))
        self.assertAlmostEqual(result["correlations"][0][1], statistics.correlation(a,b))
        self.assertEqual(result["return_count"], 3)

    def test_last36_is_36_returns_not_prices(self):
        rows, price, returns = ["Date,A"], 100, []
        for index in range(61):
            if index:
                value = (.10 if index <= 24 else .001*index)
                returns.append(value)
                price *= 1+value
            rows.append(f"{2020+index//12}-{index%12+1:02d}-01,{price:.12f}")
        recent = p.estimate_from_csv(io.StringIO("\n".join(rows)), True)
        self.assertEqual(recent["return_count"], 36)
        self.assertAlmostEqual(recent["sleeves"][0]["return"], statistics.mean(returns[-36:])*12)
        with self.assertRaisesRegex(ValueError, "37 monthly prices"):
            p.estimate_from_csv(io.StringIO("\n".join(rows[:37])), True)

    def test_bad_csv_refused(self):
        bad = [
            "Date,A\n2024-02-01,100\n2024-01-01,110\n2024-03-01,90",
            "Date,A\n2024-01-01,100\n2024-03-01,110\n2024-04-01,90",
            "Date,A\n2024-01-01,100\n2024-02-01,\n2024-03-01,90",
            "Date,A\n2024-01-01,100\n2024-02-01,nan\n2024-03-01,90",
            "Date,A\n2024-01-01,100\n2024-02-01,100\n2024-03-01,100",
            "Date,A,A\n2024-01-01,100,100\n2024-02-01,101,99\n2024-03-01,99,98",
        ]
        for text in bad:
            with self.subTest(csv=text), self.assertRaises(ValueError):
                p.estimate_from_csv(io.StringIO(text))

    def test_real_csv_and_uploaded_window(self):
        from streamlit.testing.v1 import AppTest
        csv_path = Path(__file__).with_name("prices.csv")
        if not csv_path.exists():
            self.skipTest("Price file not present")
        full = p.estimate_from_csv(csv_path)
        recent = p.estimate_from_csv(csv_path, True)
        self.assertEqual(full["price_count"], 60)
        self.assertEqual(full["return_count"], 59)
        self.assertEqual(recent["return_count"], 36)
        self.assertEqual([s["name"] for s in full["sleeves"]], ["QQQ", "ONEQ", "VUG", "BIL", "IEF", "LQD"])
        code = ('import io\nfrom pathlib import Path\nfrom unittest.mock import patch\nimport app\n'
                f'upload = io.BytesIO(Path({str(csv_path)!r}).read_bytes())\n'
                'upload.name = "prices.csv"\n'
                'with patch("streamlit.file_uploader", return_value=upload):\n    app.main()\n')
        at = AppTest.from_string(code, default_timeout=30).run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(len(at.warning), 2)  # no reserve-eligible assets at positive minimum
        at.number_input(key="reserve").set_value(0.0).run()
        self.assertEqual(len(at.exception), 0)
        baseline = [m.value for m in at.metric][:3]
        self.assertEqual(at.metric[-1].value, "0.00 percentage points")
        at.checkbox(key="recent").set_value(True).run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual([m.value for m in at.metric][:3], baseline)
        expected_current = p.search_portfolios(recent["sleeves"], recent["correlations"], .065, 0)
        self.assertEqual(at.metric[3].value, f"{expected_current['return']*100:.2f}%")
        at.checkbox(key="recent").set_value(False).run()
        self.assertEqual(at.metric[-1].value, "0.00 percentage points")

    def test_app_widgets_and_infeasible(self):
        from streamlit.testing.v1 import AppTest
        at = AppTest.from_file(str(Path(__file__).with_name("app.py")), default_timeout=30).run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual([m.value for m in at.metric][-1], "0.00 percentage points")
        at.number_input(key="return_meridian_all_3").set_value(7.0).run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual([m.value for m in at.metric][-1], "25.00 percentage points")
        self.assertEqual([m.value for m in at.metric][0], "6.51%")
        at.number_input(key="objective").set_value(9.0).run()
        self.assertEqual(len(at.exception), 0)
        self.assertTrue(any("no mix meets the objective" in w.value for w in at.warning))
        at.number_input(key="objective").set_value(6.5)
        at.number_input(key="return_meridian_all_3").set_value(8.0).run()
        self.assertEqual([m.value for m in at.metric][-1], "0.00 percentage points")


if __name__ == "__main__":
    print(p.AI_NOTICE, flush=True)
    print(p.EDUCATIONAL_NOTICE, flush=True)
    unittest.main(verbosity=2)
