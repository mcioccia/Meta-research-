> **AI-use disclosure:** The checker, automated verification, candidate D proposal and worksheet structure were prepared with OpenAI Codex assistance. AI-generated work can contain errors; the student must read the code and verify the work. Sections explicitly reserved for independent student work are blank and are not claimed as completed.
>
> **Educational purposes only. Not financial or investment advice, and not a recommendation to buy, sell or hold any security.**

# Lab 13 — Meridian Foundation Reserve: mandate defense

Prepared October 15, 2026. Fictional common case only; no META or Visa company inputs are used. **Status: checker and tests complete; independent written work pending.** Files are saved locally as requested. No GitHub submission has been made.

## The question

Which of these portfolios does the Meridian Foundation's mandate permit—and what must the CIO answer before anyone optimizes?

The checker reports whether each candidate passes the **five computable allocation tests** in the assignment. It does not certify full mandate suitability or select an optimal portfolio.

## Sources and units

- The Meridian statements, permitted holdings, candidates A–C and expected results are from the Lab 13 instructions supplied in this conversation.
- Required [IPS prework reading](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-08/student-prework.md): browser retrieval failed during preparation. Its contents have not been verified or summarized. Open and read it yourself before completing the reading reflection.
- Portfolio size and payouts use **USD millions**. Weights and thresholds use **percentage points of portfolio value**, so 2 means 2%, not 0.02. Redemption periods use **business days**.
- The case expressly makes the Treasury 10-year note reserve-eligible and redeemable in one business day. The checker uses that supplied convention without substituting a different definition.

## Run the checker

From this Lab_13 folder, the lab command is:

```powershell
python mandate.py
```

The ordinary run includes A, B, C and the proposed D. Optional verification commands:

```powershell
python mandate.py --self-test
python mandate.py --probe
```

If `python` is not recognized on this computer, the available interpreter can run it directly:

```powershell
Set-Location -LiteralPath 'C:\Users\mac10\finance-ai-work\Lab_13'
& 'C:\Users\mac10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' '.\mandate.py'
```

Add `--self-test` or `--probe` after `'.\mandate.py'` for those runs. No third-party packages are required.

## Independent work 1 — sort S1–S10 with AI closed

The lab says **“Sort before you build (no AI).”** Complete the type and reason columns yourself. If you are completing this after reviewing the checker, record that honestly rather than claiming you did the sort first.

Choose from **objective**, **hard constraint**, **preference**, **unverifiable promise**, or **missing**. If a statement combines different ideas, explain your treatment in the reason instead of hiding the ambiguity.

| Statement | CIO's words | Your type | Your one-line reason |
|---|---|---|---|
| S1 | Horizon seven years; annual rebalancing. | [Complete independently] | [Your reason] |
| S2 | Objective: CPI + 4% a year, net of costs, over rolling five-year periods. | [Complete independently] | [Your reason] |
| S3 | Pays out $0.75 million every quarter; twelve months of payouts held in cash or daily-liquid government securities. | [Complete independently] | [Your reason] |
| S4 | Benchmark: 60% global equities, 40% U.S. investment-grade bonds. | [Complete independently] | [Your reason] |
| S5 | Long-only: no borrowing, short sales or derivatives. | [Complete independently] | [Your reason] |
| S6 | No single issuer above 8%. | [Complete independently] | [Your reason] |
| S7 | Annual turnover at most 25% without committee approval. | [Complete independently] | [Your reason] |
| S8 | At least 90% redeemable within five business days. | [Complete independently] | [Your reason] |
| S9 | “The reserve cannot have a calendar-year loss greater than 10%.” No measure, no breach rule. | [Complete independently] | [Your reason] |
| S10 | No sector, ESG, tax or home-bias preference; nobody has said what the pilot should optimize. | [Complete independently] | [Your reason] |

Completed without AI on: [date/time]. Actual order of work: [your note].

## Checker scope and verification

The editable inputs are at the top of `mandate.py`. The calculation functions derive all reported measurements from those inputs. Known-answer constants appear only in `self_test()` as independent test expectations; they are not used to produce candidate measurements.

The issuer check groups securities by issuer before applying the limit. Exempt issuers are cash (`none`), U.S. Treasury and diversified funds, following the case. No look-through holdings data is supplied. The liquidity calculation includes holdings redeemable **on or before** the specified window.

