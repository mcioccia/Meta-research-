"""Lab 17 point-in-time rates app.
AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
Educational purposes only. Not financial or investment advice.
"""
import csv
from datetime import date, datetime
import io
import math
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st

DEFAULT_SERIES = ["BAA", "FEDFUNDS", "DGS10", "MORTGAGE30US"]
SERIES_INFO = {
    "BAA": ("Moody's Baa corporate bond yield", "Percent", "Monthly"),
    "FEDFUNDS": ("Effective federal funds rate", "Percent", "Monthly"),
    "DGS10": ("10-year Treasury yield", "Percent", "Daily"),
    "MORTGAGE30US": ("30-year fixed mortgage rate", "Percent", "Weekly"),
    "PAYEMS": ("Total nonfarm payroll jobs", "Thousands of persons, seasonally adjusted", "Monthly"),
    "CPIAUCSL": ("Consumer Price Index, all urban consumers", "Index 1982-1984=100, seasonally adjusted", "Monthly"),
}
AI_NOTICE = "Built with AI help. Educational purposes only. Not financial or investment advice."


def validate_id(series):
    series = series.strip().upper()
    if not re.fullmatch(r"[A-Z0-9_]{1,80}", series):
        raise ValueError("Use a FRED series ID containing letters, digits or underscores.")
    return series


def parse_csv(text, series, vintage=None):
    rows = list(csv.reader(io.StringIO(text.lstrip("\ufeff"))))
    expected = series if vintage is None else series+"_"+vintage.replace("-","")
    if not rows or len(rows[0]) != 2 or rows[0][0].lower() not in ("date","observation_date"):
        raise ValueError(f"Unexpected CSV header for {series}; requested vintage could not be verified.")
    header = rows[0][1]
    if vintage is None:
        if header != expected:
            raise ValueError("Unexpected current-series header.")
    else:
        match = re.fullmatch(re.escape(series)+r"_(\d{8})", header)
        if not match:
            raise ValueError("Historical response lacks a vintage identifier.")
        effective = datetime.strptime(match.group(1), "%Y%m%d").date()
        if effective > date.fromisoformat(vintage):
            raise ValueError("Provider returned a vintage after the requested decision date.")
    data = []
    seen = set()
    for row in rows[1:]:
        if not row:
            continue
        if len(row) != 2:
            raise ValueError("Invalid CSV row.")
        measured = date.fromisoformat(row[0])
        if measured in seen:
            raise ValueError("Duplicate measured date in provider response.")
        seen.add(measured)
        value = None if row[1].strip() in (".","") else float(row[1])
        if value is not None and not math.isfinite(value):
            raise ValueError("Nonfinite data value.")
        data.append({"date":measured.isoformat(),"value":value})
    if [r["date"] for r in data] != sorted(r["date"] for r in data):
        raise ValueError("Provider dates are not chronological.")
    return data


def fetch_csv(url, series, vintage=None):
    try:
        with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=30) as response:
            raw = response.read().decode("utf-8-sig")
        data = parse_csv(raw,series,vintage)
        effective = None if vintage is None else datetime.strptime(
            next(csv.reader(io.StringIO(raw)))[1][-8:], "%Y%m%d").date().isoformat()
        return {"series":series,"vintage":vintage,"effective_vintage":effective,"url":url,"data":data,
                "downloaded_at":datetime.now(ZoneInfo("America/New_York")).isoformat(),
                "raw_csv":raw,"error":None}
    except (HTTPError,URLError,TimeoutError,OSError,ValueError) as error:
        return {"series":series,"url":url,"error":f"{type(error).__name__}: {error}"}


@st.cache_data(show_spinner=False)
def download_current(series, download_day):
    """One FRED request per series/day; controls reuse the cached full history."""
    series = validate_id(series)
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?" + urlencode({"id":series})
    return fetch_csv(url,series)


@st.cache_data(show_spinner=False)
def download_asof(series, vintage_date, download_day):
    """One ALFRED request per series/vintage/day; keep the vintage in the URL."""
    series = validate_id(series)
    vintage = date.fromisoformat(vintage_date).isoformat()
    url = "https://alfred.stlouisfed.org/graph/alfredgraph.csv?" + urlencode(
        {"id":series,"vintage_date":vintage})
    return fetch_csv(url,series,vintage)


