# Lab 15 — QQQ download and standalone test

> AI-use disclosure: Prepared with OpenAI Codex assistance; verify sources and results.
> Educational purposes only. Not financial or investment advice.

QQQ was freshly downloaded on **2026-10-22T14:11:46.870450-04:00** (America/New_York).
The separate `QQQ_prices.csv` contains 60 monthly adjusted closes in USD, October 2021 through September 2026, oldest first. The actual observation dates run from October 29, 2021 to September 30, 2026. October 2026 is incomplete and excluded to preserve the earlier Lab 15 comparison period.

Source: [Yahoo Finance QQQ history](https://finance.yahoo.com/quote/QQQ/history/) and the [exact download endpoint](https://query1.finance.yahoo.com/v8/finance/chart/QQQ?period1=1633046400&period2=1790812800&interval=1d&events=div%2Csplits&includeAdjustedClose=true). The download uses daily observations, selecting the last available trading observation in each calendar month from the provider's explicit `adjclose` field. No prices were filled or invented, and no second dividend or split adjustment was applied. The downloaded response and timestamp are retained in `Lab_15_QQQ_source.json`.

## Results

The test imports the existing `portfolio.py`. The return objective stays at **7.49%**, and the reserve rule stays at **at least 3% in BIL only**. QQQ remains ineligible for the reserve. A one-fund fully invested portfolio can only hold 100% QQQ; there is no diversification choice to optimize.

| Window | Monthly returns | Annual return estimate | Annual volatility estimate | Eligible reserve | Mandate result |
| --- | ---: | ---: | ---: | ---: | --- |
| All months | 59 | 16.04% | 20.84% | 0.00% | Infeasible |
| Last 36 months | 36 | 26.39% | 17.26% | 0.00% | Infeasible |

QQQ clears the return threshold under both historical estimates but fails the reserve rule. Therefore the search correctly returns **no mix meets the objective** in both cases. The objective was not lowered and reserve eligibility was not changed to force a result. This one-fund diagnostic does not replace the course's three-to-six-fund universe.

The annual return estimate equals the arithmetic mean monthly return times 12, not CAGR. Volatility equals the sample monthly standard deviation times the square root of 12. These are historical estimates, not promises of future performance. Changing the window changes both estimates substantially.

## Verification and reproducibility

- All 60 exported prices match the fresh provider observations exactly; all dates align with the earlier saved six-fund file.
- Compared with that earlier file, 36 QQQ prices differ. Maximum absolute difference: USD 0.000152587890625 per share. Provider snapshots can differ; the six-fund file was preserved.
- Independent direct arithmetic checks reproduced the engine's mean and sample standard deviation for both windows.
- For a single asset, the correlation matrix is `[1.0]`; the 100% portfolio volatility equals QQQ's own volatility.
- Both searches correctly rejected QQQ-only because eligible reserve weight is zero.

CSV SHA-256: `a18277c57bb0328a1c7a170243a46756230430fac07944e63167f67b446231da`

To rerun the saved-data test from this folder:

```powershell
..\Lab_14\.venv\Scripts\python.exe test_qqq.py
```

The test saves `Lab_15_QQQ_test_output.txt` and `Lab_15_QQQ_test_results.json`. To inspect the same case in the app, upload `QQQ_prices.csv`, set the target to 7.49% and reserve minimum to 3%, and leave QQQ reserve-eligible unchecked. Both windows should report no qualifying mix. Restore `prices.csv` for the six-fund assignment. This run tested the engine directly; it does not claim a new browser interaction or partner exercise.
