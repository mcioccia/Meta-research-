"""Lab 18 SEC-only business-quality calculations.
AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
Educational purposes only. Not financial or investment advice.
"""
import argparse
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from pathlib import Path
import re
import time
from urllib.request import Request, urlopen

NOTICE = "AI-use disclosure: Prepared with OpenAI Codex assistance; verify results. Educational purposes only. Not financial or investment advice."
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
TAGS = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"],
    "net_income": ["NetIncomeLoss"],
    "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities"],
    "capital_spending": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"],
    "equity": ["StockholdersEquity"],
    "liabilities": ["Liabilities"],
}
FLOWS = {"revenue", "net_income", "operating_cash_flow", "capital_spending"}
CHECK_NAMES = ["ROE at least 15.0% every year", "Owner earnings positive every year",
               "Owner earnings grew from first year to last"]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def valid_ticker(value):
    value = value.strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,14}", value):
        raise ValueError("Enter a ticker containing letters, digits, a dot or a hyphen.")
    return value


def read_identity(config):
    import os
    identity = os.environ.get("SEC_USER_AGENT", "").strip()
    if not identity and Path(config).exists():
        identity = json.loads(Path(config).read_text(encoding="utf-8-sig")).get("user_agent", "").strip()
    if not re.search(r"\S+\s+[^\s@]+@[^\s@]+\.[^\s@]+", identity):
        raise ValueError("Set SEC_USER_AGENT to your name and email, or fill .local/sec_identity.json. No SEC request was sent.")
    if any(x in identity.lower() for x in ("example.com", "your-email", "<email>", "your name")):
        raise ValueError("Replace the sample User-Agent with your actual name and email.")
    return identity


def source_json(url, cache_path, identity=None, refresh=False, offline=False):
    cache_path = Path(cache_path)
    if cache_path.exists() and not refresh:
        wrapper = json.loads(cache_path.read_text(encoding="utf-8"))
        if wrapper.get("url") != url or wrapper.get("sha256") != digest(wrapper.get("data")):
            raise ValueError("Cached SEC source failed its URL/hash check.")
        return wrapper
    if offline:
        raise ValueError("Saved SEC source is missing. Download it first.")
    if not identity:
        raise ValueError("A name and email are required for the SEC User-Agent.")
    # Serialize requests and stay comfortably below SEC's published limit.
    time.sleep(0.2)
    with urlopen(Request(url, headers={"User-Agent": identity, "Accept": "application/json"}), timeout=45) as response:
        data = json.loads(response.read().decode("utf-8-sig"))
    wrapper = {"ai_disclosure": NOTICE, "url": url,
               "downloaded_at": datetime.now(timezone.utc).isoformat(), "sha256": digest(data), "data": data}
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(wrapper), encoding="utf-8")
    return wrapper


def annual(fact):
    try:
        days = (date.fromisoformat(fact["end"]) - date.fromisoformat(fact["start"])).days + 1
        return 335 <= days <= 395
    except (KeyError, ValueError):
        return False


def observations(facts, metric):
    for priority, tag in enumerate(TAGS[metric]):
        for fact in facts.get("facts", {}).get("us-gaap", {}).get(tag, {}).get("units", {}).get("USD", []):
            if fact.get("form") != "10-K":
                continue
            value = fact.get("val")
            if not isinstance(value, (float, int)) or isinstance(value, bool) or not math.isfinite(value):
                continue
            if metric in FLOWS and not annual(fact):
                continue
            if metric not in FLOWS and fact.get("start"):
                continue
            try:
                date.fromisoformat(fact["end"])
                date.fromisoformat(fact["filed"])
            except (KeyError, ValueError):
                continue
            yield {**fact, "tag": tag, "priority": priority}


def missing(metric, reason="No eligible USD fact from a 10-K for this fiscal period."):
    return {"value": None, "tag": None, "reason": reason, "searched_tags": TAGS[metric]}


def choose_fact(facts, metric, end, start=None):
    matches = [f for f in observations(facts, metric) if f["end"] == end
               and (metric not in FLOWS or start is None or f["start"] == start)]
    if not matches:
        return missing(metric)
    # Latest filing wins. Within that filing, apply the specified tag priority.
    latest = max(f["filed"] for f in matches)
    matches = [f for f in matches if f["filed"] == latest]
    accession = max(f.get("accn", "") for f in matches)
    matches = [f for f in matches if f.get("accn", "") == accession]
    priority = min(f["priority"] for f in matches)
    matches = [f for f in matches if f["priority"] == priority]
    if len({(f.get("start"), f["val"]) for f in matches}) != 1:
        return missing(metric, "Conflicting facts in the latest filing; manual review required.")
    f = matches[0]
    cik = int(facts["cik"])
    accn = f.get("accn", "")
    return {"value": f["val"], "tag": f["tag"], "form": "10-K", "unit": "USD",
            "start": f.get("start"), "end": f["end"], "filed": f["filed"], "accession": accn,
            "filing_url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{accn.replace('-', '')}/{accn}-index.html"}


