# Lab 18 — Buffett-inspired business-quality skill

AI-use disclosure: Prepared with OpenAI Codex assistance; verify all sources, calculations and judgments.
Educational purposes only. Not financial or investment advice.

## Current status

The SEC skill, calculation script, Streamlit app and company memos are complete and tested. COST's downloaded fiscal periods ending 2022-08-28 through 2026-08-30 match every course table value and pass all three checks. JPM's downloaded fiscal periods end 2021-12-31 through 2025-12-31: its required capex tags are missing, owner earnings is not found, and the owner-earnings checks are not known. Its every-year ROE test fails.

Both AI memos use only printed numbers and pass the numeric audit. The app was tested with the live downloaded reports; adding 40.0% produced the warning, and restoring the memo cleared it. Each memo is bound to its ticker, calculated report and saved text. SEC identity is saved privately under the ignored .local folder.

**Still yours to complete:** the partner explanation and fresh-chat comparison. Your personal trust decision is saved beneath COST’s memo and in [Trust Buffett?](<Trust Buffett.md>). GitHub submission remains pending.

## Files and purpose

- `buffett-sec-review/SKILL.md`: repeatable instructions for the AI.
- `buffett-sec-review/scripts/sec_facts.py`: downloads SEC sources, selects annual facts, computes ratios/checks and audits numeric literals.
- `app.py`: financial record, cash-generation chart, three checks, filing evidence and memo audit.
- `setup_sec.py`: collects your SEC requester name/email and saves it only in ignored local settings.
- `test_sec_facts.py`: synthetic rule tests.
- `test_app.py`: synthetic Streamlit test, including the invented ROE probe.
- `verify_live.py`: compares actual downloaded COST and JPM reports with the course expectations. Expected answers exist only in this validation file.
- `verification.txt`: saved synthetic test results from the build.
- `live_verification.txt`: passing COST/JPM known-answer checks.
- `app_verification.txt`: live app and invented-number probe results.
- `runs/TICKER/report.md` and `report.json`: saved SEC calculations, with fiscal periods, tags, values and filing links.
- `runs/TICKER/memo.md` and `memo_meta.json`: saved AI judgments bound to the corresponding calculated reports.
- `sources/`: downloaded SEC JSON with URL, UTC download timestamp and SHA-256 integrity hash.

The installed project skill is at `Lab_18/.agents/skills/buffett-sec-review`. Open Lab_18 as your Codex project so this skill is discoverable. A submission/runtime copy is in `buffett-sec-review`; the copies were verified identical. The personal skills directory could not be created with the available filesystem access, so the project-scoped location is used. Invoke it as `$buffett-sec-review`; restart Codex if needed.

## Run from PowerShell

Stay in Lab_18, not inside a virtual-environment folder.

```powershell
cd C:\Users\mac10\finance-ai-work\Lab_18
& ..\Lab_14\.venv\Scripts\python.exe setup_sec.py
& ..\Lab_14\.venv\Scripts\python.exe buffett-sec-review\scripts\sec_facts.py COST --root .
& ..\Lab_14\.venv\Scripts\python.exe buffett-sec-review\scripts\sec_facts.py JPM --root .
& ..\Lab_14\.venv\Scripts\python.exe verify_live.py
& ..\Lab_14\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8504
```

For future reruns, ask Codex: "Use $buffett-sec-review on COST and JPM. Use Lab_18 as the output folder, review the printed SEC reports, save each memo and its binding, and audit the memo."

The SEC downloader needs no API key. Your name and email identify the requester in its User-Agent. Keep `.local/` out of GitHub. The downloader never prints that header.

Use `--offline` to rerun saved sources, or `--refresh` to fetch new filings. A changed source/report makes an earlier memo stale until reviewed again. The app's memo editor is a temporary probe; it does not overwrite the reviewed file.

## What is computed