Negative weights are allowed through input validation so the long-only rule can detect and report them. The checker does not silently remove or replace them. A tiny numerical tolerance is used for sums and percentage boundaries, but any negative weight fails long-only.

The five reported allocation tests do not establish compliance with every CIO statement:

- Calendar-year loss always prints **“requires CIO clarification”** and is never tested.
- Turnover needs trades, starting holdings and an agreed calculation convention; annual rebalancing needs a schedule/history. Neither can be established from one allocation table.
- No borrowing or derivatives are represented among the permitted holdings. The checker tests the supplied weights; it is not a general detector of embedded leverage or instruments outside the table.
- No return scenarios, CPI series, fees or optimization objective are supplied. The checker does not manufacture them or optimize anything.

### Captured A–D results and automated known-answer tests

This is actual program output, including the reserve minimum and the known-answer verification status.

```text
Reserve minimum: 3.0% of the portfolio
AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
Educational purposes only. Not financial or investment advice, and not a recommendation to buy, sell or hold any security.

Candidate A
  Weights sum to 100: 100.0 pass
  Long-only (lowest weight): 0.0 pass
  Reserve >= 3.0%: 14.0 pass
  Redeemable in 5 days >= 90.0%: 100.0 pass
  Largest single company <= 8.0%: 0.0 pass
  Calendar-year loss: requires CIO clarification
  Verdict: passes every checkable rule

Candidate B
  Weights sum to 100: 100.0 pass
  Long-only (lowest weight): 0.0 pass
  Reserve >= 3.0%: 1.0 FAIL
  Redeemable in 5 days >= 90.0%: 85.0 FAIL
  Largest single company <= 8.0%: 9.0 FAIL
  Calendar-year loss: requires CIO clarification
  Verdict: fails 3 rule(s)

Candidate C
  Weights sum to 100: 100.0 pass
  Long-only (lowest weight): 0.0 pass
  Reserve >= 3.0%: 2.0 FAIL
  Redeemable in 5 days >= 90.0%: 100.0 pass
  Largest single company <= 8.0%: 8.0 pass
  Calendar-year loss: requires CIO clarification
  Verdict: fails 1 rule(s)

Candidate D
  Weights sum to 100: 100.0 pass
  Long-only (lowest weight): 0.0 pass
  Reserve >= 3.0%: 100.0 pass
  Redeemable in 5 days >= 90.0%: 100.0 pass
  Largest single company <= 8.0%: 0.0 pass
  Calendar-year loss: requires CIO clarification
  Verdict: passes every checkable rule

Scope: these are static checks, not full mandate approval. Turnover and rebalancing need trade/history data; return and loss outcomes are not tested.

SELF-TEST PASS: known answers A-C; D; negative-weight probe; issuer/liquidity boundaries; base inputs unchanged.
```

### Negative-weight probe and restoration

`--probe` sets A's Cash to **−2** and Global equity index fund to **64** in a fresh copy. The saved base inputs remain unchanged. It prints the altered A, then the original A, showing the restoration explicitly. You may instead make and undo the two edits manually as described in the lab.

```text
Reserve minimum: 3.0% of the portfolio
AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
Educational purposes only. Not financial or investment advice, and not a recommendation to buy, sell or hold any security.

Candidate A (temporary negative-weight probe)
  Weights sum to 100: 100.0 pass
  Long-only (lowest weight): -2.0 FAIL
  Reserve >= 3.0%: 10.0 pass
  Redeemable in 5 days >= 90.0%: 100.0 pass
  Largest single company <= 8.0%: 0.0 pass
  Calendar-year loss: requires CIO clarification
  Verdict: fails 1 rule(s)

Candidate A (restored base; saved inputs unchanged)
  Weights sum to 100: 100.0 pass
  Long-only (lowest weight): 0.0 pass
  Reserve >= 3.0%: 14.0 pass
  Redeemable in 5 days >= 90.0%: 100.0 pass
  Largest single company <= 8.0%: 0.0 pass
  Calendar-year loss: requires CIO clarification
  Verdict: passes every checkable rule

Scope: these are static checks, not full mandate approval. Turnover and rebalancing need trade/history data; return and loss outcomes are not tested.
```

Automated verification also tests the issuer threshold just above 8%, liquidity exactly at 90% and just below it, and preservation of the original candidate inputs.

