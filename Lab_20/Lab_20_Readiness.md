I used OpenAI Codex to help check my repository, resolve a setup error when opening my partner’s app, and draft this readiness record. The analysis and investment decision are mine. Partner observations and my AI-off prediction remain identified below where they are unresolved.

This is an educational course project. It is not financial or investment advice.

# Lab 20 — Project 2 Readiness

Matt Cioccia · November 17, 2026

## My decision

**Pilot the process on paper, starting with 65% BIL and 35% equities. Pause if the mandate becomes infeasible or usable signal evidence is missing, and request committee review if any fund moves at least 20 percentage points across estimation windows.**

The base equity allocation is 15% QQQ, 5% ONEQ and 15% VUG. IEF and LQD receive zero. A funded allocation would require committee confirmation of loss tolerance and review of forward paper results after costs.

## Repository and current result

[My Project 2 repository](https://github.com/mcioccia/Amazon-Project-2) · [README](https://github.com/mcioccia/Amazon-Project-2/blob/main/README.md)

The model uses the October 30, 2026 decision snapshot, prices through September 30, 2026, and a 7.49% first-year net return target. The base trading charge is 10 basis points per dollar switched from equal weight. The reserve starts at 3% BIL and rises to 10% under the selected CPI signal.

| Portfolio | Estimated first-year net return | Estimated annual volatility | Mandate verdict |
|---|---:|---:|---|
| Equal weight | 7.494% | 12.138% | Pass |
| Inverse volatility | 3.775% | 1.999% | Fail — return below target |
| Constrained | 7.498% | 7.241% | Pass |

The constrained portfolio clears the target by 0.80 basis points. Across the 59-, 48- and 36-month estimation windows, BIL ranges from 65% to 85%, with the complementary equity weight from 35% to 15%. A 90% BIL minimum leaves no feasible mix.

[Saved base and stresses](https://github.com/mcioccia/Amazon-Project-2/blob/main/outputs/committee-run.json) · [Decision memo](https://github.com/mcioccia/Amazon-Project-2/blob/main/docs/decision-memo.md)

## Readiness check

| Item | Evidence and status |
|---|---|
| Runnable app and startup instructions | Present. README provides download, installation and launch steps. Partner execution of my repository remains unconfirmed. |
| Visible output | Base and stress results are saved in the linked JSON file and summarized above. |
| Decision memo | Present with the same base results and conditional paper-pilot decision. |
| Validation and AI use | Present, including checks and my $48.33 personal calculation. |
| Locked Changed-Input Record | Unresolved. The completed 10-to-25 bp practice prediction was AI-assisted. A new personal prediction committed before its run is still needed. |
| Videos 1–3 | Recording guides are prepared. Final YouTube links, runtimes and corrected transcripts have not been provided in this record. |
| Access | Repository is private. Partner and instructor access must be confirmed. |
| Week 12 must-fix list | Unresolved. The studio list has not been supplied for this review. |

[Validation record](https://github.com/mcioccia/Amazon-Project-2/blob/main/docs/validation-and-ai-use.md) · [Submission manifest](https://github.com/mcioccia/Amazon-Project-2/blob/main/docs/manifest.md)

## Partner cold run of my repository

**Awaiting my partner’s own observations.** The recorded startup error below occurred while I opened my partner’s project.

| Partner records after following only my README | Entry |
|---|---|
| Partner name and date | Pending |
| Repository commit tested | Pending |
| Command used | Pending |
| First failure, or confirmation that the run was clean | Pending |
| Elapsed time | Pending |
| Where the result appeared | Pending |
| One control moved and the mandate verdict observed | Pending |
| Fix required and rerun outcome | Pending |

The partner should record what actually happened, including a clean run if applicable. A question requiring coaching identifies an instruction to improve in the README.

## My review of my partner’s project

Partner repository — [Drew Scheiderer’s Foundation Reserve Portfolio](https://github.com/dscheid7717/project2-portfolio).

On November 17, I initially ran the setup commands from **C:\Users\mac10**. Installing from requirements.txt failed because that file was absent in that folder. The subsequent launch failed with **No module named streamlit**.

With Codex assistance, the repository was cloned into **C:\p2**, a Python 3.12 virtual environment was created there, and its requirements were installed successfully. The analysis command reproduced the base report. The Streamlit server then started at **http://127.0.0.1:8507/**, and I opened that address in my browser.

Commands used for the successful setup and launch:

~~~powershell
git clone https://github.com/dscheid7717/project2-portfolio C:\p2
cd C:\p2
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8507 --server.headless true --browser.gatherUsageStats false
~~~

The port was selected for this local session. Total elapsed time was not measured. My reading of the rendered verdict and a changed-control result in his app remain to be recorded. This setup was assisted by AI.

## One readiness improvement pushed

My README now explains how to download and extract the repository, open a terminal in the folder containing app.py and requirements.txt, start the app, and open its local address. It also explains private repository access and the Python version.

This is a documentation improvement prompted by today’s setup experience. Confirmation that it resolves my partner’s first failure in my repository is pending.

[README improvement commit](https://github.com/mcioccia/Amazon-Project-2/commit/848206a4c79a7d6c2f8426c45e0c1365857dae06)

## Locked Changed-Input Record

**Status — unresolved.** Complete the prediction with AI closed, then commit and push it before running a new scenario. The previously observed 25 bp practice run and saved stresses are already known. Preserve the base output, record the new output, and commit the result separately.

| Before the run — my own prediction | Entry |
|---|---|
| One input, old value, new value and units | Pending |
| All held-fixed inputs | Pending |
| Direction expected for a named result | Pending |
| Expected effect on my pilot decision | Pending |
| My economic reason | Pending |
| Pre-run commit URL and timestamp | Pending |

| After the run | Entry |
|---|---|
| Command or app settings and run time | Pending |
| Base and changed output links | Pending |
| Actual change in the named result, with units | Pending |
| Decision changed or remained the same, and why | Pending |
| Why the result matched or differed from my prediction | Pending |
| Post-run commit URL | Pending |

## Code explanation and reflection

To prepare for the code explanation, open **analysis.py → calculate()**, then follow **portfolio.py → search_portfolios()**. Explain how the net return, reserve test and volatility ranking produce the proposed allocation. Partner question and my answer remain pending.

| Personal reflection | Entry |
|---|---|
| What did my partner’s cold run reveal that I missed? | Pending my partner’s review |
| What will I leave fixed before the deadline? | Pending my own response |

## Submission status

This record preserves completed evidence and truthful unresolved items. The partner cold run of my repository, personal prediction and result, code discussion, reflection, and final video evidence still require completion or an updated unresolved status. Lab 20 permits truthful unresolved items, and its completion does not approve Project 2.
