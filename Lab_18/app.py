"""Lab 18 business-quality dashboard.
AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
Educational purposes only. Not financial or investment advice.
"""
import hashlib
import json
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "buffett-sec-review" / "scripts"))
from sec_facts import (NOTICE, audit_memo, display_rows, read_identity,
                       render_report, run_ticker, valid_ticker)

st.set_page_config(page_title="Business Quality | SEC", layout="wide")
st.title("Business quality • SEC research desk")
st.caption("Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.")
st.write("A Buffett-inspired review of profitability and cash generation. The verdict concerns the business; it does not establish an attractive purchase price.")

with st.sidebar:
    st.header("Research universe")
    raw_ticker = st.text_input("Company ticker", "COST")
    refresh = st.button("Download / refresh SEC filings", type="primary")
    st.caption("Uses annual 10-K facts. Downloading requires your name and email in local SEC settings.")
    st.write("**Owner earnings:** operating cash flow less capital spending.")
    st.caption("A simplified course measure. No price data, forecasts or valuation are used.")

try:
    ticker = valid_ticker(raw_ticker)
    if refresh:
        with st.spinner("Downloading SEC facts and recalculating the five annual periods…"):
            report = run_ticker(ticker, ROOT, read_identity(ROOT/".local"/"sec_identity.json"), refresh=True)
    else:
        report = run_ticker(ticker, ROOT, offline=True)
except (ValueError, OSError, KeyError, json.JSONDecodeError) as error:
    st.info("SEC data is not ready for this ticker.")
    st.error(str(error))
    st.caption("Once the local SEC identity is set, select Download / refresh SEC filings. Missing data is never replaced with course answer values.")
    st.stop()

rows = report["rows"]
printed = render_report(report)
st.subheader(report["company"] + " (" + ticker + ")")
st.caption("USD millions • ROE uses year-end equity • annual observations, latest filing wins")
if rows:
    st.write("**Fiscal coverage:** " + rows[0]["fy_end"] + " through " + rows[-1]["fy_end"])
st.caption("Source downloaded (UTC): " + report["source"].get("downloaded_at", "not recorded"))
if len(rows) != 5:
    st.warning("Fewer than five eligible fiscal periods were found. Five-year checks remain unresolved.")

st.subheader("Cash generation and accounting earnings")
chart_rows = [{"Fiscal year end": pd.Timestamp(r["fy_end"]),
               "Owner earnings": None if r["owner_earnings"] is None else r["owner_earnings"]/1_000_000,
               "Net income": None if r["fields"]["net_income"]["value"] is None else r["fields"]["net_income"]["value"]/1_000_000}
              for r in rows]
if chart_rows:
    frame = pd.DataFrame(chart_rows).set_index("Fiscal year end")
    st.line_chart(frame, y_label="USD millions", x_label="Fiscal year end", color=["#14866D", "#3778BF"])
    if frame.isna().any().any():
        st.caption("Missing values are left blank. They are not zero.")
else:
    st.info("No eligible annual observations are available.")

st.subheader("Business-quality checks")
for col, (label, result) in zip(st.columns(3), report["checks"].items()):
    col.metric(label, result.upper())

st.subheader("Annual financial record")
st.dataframe(pd.DataFrame(display_rows(report)), hide_index=True, width="stretch")
with st.expander("Audit trail • XBRL tags and original filings"):
    st.markdown(printed)
st.download_button("Download calculated report", printed, file_name=ticker+"_SEC_report.md", mime="text/markdown")

st.subheader("Buffett-inspired analyst memo")
st.caption("AI judgment, not Warren Buffett's actual opinion. The script supplies every number.")
memo_path = ROOT/"runs"/ticker/"memo.md"
meta_path = memo_path.with_name("memo_meta.json")
if not memo_path.exists():
    st.warning("A reviewed memo has not yet been saved for this company's calculated report.")
    st.write("Ask the AI to run the buffett-sec-review skill on this ticker, read the printed report, and save its business-quality judgment.")
else:
    saved = memo_path.read_text(encoding="utf-8-sig")
    bound = False
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
            bound = (meta.get("ticker") == ticker and meta.get("report_id") == report["report_id"]
                     and meta.get("memo_sha256") == hashlib.sha256(memo_path.read_bytes()).hexdigest())
        except (ValueError, OSError):
            pass
    if not bound:
        st.warning("This memo is unverified or stale: its company, source report or saved text does not match its review record.")
    text = st.text_area("Memo text • edit here to test an unsupported number", saved, height=280,
                        key="memo_"+ticker+"_"+report["report_id"])
    if text != saved:
        st.caption("Unsaved probe: this edit does not overwrite the reviewed memo.")
    flagged = audit_memo(text, printed)
    if flagged:
        st.error("Unsupported numbers found. Do not rely on these claims.")
        st.dataframe(pd.DataFrame([{"Number":f["number"], "Memo line":f["line"]} for f in flagged]),
                     hide_index=True, width="stretch")
    else:
        st.success("All numeric literals appear in the script's printed report.")
    st.caption("This checks numeric membership only. A printed number assigned to the wrong year, metric or unit still requires human review.")
    st.markdown(text)
st.divider()
st.caption(NOTICE)