def fiscal_periods(facts):
    # Actual annual duration facts supply the measured FY end. Never use the
    # reporting filing's 'fy' label for a prior-year comparative observation.
    ends = sorted({f["end"] for m in FLOWS for f in observations(facts, m)})[-5:]
    periods = []
    for end in ends:
        start = None
        for metric in ("net_income", "operating_cash_flow", "revenue", "capital_spending"):
            candidates = [f for f in observations(facts, metric) if f["end"] == end]
            if candidates:
                last = max(candidates, key=lambda f:(f["filed"], f.get("accn", ""), -f["priority"]))
                start = last["start"]
                break
        periods.append((start, end))
    return periods


def year_row(facts, start, end):
    fields = {m:choose_fact(facts, m, end, start) for m in TAGS}
    val = lambda m: fields[m]["value"]
    equity = val("equity")
    roe = None if equity is None or equity <= 0 or val("net_income") is None else val("net_income") / equity * 100
    owner = None if val("operating_cash_flow") is None or val("capital_spending") is None else val("operating_cash_flow") - val("capital_spending")
    leverage = None if equity is None or equity <= 0 or val("liabilities") is None else val("liabilities") / equity
    return {"start":start, "fy_end":end, "fields":fields, "roe_percent":roe,
            "owner_earnings":owner, "liabilities_to_equity":leverage}


def checks(rows):
    def every(field, predicate):
        values = [r[field] for r in rows]
        if len(values) != 5 or any(v is None for v in values):
            return "not known"
        return "pass" if all(predicate(v) for v in values) else "fail"
    growth = "not known"
    if len(rows) == 5 and rows[0]["owner_earnings"] is not None and rows[-1]["owner_earnings"] is not None:
        growth = "pass" if rows[-1]["owner_earnings"] > rows[0]["owner_earnings"] else "fail"
    return dict(zip(CHECK_NAMES, [every("roe_percent", lambda v:v >= 15),
        every("owner_earnings", lambda v:v > 0), growth]))


def analyze(facts, ticker, provenance=None):
    rows = [year_row(facts, start, end) for start, end in fiscal_periods(facts)]
    report = {"ai_disclosure":NOTICE, "ticker":valid_ticker(ticker),
              "company":facts.get("entityName", ticker), "cik":int(facts["cik"]),
              "currency_scale":"USD millions", "rows":rows, "checks":checks(rows),
              "source":provenance or {}, "method":"10-K only; latest filing per period; priority tags within latest filing; full-year USD flows; ROE uses year-end equity; owner earnings = OCF minus capex."}
    report["report_id"] = digest(report)
    return report


def amount(value, missing_text="not found"):
    return missing_text if value is None else f"{value/1_000_000:,.3f}".rstrip("0").rstrip(".")


def display_rows(report):
    out = []
    for r in report["rows"]:
        f = r["fields"]
        out.append({"FY end":r["fy_end"], "Revenue":amount(f["revenue"]["value"]),
            "Net income":amount(f["net_income"]["value"]),
            "Operating cash flow":amount(f["operating_cash_flow"]["value"]),
            "Capital spending":amount(f["capital_spending"]["value"]),
            "Equity":amount(f["equity"]["value"]),
            "ROE %":"not known" if r["roe_percent"] is None else f"{r['roe_percent']:.1f}%",
            "Owner earnings":amount(r["owner_earnings"])})
    return out


