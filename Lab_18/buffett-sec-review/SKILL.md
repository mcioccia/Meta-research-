---
name: buffett-sec-review
description: Use when asked to assess a company's business quality with Buffett-inspired judgment using SEC 10-K facts, five annual periods, reproducible ROE and owner-earnings checks, and a numerically audited memo. Not for stock-price valuation.
---

# SEC business-quality review

AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
Educational purposes only. Not financial or investment advice.

Act as a Buffett-inspired analyst, never claim to be Warren Buffett or describe this as his actual opinion. Code computes; the model judges. Do not install FAskills or use paid data, stock prices, forecasts or valuations.

## Run
1. Select the ticker and a user-authorized output folder. Use the bundled `scripts/sec_facts.py`; do not reproduce its arithmetic in prose.
2. Require the user's name and email in `SEC_USER_AGENT`, or `OUTPUT/.local/sec_identity.json` with key `user_agent`. Never invent contact details. Keep this file outside version control and never print the header.
3. Run `python PATH_TO_SKILL/scripts/sec_facts.py TICKER --root OUTPUT`. Use `--refresh` for a new download; use `--offline` only to reproduce saved, hash-checked sources. Save the visible output.
4. Read `OUTPUT/runs/TICKER/report.md` in full. Numbers come only from this printed report. Report the actual fiscal periods downloaded; if course examples differ, show the discrepancy, never alter SEC data to match them.

## Rules enforced by the script
Only USD facts from 10-Ks, the latest five annual fiscal periods, and latest filing per period. Annual durations accept normal calendar and retail week-based years. Within the latest filing, prefer the specified revenue and capex tags; all selected tags and filing accessions are printed.

ROE = net income / year-end equity. Owner earnings = operating cash flow minus capital spending, a simplified lab proxy, not a maintenance-capex estimate. Missing facts stay "not found"; ratios with nonpositive equity and checks with missing inputs stay "not known". The three tests are ROE at least 15% every year, positive owner earnings every year, and growth from first year to last.

## Judge and save
Write `OUTPUT/runs/TICKER/memo.md` with:
- AI disclosure and educational/not-advice notice.
- A verdict: **own the business**, **watch it**, or **pass** — business quality only.
- A short explanation tied to the code's checks and printed figures.
- What the figures cannot establish: durable moat, management, circle of competence and future reinvestment needs. Do not invent qualitative facts.
- Missing-data limitations. In particular, if capex is missing, explicitly say owner earnings cannot be judged.
- A student-decision line left unanswered for the student.

Use numeric literals exactly as printed, including units and percent signs. Do not insert uncomputed growth rates, valuations, ROE averages or additional estimates. Do not use spelled-out quantities to evade the numeric audit.

Audit with `python PATH_TO_SKILL/scripts/sec_facts.py TICKER --root OUTPUT --offline --memo OUTPUT/runs/TICKER/memo.md`. Fix unsupported numbers before delivery. The audit checks number membership, not whether a number supports a particular claim; manually check its year, metric and unit too.

Save `memo_meta.json` beside the memo containing `ticker`, the report's `report_id`, `memo_sha256` (SHA-256 of the memo file bytes), and `ai_disclosure`. A refreshed report needs a fresh review and binding; never silently carry a verdict to another company.

## Sources and interpretation
[Buffett's FAskills page](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/warren_buffett.md) motivates durable earnings, understandable economics, disciplined capital allocation and patient ownership. This course restricts that broader philosophy to business analysis and the simpler cash-flow proxy.
[SEC API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces).

