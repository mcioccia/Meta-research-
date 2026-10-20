> **AI-use disclosure:** Prepared with OpenAI Codex assistance. Verify the code, calculations and conclusions.
>
> **Educational purposes only. Not financial or investment advice.**

# Lab 14 — Portfolio engine and mandate comparison

Prepared and verified October 20, 2026.

## Source and scope

All return, volatility, correlation, portfolio and mandate inputs come from the course-authored tables pasted into this chat. They are training values, not market estimates. No market-data source or download applies to these inputs. The separate META `prices.csv` is not used in this engine.

Annual return objective: estimated CPI of 2.5% plus 4.0%, giving 6.5% using the course's additive convention. No fee assumptions or realized five-year returns were supplied: this compares expected annual returns with the threshold, not achievement of the full rolling five-year, net-of-costs mandate.

`portfolio.py` uses only the Python standard library. Inputs are editable near the top; returns, volatility and weights use decimals. Matrix and weight order is bills, 10-year note, IG bond fund, global equity fund. `mandate.py` uses percentage weights instead.

## Run from the Lab_14 folder

```powershell
python portfolio.py
python portfolio.py --self-test
python mandate.py --self-test
```

If `python` is not available on your path, use the existing local environment:

```powershell
.\.venv\Scripts\python.exe portfolio.py
.\.venv\Scripts\python.exe portfolio.py --self-test
.\.venv\Scripts\python.exe mandate.py --self-test
```

## Verified base results

| Portfolio | Bills / 10-year / IG / equity weights (%) | Expected annual return | Annual volatility | Reserve-eligible weight | Meets 6.5%? |
| --- | --- | --- | --- | --- | --- |
| Benchmark | 0.0 / 0.0 / 40.0 / 60.0 | 6.80% | 10.46% | 0.0% | Yes |
| Equal weight | 25.0 / 25.0 / 25.0 / 25.0 | 5.20% | 5.21% | 50.0% | No |
| Inverse volatility | 84.3 / 6.0 / 7.0 / 2.6 | 3.77% | 1.05% | 90.3% | No |

Every displayed value matches the supplied known answer. Inverse-volatility weights display a total of 99.9% because each component is rounded separately; calculations use unrounded weights that sum to 100%.

## Verification evidence

Actual console results are saved in `Lab_14_portfolio_output.txt` and `Lab_14_mandate_output.txt`.

- Changed IG–equity correlation to 0.50 in both cells in an independent copy: benchmark volatility rose to 11.00%.
- Changed one IG–equity correlation to 1.3: the engine refused it with a message identifying the cell and allowed range.
- Changed only one IG–equity correlation to 0.50: the engine refused the asymmetric matrix.
- Confirmed original inputs were unchanged and reran the base; results matched exactly.
- The Lab_14 copy of `mandate.py` includes candidate E: 40% IG bonds and 60% global equity, with every other holding at zero.
- Candidate E has 100.0% total weight, 0.0% lowest weight, 0.0% reserve eligibility, 100.0% five-day liquidity and 0.0% non-exempt single-company exposure. It fails exactly one check: the 3.0% reserve minimum.
- Existing mandate known-answer and boundary tests still pass. Calendar-year loss remains “requires CIO clarification.”

These were AI-assisted checks of this engine, not a claimed exchange with a learning partner.

## What the comparison establishes

The benchmark meets the expected-return threshold but fails S3's payout-reserve requirement. A benchmark is a comparison standard; it need not be a permissible client holding. Under the case's explicit table, both Treasury bills and the 10-year Treasury note qualify for the reserve. Reserve eligibility does not mean a 10-year note has a stable market value.

No optimization was performed. Volatility is not a maximum-loss guarantee, and this engine does not test S9.

## Reusing the calculations

`evaluate_portfolios` accepts sleeves, correlations, benchmark weights and an objective, returning the computed results without printing or modifying those inputs. Separate functions handle covariance, portfolio return, portfolio volatility, reserve weight, equal weights, inverse-volatility weights and the objective comparison. Importing the file does not run its command-line report.

## Student work still to do

The course asks you to explain the volatility block with AI closed. Open `portfolio_volatility` and its covariance-building function and explain the code yourself. These notes do not claim you have completed that exercise.

- Quiz topic selected: __________
- My answer before the AI explains: __________
- The line I can now explain: __________
- My partner's question and my own answer: __________
- Partner-file break test, if performed: __________

Choose your quiz topic in the chat; the next step is one question for you to answer before an explanation.
