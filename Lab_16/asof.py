"""Lab 16: fictional card-spend index, filtered by publication date.
AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
Educational purposes only. Not financial or investment advice.
"""
import argparse
from datetime import date
import math

# Editable inputs: row number, ticker, month measured, published on, index.
TABLE = [
    (1, "AAA", "2026-01", "2026-02-10", 101.0),
    (2, "AAA", "2026-02", "2026-03-10", 104.0),
    (3, "AAA", "2026-03", "2026-04-10", 109.0),
    (4, "AAA", "2026-02", "2026-03-25", 103.0),
    (5, "BBB", "2026-01", "2026-02-10", 98.0),
    (6, "BBB", "2026-02", "2026-03-10", 97.0),
    (7, "BBB", "2026-02", "2026-03-10", 97.0),
    (8, "BBB", "2026-03", "2026-04-10", 92.0),
    (9, "CCC", "2026-01", "2026-02-10", 110.0),
    (10, "CCC", "2026-02", "2026-04-05", 112.0),
    (11, "", "2026-02", "2026-03-10", 99.0),
    (12, "CCC", "2026-02", "2026-03-10", 111.0),
]
DECISION_DATE = "2026-03-31"
AI_NOTICE = "AI-use disclosure: Prepared with OpenAI Codex assistance; verify results."
NOTICE = "Educational purposes only. Not financial or investment advice."


def clean_rows(table):
    """Rules 1 and 2. Duplicate identity excludes the record's row number."""
    rows, missing, duplicates = [], [], []
    seen, ids = set(), set()
    for number, ticker, month, published, value in table:
        if number in ids:
            raise ValueError(f"Duplicate row number: {number}")
        ids.add(number)
        ticker = ticker.strip()
        if not ticker:
            missing.append(number)
            continue
        measured = date.fromisoformat(month + "-01")
        publication = date.fromisoformat(published)
        if measured.strftime("%Y-%m") != month or not math.isfinite(value):
            raise ValueError(f"Row {number}: invalid month or index")
        key = (ticker, month, publication, value)
        if key in seen:
            duplicates.append(number)
            continue
        seen.add(key)
        rows.append(dict(row=number, ticker=ticker, month=month,
                         published=publication, index=value))
    return rows, missing, duplicates


def latest_publications(rows):
    """Rule 4. For an as-of panel, rows must already satisfy the cutoff."""
    latest = {}
    for row in rows:
        key = (row["ticker"], row["month"])
        previous = latest.get(key)
        if previous is None or row["published"] > previous["published"]:
            latest[key] = row
        elif row["published"] == previous["published"] and row["index"] != previous["index"]:
            raise ValueError(f"Conflicting same-date publications for {key}")
    panel = sorted(latest.values(), key=lambda row: (row["ticker"], row["month"]))
    kept = {row["row"] for row in panel}
    replaced = sorted(row["row"] for row in rows if row["row"] not in kept)
    return panel, replaced


def build_panels(table, cutoff):
    clean, missing, duplicates = clean_rows(table)
    # Rule 3 comes before rule 4, so future revisions cannot displace known data.
    available = [row for row in clean if row["published"] <= cutoff]
    future = [row["row"] for row in clean if row["published"] > cutoff]
    panel, replaced = latest_publications(available)
    # Naive still cleans missing/duplicate records, but ignores the cutoff.
    naive, _ = latest_publications(clean)
    funnel = [("Quarantined: no ticker", missing), ("Exact duplicate", duplicates),
              ("Published after decision date", future),
              ("Older vintage replaced by a revision", replaced)]
    assert sum(len(numbers) for _, numbers in funnel) + len(panel) == len(table)
    return panel, naive, funnel


def signals(panel):
    groups = {}
    for row in panel:
        groups.setdefault(row["ticker"], []).append(row)
    result = {}
    for ticker, rows in sorted(groups.items()):
        rows = sorted(rows, key=lambda row: row["month"])
        latest = rows[-1]
        if len(rows) < 2:
            result[ticker] = (latest["month"], None, "fewer than two months")
            continue
        previous = rows[-2]
        current = date.fromisoformat(latest["month"] + "-01")
        prior = date.fromisoformat(previous["month"] + "-01")
        gap = (current.year-prior.year)*12 + current.month-prior.month
        if gap != 1:
            result[ticker] = (latest["month"], None, "previous calendar month unavailable")
        elif previous["index"] == 0:
            result[ticker] = (latest["month"], None, "previous index is zero")
        else:
            result[ticker] = (latest["month"], (latest["index"]/previous["index"]-1)*100, "")
    return result