def render_report(report):
    lines = ["# "+report["ticker"]+" — SEC business-quality report", "", NOTICE, "",
             report["company"], "Currency and scale: USD millions. 10-K only.", report["method"], ""]
    records = display_rows(report)
    if records:
        cols = list(records[0])
        lines += ["| "+" | ".join(cols)+" |", "| "+" | ".join(["---"]*len(cols))+" |"]
        lines += ["| "+" | ".join(row.values())+" |" for row in records]
    else:
        lines.append("No eligible annual data found.")
    lines += ["", "## Code-computed checks", ""]
    lines += [f"- {label}: **{value}**" for label, value in report["checks"].items()]
    lines += ["", "## XBRL evidence by fiscal year", ""]
    for r in report["rows"]:
        lines += ["### "+r["fy_end"], f"Annual flow period: {r['start']} through {r['fy_end']}."]
        for metric, f in r["fields"].items():
            if f["value"] is None:
                lines.append(f"- {metric}: not found. Searched us-gaap tags: {', '.join(f['searched_tags'])}. {f['reason']}")
            else:
                lines.append(f"- {metric}: {amount(f['value'])}; us-gaap:{f['tag']}; filed {f['filed']}; accession {f['accession']}; [10-K]({f['filing_url']}).")
        roe = "not known" if r["roe_percent"] is None else f"{r['roe_percent']:.1f}%"
        lines += [f"- ROE: {roe}; derived from NetIncomeLoss / StockholdersEquity.",
                  f"- Owner earnings: {amount(r['owner_earnings'])}; derived from operating-cash-flow tag minus selected capital-spending tag."]
        lev = "not known" if r["liabilities_to_equity"] is None else f"{r['liabilities_to_equity']:.2f}"
        lines += [f"- Liabilities / equity: {lev}; derived from Liabilities / StockholdersEquity."]
    lines += ["", "The owner-earnings measure is the lab's simplified cash-flow proxy, not a maintenance-capital-spending estimate.",
              "Checks with missing required inputs are not known. Zero or negative equity makes ROE and liabilities/equity not known."]
    return "\n".join(lines)+"\n"


# Scan numeric literals, preserving percentages and ISO dates. Arithmetic is not
# performed by the model. This verifies number membership, not claim semantics.
NUMBER = re.compile(r"(?<![\d.])(?:\d{4}-\d{2}-\d{2}|[+\-−]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\.\d+)(?:[eE][+\-]?\d+)?[ \t]*%?)(?!\d|\.\d)")


def number_key(text):
    text = text.strip().replace("−","-").replace(",","")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}",text):
        return ("date",text)
    unit = "percent" if text.endswith("%") else "number"
    try:
        return (unit,Decimal(text.rstrip("%").strip()))
    except InvalidOperation:
        return ("literal",text)


def audit_memo(text, printed_report):
    allowed = {number_key(m.group()) for m in NUMBER.finditer(printed_report)}
    return [{"number":m.group().strip(), "line":text.count("\n",0,m.start())+1,
             "start":m.start(), "end":m.end()}
            for m in NUMBER.finditer(text) if number_key(m.group()) not in allowed]


def run_ticker(ticker, root, identity=None, refresh=False, offline=False):
    ticker = valid_ticker(ticker)
    root = Path(root)
    ticker_source = source_json(TICKERS_URL, root/"sources"/"company_tickers.json",identity,refresh,offline)
    matches = [r for r in ticker_source["data"].values() if r["ticker"].upper() == ticker]
    if len(matches) != 1:
        raise ValueError("Ticker not uniquely found in SEC's ticker map.")
    cik = int(matches[0]["cik_str"])
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
    source = source_json(url,root/"sources"/f"{ticker}_companyfacts.json",identity,refresh,offline)
    if int(source["data"]["cik"]) != cik:
        raise ValueError("SEC facts CIK differs from ticker map.")
    provenance = {k:source[k] for k in ("url","downloaded_at","sha256")}
    report = analyze(source["data"],ticker,provenance)
    target = root/"runs"/ticker
    target.mkdir(parents=True,exist_ok=True)
    (target/"report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    (target/"report.md").write_text(render_report(report),encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticker")
    parser.add_argument("--root",type=Path,default=Path.cwd())
    parser.add_argument("--refresh",action="store_true")
    parser.add_argument("--offline",action="store_true")
    parser.add_argument("--memo",type=Path,help="Audit a memo against this ticker's printed report.")
    args = parser.parse_args()
    print(NOTICE)
    try:
        identity = None if args.offline else read_identity(args.root/".local"/"sec_identity.json")
        report = run_ticker(args.ticker,args.root,identity,args.refresh,args.offline)
        printed = render_report(report)
        print(printed)
        if args.memo:
            flagged = audit_memo(args.memo.read_text(encoding="utf-8-sig"),printed)
            print("Memo numeric audit:", json.dumps(flagged) if flagged else "pass")
            if flagged:
                raise SystemExit(2)
    except (ValueError,OSError,KeyError) as error:
        raise SystemExit(f"Unable to complete SEC analysis: {error}")


if __name__ == "__main__":
    main()

