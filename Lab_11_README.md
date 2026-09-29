# META base run — September 29, 2026

> **AI-use disclosure:** Prepared or edited with assistance from OpenAI Codex. AI-generated content may contain errors. The author is responsible for verifying sources, calculations, and conclusions.
>
> **Educational purposes only. Not financial or investment advice, and not a recommendation to buy, sell, or hold any security.**

Command: `python Lab_11_meta_proforma.py`, run in the AI Finance folder with no scenario overrides.

**Result: reproduced the previous run.** The source file and base inputs are unchanged; the complete visible output matches the prior output after normalizing line endings. Exit code: 0.

The terminal did not have `python` on PATH. The available Python installation was made available to this one process to execute the lab command. No persistent environment settings were changed.

## Saved evidence

- `Lab_11_meta_proforma.py`: exact standalone source used, including embedded opening balances, assumptions, labels, reasons and sources.
- `Lab_11_META_base_inputs.json`: readable snapshot of all base inputs, plus command and run provenance.
- `Lab_11_META_base_output.txt`: complete visible income statement, balance sheet, cash flow statement, check block and valuation output.

## Accounting checks (USD millions)

| Year | Balance gap | Largest link gap | Ending cash | Minimum cash | Result |
|---|---:|---:|---:|---:|---|
| 2026 | 0.0 | 0.00000000 | 10,000.0 | 10,000.0 | PASS |
| 2027 | 0.0 | 0.00000000 | 10,000.0 | 10,000.0 | PASS |
| 2028 | 0.0 | 0.00000000 | 17,972.5 | 10,000.0 | PASS |
| 2029 | 0.0 | 0.00000000 | 57,283.5 | 10,000.0 | PASS |
| 2030 | 0.0 | 0.00000000 | 117,687.8 | 10,000.0 | PASS |

No revolver is drawn in any forecast year. Existing cash and marketable-security sales fund early cash needs.

Equity value: **$556,965.41 million**. Value per share: **$216.38**, using the unchanged 2,574 million-share proxy. The main valuation uses economic FCFF and WACC, retaining negative forecast cash flows.

This is a reproducibility run dated September 29, 2026; the model's information cutoff remains **January 29, 2026**. It does not refresh market prices, filings or assumptions.

Source SHA-256: `4211cb8cd038248e44a5b9d107370d081b8eac1ba4ca8aa77539b00743ab64cd`

Files were renamed with the Lab_11_ prefix on September 29, 2026. The JSON snapshot retains original run provenance; the filenames in this guide refer to the renamed files.
