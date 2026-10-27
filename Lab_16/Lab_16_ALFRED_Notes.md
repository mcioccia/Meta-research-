# Lab 16 — Free ALFRED example

> AI-use disclosure: Prepared with OpenAI Codex assistance; verify sources and calculations.
>
> Educational purposes only. Not financial or investment advice.

Downloaded October 27, 2026. ALFRED was accessed without a paid subscription or API key.

## Series and scope

The example uses **CPIAUCSL**, Consumer Price Index for All Urban Consumers: All Items in U.S. City Average. Source agency: U.S. Bureau of Labor Statistics, distributed through the Federal Reserve Bank of St. Louis. Units: index, 1982–1984 = 100; monthly; seasonally adjusted. CPI was chosen as an educational example because the course mandate references inflation. It is not an ETF price series.

[ALFRED series page](https://alfred.stlouisfed.org/series?seid=CPIAUCSL) · [Vintage-date documentation](https://alfred.stlouisfed.org/help/downloaddata)

ALFRED's vintage date selects information available as of that day. It is not necessarily the observation's first publication date. These snapshots demonstrate availability at a cutoff; they do not provide the full publication and revision history needed to recreate all four training-table cleaning steps.

## What was knowable?

The signal uses the same formula as the course: percent change from the prior month to the latest available month. To isolate the decision-period comparison, the measured-month scope stays fixed at January–March 2026 in all three snapshots.

| Index observation | March 31 vintage | April 15 vintage | October 27 vintage |
| --- | ---: | ---: | ---: |
| January 2026 | 326.588 | 326.588 | 326.588 |
| February 2026 | 327.460 | 327.460 | 327.460 |
| March 2026 | Unavailable | 330.293 | 330.293 |
| Latest available monthly change within this scope | +0.27% (February) | +0.87% (March) | +0.87% (March) |

On March 31, the latest available observation in this window was February. The later snapshots include March. Using the March change for a March 31 decision would use information unavailable on that date.

January and February are unchanged across these snapshots. This particular example shows the effect of a later release, not a detected revision of those two months. The two signals refer to different measured months; their difference is not a revision to the February signal.

These percentages are **month-over-month inflation**, not annual inflation, fund returns, or a new portfolio objective. The 7.49% portfolio target and BIL reserve rule have not been altered.

The downloads also retain April–September observations where available, but those later measured months are excluded from the fixed January–March signal comparison. Missing values remain unavailable rather than being filled with zero.

## Reproduce

From the Lab_16 folder, run the saved data without an internet connection:

```powershell
python alfred_example.py
```

To download the same three historical snapshots again:

```powershell
python alfred_example.py --download
```

The script imports the existing signal function from `asof.py`. It checks the vintage identifier returned by ALFRED, dates, numeric values and an independent arithmetic calculation.

## Saved evidence

- `Lab_16_ALFRED_source.json`: exact returned CSV text inside a JSON record, parsed observations, source URLs, download timestamps and SHA-256 hashes for each snapshot.
- `Lab_16_ALFRED_results.json`: computed signals, comparison scope and same-month differences.
- `Lab_16_ALFRED_output.txt`: actual run output.
- `alfred_example.py`: reproducible download and comparison.

The original fictional training table and its passing tests remain in `asof.py`. The selected vintage dates must not be relabelled as actual publication dates. Exact initial publication dates, intervening revisions and intraday availability remain unresolved by this snapshot-only example. No partner exercise is claimed.