For each of the latest five annual fiscal periods:
- Revenue, net income, operating cash flow, capital spending and equity come from the specified US-GAAP XBRL tags, in USD.
- Annual flows must span 335–395 days; this accepts ordinary and retail week-based fiscal years and excludes quarterly figures.
- Only exact 10-K forms qualify. Comparative values belong to their actual period end, not the filing's reporting-year label.
- Latest filing wins for the same period. Within that filing, the required primary tag is preferred to its fallback.
- ROE = net income / year-end equity.
- Owner earnings = operating cash flow − capital spending.
- Optional liabilities/equity uses the Liabilities tag and year-end StockholdersEquity.

Missing facts stay **not found**. Missing check inputs or nonpositive equity make the applicable check/ratio **not known**. No price, P/E, DCF or invented company estimate is used.

The cash-flow measure is the lab's simplified owner-earnings proxy. It does not separate maintenance from growth capital spending. Passing its checks is a screening result, not proof of a durable moat or a sound investment at any price.

## Number audit and its limitation

The app compares every numeric literal in the memo with the printed script report. It recognizes dates, percentages, signs, decimals, comma-separated values and scientific notation. Repeated unsupported occurrences are listed separately. The deliberate `40.0%` probe is tested.

This is a membership check, not a complete fact checker: a real number attached to the wrong year, metric or unit still needs human review. The skill prohibits spelling out unprinted quantities to evade the audit. The app also checks a memo's ticker, report identity and file hash before treating it as a saved reviewed memo.

## Live validation checklist — performed by AI/tools

- [x] Supply SEC requester identity privately.
- [x] Download COST and save its printed output.
- [x] Check every course value and all three Buffett checks against actual SEC output.
- [x] Download JPM; verify missing capex/owner earnings and unknown owner-earnings checks if the actual tags support that result.
- [x] Save both AI memos using only printed numbers.
- [x] Audit both memos and bind them to the matching reports.
- [x] Add 40.0% in the app's temporary memo editor; observe the warning, then restore.
- [x] Read the live chart and table; confirm their fiscal coverage.

If live SEC results differ from the course table, retain the source values and investigate dates, tags and filing revisions. Never paste the expected answers into the engine.

## Student work — complete yourself

These are prompts, not claimed completed exercises.

**Explain to your partner:** identify something code computes and something the analyst must judge.

**Explain the code:** open `year_row` and trace where missing inputs lead to None internally and "not found"/"not known" in the report. Explain the difference between year-end equity and average equity.

**Fresh-chat probe:** save the exact unassisted question, answer and sources from a separate chat; compare them with the SEC table. This exercise has not been run or fabricated.

**Your decision (write beneath COST's memo):** Do you trust the verdict on COST, and why?
Your answer: I would agree with the Buffett-inspired verdict because I see significant growth in the grocery sector as grocery prices rise and consumers continue to look for cheaper, more affordable options. See [Trust Buffett?](<Trust Buffett.md>).

## Submission

Submit GitHub links to this Markdown file, the skill folder, the script and app, the actual saved reports/memos, and the validation output. Do not submit private SEC identity settings, the virtual environment or temporary test packages. No GitHub push has been performed.

## Sources

- [Buffett page in FAskills](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/warren_buffett.md) — read for philosophy only; FAskills was not installed and its paid data services were not used.
- [SEC EDGAR API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces).
- [SEC ticker-to-CIK map](https://www.sec.gov/files/company_tickers.json).
- [SEC company-facts endpoint example for Costco](https://data.sec.gov/api/xbrl/companyfacts/CIK0000909832.json) — retrieved and retained in sources/.
- [Codex skill documentation](https://developers.openai.com/codex/skills) — project skills live under .agents/skills; personal skills use ~/.agents/skills.
- [Streamlit documentation](https://docs.streamlit.io).

Prepared and verified 2026-11-03. Source download timestamps (UTC):

- COST: 2026-11-03T19:00:33.485305+00:00
- JPM: 2026-11-03T19:00:49.105534+00:00