## AI-proposed attack: candidate D

| Holding | D weight (%) |
|---|---:|
| Cash | 0 |
| Treasury bills | 0 |
| Treasury 10-year note | 100 |
| Global equity index fund | 0 |
| Investment-grade bond fund | 0 |
| Private real estate fund | 0 |
| Acme Corp bonds | 0 |
| Acme Corp stock | 0 |

**AI's proposed objection:** D concentrates the entire reserve in a long-maturity government note. The case's daily redemption and reserve-eligibility flags do not guarantee a stable sale price. Interest-rate movements could cause mark-to-market losses even though the holding remains liquid and exempt from the issuer cap. This exposes **S9's undefined loss measure and response**, and **S10's missing optimization objective**. The CIO could reasonably withhold approval until those issues are resolved.

This is a proposed challenge for you to evaluate, not a finding that D certainly loses more than 10%. There is no yield, duration or return scenario in the case from which to compute such a loss. A ten-year maturity does not by itself make the holding unredeemable within the seven-year horizon. No new mandate limits have been invented to make D fail.

### Independent work 2 — judge the attack with AI closed

Write **two sentences** in your own words:

1. Does the objection hold? [Your judgment and reason.]
2. Which CIO statement decides it? [Name the statement and explain its consequence.]

For this solo lab, play the skeptical-colleague role yourself. Statement you would cite against the proposed D: [Your own answer]. Do not claim a partner exchange occurred if it did not.

## Independent work 3 — the one question for the CIO

With AI closed, write **one** question that must be answered before optimization, then state the answer that would change your design.

**My one question:** [Your question.]

**The answer that would change my portfolio or rules:** [Your answer and the specific design consequence.]

## IPS reading and reflection

General study note, not a summary of the unavailable reading: an investment policy statement is a written agreement defining an investor's objectives, constraints, responsibilities and review process. Objectives describe intended outcomes; constraints limit allowable choices; monitoring rules explain how compliance and breaches are handled. A measurable rule needs defined inputs, units, timing and a decision rule.

After reading the assigned prework, explain these in your own words:

1. **What is an IPS?** [Your explanation.]
2. **How do its objectives and constraints work together?** [Your explanation.]
3. **Map S1–S10 onto the IPS.** Refer to your classification table above; identify any wording that requires clarification. [Your explanation.]
4. **Why can a portfolio pass every checkable rule and still be wrong for this client?** [Your reflection.]
5. **Which statement type were you least sure of, and why?** [Your reflection.]

## Payout-reserve quiz — answer before AI explains

You selected the payout-reserve calculation for practice. This hypothetical does **not** change the Meridian model:

If the reserve were **$80 million**, quarterly payouts stayed at **$0.75 million**, and four quarters must be covered, how many dollars and what percentage of the reserve are required?

**Your calculation and answer:** [Answer here or in the chat before requesting the explanation.]

## Project 2 — your own client's mandate, separate from Meridian

AI assistance is permitted for this later section. Your own client's facts have not been supplied, so this is a template, not an invented client mandate.

- **Client and portfolio purpose:** [Who and what the money is for.]
- **Objective:** [Metric, target, horizon, measurement period, cost/inflation treatment.]
- **Hard constraints:** [Amounts or percentages, dates, liquidity, concentration, permitted instruments and any required approvals.]
- **One question for the client:** [The unresolved decision and how alternative answers change the design.]

## Completion and delivery

| Item | Status |
|---|---|
| Standard-library `mandate.py`; results computed from inputs | Complete |
| A–C match every supplied measurement and verdict | Verified by automated checks |
| Negative-weight probe fails only long-only; A restored | Verified |
| Candidate D added, run and passes | Verified; suitability judgment still yours |
| S1–S10 types and reasons | Pending independent student work |
| Your two-sentence judgment of D | Pending independent student work |
| Your one CIO question and design consequence | Pending independent student work |
| IPS reading, mapping and reflections | Pending student work; reading link could not be fetched |
| Payout-reserve quiz answer | Pending |
| Own-client Project 2 mandate | Client details needed |
| GitHub links for checkout | Not published; local-only saving requested |

The lab requires GitHub links to the completed Markdown and `mandate.py`. Local files are preparation, not a completed GitHub submission. Complete the independent sections before submitting; there is no claim that this worksheet already satisfies all five merit criteria.