def compare_series(current, historical, start):
    """Latest actual observations; counts within the chosen measured-date window."""
    if current.get("error") or historical.get("error"):
        raise ValueError(current.get("error") or historical.get("error"))
    now = {r["date"]:r["value"] for r in current["data"] if r["value"] is not None}
    then = {r["date"]:r["value"] for r in historical["data"] if r["value"] is not None}
    last_now = max(now,default=None)
    last_then = max(then,default=None)
    common = sorted(d for d in now.keys() & then.keys() if d >= start)
    revisions = [d for d in common if not math.isclose(now[d],then[d],rel_tol=0,abs_tol=1e-9)]
    after = None if last_then is None else sum(d >= start and d > last_then for d in now)
    return {"last_known_date":last_then,"known_value":then.get(last_then),
            "last_current_date":last_now,"current_value":now.get(last_now),
            "values_after_last_known":after,"revised_count":len(revisions),
            "compared_count":len(common),"revised_dates":revisions}



FINANCE_CONTEXT = {
    "BAA": "Corporate borrowing costs · read alongside Treasury yields to assess credit conditions.",
    "FEDFUNDS": "Monetary policy · a reference for short-term funding costs and the cash-yield environment.",
    "DGS10": "Treasury benchmark · relevant to discount rates and bond duration exposure.",
    "MORTGAGE30US": "Housing finance · tracks the cost of new 30-year fixed-rate mortgage borrowing.",
    "CPIAUCSL": "Inflation backdrop · this is a price index level, not the inflation rate.",
    "PAYEMS": "Labor-market backdrop · payroll employment level, not monthly job creation.",
}


def latest_move(record):
    """Change between the two latest nonmissing observations, in native units."""
    valid = [r for r in record["data"] if r["value"] is not None]
    if not valid:
        return None, None, None
    last = valid[-1]
    prior = valid[-2] if len(valid) > 1 else None
    return last, prior, None if prior is None else last["value"] - prior["value"]


def overlay_data(records, start, indexed=False):
    """Monthly means of available observations; never fill missing months.
    Rebased mode uses the first month shared by every included series.
    """
    monthly = {}
    for series, record in records.items():
        if record.get("error"):
            continue
        buckets = {}
        for row in record["data"]:
            if row["date"] >= start and row["value"] is not None:
                buckets.setdefault(row["date"][:7], []).append(row["value"])
        if buckets:
            monthly[series] = {m:sum(v)/len(v) for m,v in buckets.items()}
    if not monthly:
        return [], None
    base = None
    if indexed:
        common = set.intersection(*(set(v) for v in monthly.values()))
        eligible = [m for m in common if all(v[m] > 0 for v in monthly.values())]
        if not eligible:
            raise ValueError("No shared month with positive values to rebase every series.")
        base = min(eligible)
    first = base or min(min(v) for v in monthly.values())
    last = max(max(v) for v in monthly.values())
    months = pd.date_range(first+"-01", last+"-01", freq="MS")
    result = []
    for series, values in monthly.items():
        for measured in months:
            value = values.get(measured.strftime("%Y-%m"))
            if indexed and value is not None:
                value = value / values[base] * 100
            result.append({"Month":measured, "Series":series, "Value":value})
    return result, base


def format_level(value, units):
    if value is None:
        return "Unavailable"
    return f"{value:,.2f}%" if units == "Percent" else f"{value:,.3f}"


