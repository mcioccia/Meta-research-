# Lab 16 — What was knowable on the decision date?

> AI-use disclosure: Prepared with OpenAI Codex assistance; verify calculations and conclusions.
>
> Educational purposes only. Not financial or investment advice.

Prepared October 27, 2026. Source: the fictional 12-row card-spend training table and rules supplied in the course instructions. These are not company or market observations.

## Run

Open PowerShell:

```powershell
cd C:\Users\mac10\finance-ai-work\Lab_16
python asof.py
python asof.py --self-test
python asof.py --decision-date 2026-04-15
python asof.py
```

The file uses the Python standard library only. Edit TABLE and DECISION_DATE at the top, or use the optional date argument. The date argument changes only that run; it does not change the saved March 31 default.

## Verified March 31 results

| Rule | Removed count | Row numbers | Remaining count |
| --- | ---: | --- | ---: |
| Missing ticker quarantined | 1 | 11 | 11 |
| Exact duplicate removed | 1 | 7 | 10 |
| Published after decision date | 3 | 3, 8, 10 | 7 |
| Older publication replaced | 1 | 2 | 6 |

Remaining row IDs: **1, 4, 5, 6, 9, 12**.

| Ticker | As-of signal | Naive signal |
| --- | --- | --- |
| AAA | +1.98% (February 2026) | +5.83% (March 2026) |
| BBB | -1.02% (February 2026) | -5.15% (March 2026) |
| CCC | +0.91% (February 2026) | +1.82% (February 2026, later revision) |

Each signal is `(latest month index / previous month index - 1) * 100`. Naive retains the missing-ticker and duplicate cleaning, but selects the latest publication without the decision-date cutoff. Missing prior months and zero denominators produce an unavailable signal instead of an invented value.

## Later-date test

With April 15, 2026 as the decision date, all publications in this supplied table are available. The as-of signals become +5.83%, -5.15%, and +1.82%, matching the naive results ticker for ticker. This equality applies to the supplied table, not to arbitrary future data.

The program and automated tests were run with AI assistance. A separate human partner run has not been claimed. The default March 31 run was repeated after the later-date probe.

## What the evidence means

The measured month identifies the economic period. The publication date identifies when that version was available. A March observation first published in April cannot inform a March 31 decision. A later revision can also change what today's dataset says about an older month.

Using information published after the decision date creates look-ahead bias. The gap between these columns shows the effect of later information, though AAA and BBB also compare different latest measured months. The rule uses day-level dates and includes publication on the decision day; it does not establish whether a release arrived before a specific intraday trade.

## Checks and saved evidence

- `Lab_16_base_output.txt`: March 31 funnel, remaining panel and signals.
- `Lab_16_later_date_output.txt`: April 15 panel and signals.
- `Lab_16_test_output.txt`: known-answer checks, April 15 comparison, inclusive publication-date boundary and restored base.
- `asof.py`: editable inputs, filtering, signals, reporting and optional self-test in one file.

Duplicate detection ignores row ID because the ID identifies the record rather than its economic content. Conflicting values for the same ticker/month/publication date are refused. Known-answer numbers occur only in the test expectations; report values are calculated from the editable table.

## Personal exercises still to complete

- No-screen explanation with partner: pending.
- Line-by-line explanation of `latest_publications` with AI closed: pending.
- Partner's actual question and your answer: pending.
- Partner's own later-date run: pending.
- Quiz topic selected: keeping the latest available revision.
- Quiz answer: pending. Which AAA February row should remain on March 31, and why?

This document records completed calculations separately from personal exercises. Files are saved locally; GitHub upload/submission has not been performed.