def show_signal(value):
    if value is None:
        return "unavailable: no rows"
    month, change, reason = value
    label = date.fromisoformat(month+"-01").strftime("%B %Y")
    return f"{change:+.2f}% ({label})" if change is not None else f"unavailable ({label}: {reason})"


def report(table, cutoff):
    panel, naive, funnel = build_panels(table, cutoff)
    print(f"\nDecision date: {cutoff} (publications on this date are included)")
    print(f"Input rows: {len(table)}\n\nROW FUNNEL")
    remaining = len(table)
    for label, numbers in funnel:
        remaining -= len(numbers)
        print(f"{label}: removed {len(numbers)}; rows {', '.join(map(str,numbers)) or 'none'}; remaining {remaining}")
    print(f"As-of panel: {len(panel)} rows; {', '.join(str(r['row']) for r in panel)}")
    print("\nAS-OF PANEL")
    print(f"{'Row':>3}  {'Ticker':<6}  {'Measured':<10}  {'Published':<10}  {'Index':>7}")
    for r in panel:
        print(f"{r['row']:>3}  {r['ticker']:<6}  {r['month']:<10}  {str(r['published']):<10}  {r['index']:>7.1f}")
    actual, hindsight = signals(panel), signals(naive)
    print("\nSIGNALS: (latest month / previous month - 1) x 100")
    print(f"{'Ticker':<8}{'As-of':<30}Naive (ignores publication cutoff)")
    for ticker in sorted(set(actual) | set(hindsight)):
        print(f"{ticker:<8}{show_signal(actual.get(ticker)):<30}{show_signal(hindsight.get(ticker))}")
    print("Naive still cleans missing tickers and exact duplicates.")
    print("Both panels select the latest publication per ticker and measured month.")


def self_test():
    """Known answers are test expectations; report values are computed from TABLE."""
    base = date(2026,3,31)
    panel, naive, funnel = build_panels(TABLE,base)
    assert [numbers for _,numbers in funnel] == [[11],[7],[3,8,10],[2]]
    assert [row["row"] for row in panel] == [1,4,5,6,9,12]
    actual, hindsight = signals(panel), signals(naive)
    expected = {"AAA":("+1.98","+5.83"), "BBB":("-1.02","-5.15"), "CCC":("+0.91","+1.82")}
    for ticker,(a,n) in expected.items():
        assert f"{actual[ticker][1]:+.2f}" == a
        assert f"{hindsight[ticker][1]:+.2f}" == n
    print("PASS: base funnel, panel and six signals match the course answer.")
    later, later_naive, _ = build_panels(TABLE,date(2026,4,15))
    assert later == later_naive and signals(later) == hindsight
    print("PASS: April 15 as-of equals naive for every ticker.")
    before,_,_ = build_panels(TABLE,date(2026,3,24))
    on_date,_,_ = build_panels(TABLE,date(2026,3,25))
    assert next(r["row"] for r in before if r["ticker"]=="AAA" and r["month"]=="2026-02") == 2
    assert next(r["row"] for r in on_date if r["ticker"]=="AAA" and r["month"]=="2026-02") == 4
    print("PASS: cutoff includes decision day and excludes later revisions.")
    assert build_panels(TABLE,base) == (panel,naive,funnel)
    print("PASS: base restored; input table and default date unchanged.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision-date", default=DECISION_DATE, help="YYYY-MM-DD")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    print(AI_NOTICE)
    print(NOTICE)
    print("Fictional course training data; not retailer or market observations.")
    try:
        report(TABLE,date.fromisoformat(args.decision_date))
        if args.self_test:
            print("\nVERIFICATION")
            self_test()
    except ValueError as error:
        parser.exit(1,f"REFUSED: {error}\n")


if __name__ == "__main__":
    main()