def main():
    st.set_page_config(page_title="Lab 17 | Rates & macro monitor",layout="wide")
    today = datetime.now(ZoneInfo("America/New_York")).date()
    day = today.isoformat()
    st.title("Rates & macro monitor")
    st.caption(f"Lab 17 · Data from FRED and ALFRED, Federal Reserve Bank of St. Louis, downloaded today ({day}); built with AI help, a learning demonstration, not investment advice.")
    st.write("Track financing costs, compare rate trends, and audit what was available at a historical decision date.")
    st.sidebar.header("Research controls")
    selected = st.sidebar.multiselect("Series",DEFAULT_SERIES,default=DEFAULT_SERIES,
        format_func=lambda s:f"{s} — {SERIES_INFO[s][0]}",key="series")
    custom = st.sidebar.text_input("Add another FRED series ID",placeholder="CPIAUCSL or PAYEMS",key="custom")
    start = st.sidebar.date_input("Chart start date",value=date(2020,1,1),min_value=date(1900,1,1),max_value=today,key="start")
    asof = st.sidebar.date_input("As known on",value=today,min_value=date(1900,1,1),max_value=today,key="asof")
    st.sidebar.caption("Decision-date snapshots are end-of-date evidence, not confirmation that a release preceded an intraday trade.")
    if custom.strip():
        try:
            extra = validate_id(custom)
            if extra not in selected:
                selected = [*selected,extra]
        except ValueError as error:
            st.error(f"Custom series: {error}")
    if not selected:
        st.info("Select a series or enter a FRED ID.")
        return
    evidence = {}
    with st.spinner("Loading market and vintage data"):
        for series in selected:
            evidence[series] = {"current":download_current(series,day),
                "historical":download_asof(series,asof.isoformat(),day)}

    st.subheader("Latest market readings")
    st.caption("Changes are versus each series' previous nonmissing observation: daily, weekly or monthly as labelled. 1 basis point (bp) = 0.01 percentage point. These are rate or macro changes, not investment returns.")
    for offset in range(0,len(selected),2):
        cards = st.columns(2)
        for column,series in zip(cards,selected[offset:offset+2]):
            title,units,frequency = SERIES_INFO.get(series,(series,"Provider units — check FRED","Provider frequency"))
            with column:
                current = evidence[series]["current"]
                if current.get("error"):
                    st.error(f"{series}: current download failed. {current['error']}")
                    continue
                last,prior,move = latest_move(current)
                delta = None if move is None else (f"{move*100:+.1f} bp" if units == "Percent" else f"{move:+,.3f} native units")
                st.metric(series,format_level(last["value"] if last else None,units),delta=delta,delta_color="off")
                st.caption(f"{title} · {frequency} · measured {last['date'] if last else 'unavailable'}")
                if prior:
                    st.caption(f"Change versus {prior['date']} · {units}")

    st.divider()
    st.subheader("Series research")
    st.caption("Individual charts show today's history at its original frequency. Expand the evidence below each chart to inspect revisions and source timestamps.")
    summaries = []
    for series in selected:
        title,units,frequency = SERIES_INFO.get(series,(series,"Provider units — check the linked FRED page","Provider frequency"))
        current = evidence[series]["current"]
        historical = evidence[series]["historical"]
        st.subheader(f"{series} · {title}")
        st.write(FINANCE_CONTEXT.get(series,"Custom research series · verify its definition and units before interpreting it."))
        st.caption(f"{units} · {frequency} · https://fred.stlouisfed.org/series/{series}")
        if not current.get("error"):
            plotted = [r for r in current["data"] if r["date"] >= start.isoformat()]
            if plotted:
                frame = pd.DataFrame(plotted)
                frame["date"] = pd.to_datetime(frame["date"])
                st.line_chart(frame,x="date",y="value",x_label="Date measured",y_label=units,height=260)
            else:
                st.info("No observations in the selected chart window.")
        if historical.get("error"):
            st.error(f"{series}: as-of download failed. {historical['error']}")
        if current.get("error") or historical.get("error"):
            summaries.append({"Series":f"https://fred.stlouisfed.org/series/{series}","Status":"Download error"})
            continue
        if historical["effective_vintage"] != asof.isoformat():
            st.warning(f'{series}: requested {asof}, but ALFRED labelled its response {historical["effective_vintage"]}. Completeness through the requested day is unconfirmed.')
        audit = compare_series(current,historical,start.isoformat())
        now = {r["date"]:r["value"] for r in current["data"]}
        then = {r["date"]:r["value"] for r in historical["data"]}
        same_date_now = now.get(audit["last_known_date"])
        revision = None if same_date_now is None or audit["known_value"] is None else same_date_now - audit["known_value"]
        st.write(f"**Available in the returned snapshot:** {format_level(audit['known_value'],units)} · measured {audit['last_known_date'] or 'unavailable'} · vintage {historical['effective_vintage']}")
        if revision is not None:
            revision_text = f"{revision*100:+.1f} bp" if units == "Percent" else f"{revision:+,.3f} native units"
            st.caption(f"Revision to that same observation in today's history: {revision_text}. New observations are counted separately below.")
        summaries.append({"Series":f"https://fred.stlouisfed.org/series/{series}",
            "Known: last measured":audit["last_known_date"],"Known: value":audit["known_value"],
            "Today: last measured":audit["last_current_date"],"Today: value":audit["current_value"],
            "Later observations":audit["values_after_last_known"],"Revised same dates":audit["revised_count"],
            "Dates compared":audit["compared_count"],"Units":units,"Returned vintage":historical["effective_vintage"],
            "Status":"OK" if historical["effective_vintage"] == asof.isoformat() else "Earlier vintage returned"})
        with st.expander(f"{series}: source evidence and revisions"):
            st.write({"Current downloaded":current["downloaded_at"],"Vintage downloaded":historical["downloaded_at"],
                "Current URL":current["url"],"Vintage URL":historical["url"]})
            detail = [{"Date measured":d,"As known then":then.get(d),"Current value":now.get(d),
                       "Revised":d in audit["revised_dates"]}
                      for d in sorted(now.keys() | then.keys()) if d >= start.isoformat()]
            st.dataframe(pd.DataFrame(detail),hide_index=True)
    st.subheader("Decision-date audit")
    st.caption(f"Decision date: {asof} · Counts from {start}. Latest readings use each full downloaded series. A later observation is new information; a revision changes a value for the same measured date.")
    st.dataframe(pd.DataFrame(summaries),hide_index=True,width="stretch",
        column_config={"Series":st.column_config.LinkColumn("Series",display_text=r"https://fred\.stlouisfed\.org/series/(.*)")})
    st.caption("Missing values are excluded, never replaced by zero. Revisions compare dates with values in both snapshots (absolute tolerance: 0.000000001 native units). Observation dates are not publication dates.")

    st.divider()
    st.subheader("All series · comparison chart")
    st.write("See the selected series on one timeline.")
    source = st.radio("Chart information set",["Today's history","As known on the selected date"],horizontal=True,key="overlay_source")
    source_key = "current" if source == "Today's history" else "historical"
    records = {s:evidence[s][source_key] for s in selected if not evidence[s][source_key].get("error")}
    failed = [s for s in selected if evidence[s][source_key].get("error")]
    if failed:
        st.warning("No overlay data for: "+", ".join(failed))
    mixed = any(SERIES_INFO.get(s,("",None,""))[1] != "Percent" for s in records)
    if mixed:
        indexed = True
        st.info("Mixed units: all series are rebased to 100 in their first shared month. This compares relative movement; it is not a total-return or inflation-rate chart.")
    else:
        indexed = st.radio("Comparison scale",["Rate levels (%)","Indexed levels (start = 100)"],horizontal=True,key="overlay_scale").startswith("Indexed")
    if source_key == "historical":
        earlier = [f"{s}: {r['effective_vintage']}" for s,r in records.items() if r["effective_vintage"] != asof.isoformat()]
        if earlier:
            st.warning("Earlier snapshots in this chart — "+", ".join(earlier))
    try:
        rows,base = overlay_data(records,start.isoformat(),indexed)
        if rows:
            st.line_chart(pd.DataFrame(rows),x="Month",y="Value",color="Series",
                x_label="Measured month",y_label="Index (base = 100)" if indexed else "Yield / rate (%)",height=420)
            st.caption("Monthly averages of available observations put daily, weekly and monthly series on a common display frequency. No forward fill or missing-value substitution. Partial first/latest months may be incomplete; monthly labels do not imply publication on the first day.")
            if base:
                st.caption(f"Shared base month: {base}. Each index = monthly average / its base-month average × 100. No data before the shared base is plotted.")
            else:
                st.caption("Line gaps are rate differentials, not automatically credit spreads: the instruments differ in maturity, credit quality and construction.")
        else:
            st.info("No observations available for this comparison window.")
    except ValueError as error:
        st.warning(str(error))
    st.caption(AI_NOTICE)


if __name__ == "__main__":
    main()

