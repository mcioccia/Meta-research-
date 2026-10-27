"""Lab 16 ALFRED CPI snapshot comparison, standard library only.
AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
Educational purposes only. Not financial or investment advice.
"""
import argparse
import csv
from datetime import datetime
import hashlib
import io
import json
import math
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
from asof import signals, show_signal

SERIES = "CPIAUCSL"
DECISION_DATE = "2026-03-31"
LATER_DATE = "2026-04-15"
COMPARISON_DATE = "2026-10-27"
START = "2026-01-01"
END = "2026-09-01"
ROOT = Path(__file__).resolve().parent
AI_NOTICE = "AI-use disclosure: Prepared with OpenAI Codex assistance; verify results."
NOTICE = "Educational purposes only. Not financial or investment advice."


def download(vintage):
    parameters = dict(id=SERIES,cosd=START,coed=END,vintage_date=vintage)
    url = "https://alfred.stlouisfed.org/graph/alfredgraph.csv?" + urlencode(parameters)
    with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=30) as response:
        raw = response.read()
    text = raw.decode("utf-8-sig")
    records = list(csv.reader(io.StringIO(text)))
    expected_header = [ "observation_date", SERIES+"_"+vintage.replace("-","") ]
    if not records or records[0] != expected_header:
        raise ValueError(f"Unexpected vintage header for {vintage}: {records[:1]}")
    observations = []
    for row in records[1:]:
        if not row:
            continue
        if len(row) != 2:
            raise ValueError("Unexpected CSV layout")
        day,value = row
        if not START <= day <= END:
            raise ValueError(f"Date outside requested window: {day}")
        if value in ("","."):
            observations.append({"month_measured":day[:7],"index":None})
        else:
            number = float(value)
            if not math.isfinite(number) or number <= 0:
                raise ValueError("Invalid CPI index")
            observations.append({"month_measured":day[:7],"index":number})
    months = [r["month_measured"] for r in observations]
    if months != sorted(set(months)):
        raise ValueError("Duplicate or unordered months")
    return {"as_of_date":vintage,"url":url,
            "downloaded_at":datetime.now(ZoneInfo("America/New_York")).isoformat(),
            "provider_csv_sha256":hashlib.sha256(raw).hexdigest(),
            "provider_csv":text,"observations":observations}


def make_panel(snapshot, last_month="2026-03"):
    # Snapshot dates are NOT claimed to be first publication dates.
    return [{"row":i,"ticker":SERIES,"month":r["month_measured"],"index":r["index"]}
            for i,r in enumerate(snapshot["observations"],1)
            if r["index"] is not None and r["month_measured"] <= last_month]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download",action="store_true",help="Fetch the three fixed vintage dates; otherwise use saved source")
    args = parser.parse_args()
    source_path = ROOT/"Lab_16_ALFRED_source.json"
    if args.download:
        source = {"ai_disclosure":AI_NOTICE,"educational_notice":NOTICE,
                  "series":SERIES,"units":"Index 1982-1984=100",
                  "frequency":"Monthly","seasonal_adjustment":"Seasonally adjusted",
                  "series_source":"https://alfred.stlouisfed.org/series?seid=CPIAUCSL",
                  "snapshots":[download(v) for v in (DECISION_DATE,LATER_DATE,COMPARISON_DATE)]}
        source_path.write_text(json.dumps(source,indent=2),encoding="utf-8")
    else:
        source = json.loads(source_path.read_text(encoding="utf-8"))
    snapshots = source["snapshots"]
    if [s["as_of_date"] for s in snapshots] != [DECISION_DATE,LATER_DATE,COMPARISON_DATE]:
        raise ValueError("Saved snapshots do not match the configured dates; rerun --download.")
    result = {"ai_disclosure":AI_NOTICE,"educational_notice":NOTICE,"series":SERIES,
              "signal_scope":"January-March 2026 measured months, held fixed across vintages",
              "snapshot_is_not_first_publication_date":True,"signals":{}}
    lines = [AI_NOTICE,NOTICE,"ALFRED CPIAUCSL: real BLS data, monthly, seasonally adjusted.",
             "Fixed measured-month scope for signals: January-March 2026.",
             "Vintage date means known as of that day, not first publication day.",""]
    for snapshot in snapshots:
        panel = make_panel(snapshot)
        signal = signals(panel).get(SERIES)
        result["signals"][snapshot["as_of_date"]] = signal
        # Independent direct check against the two last available observations.
        if signal and signal[1] is not None:
            prior,current = panel[-2:]
            independent = (current["index"]-prior["index"])/prior["index"]*100
            if not math.isclose(signal[1],independent,abs_tol=1e-12):
                raise AssertionError("Independent signal calculation differs")
        lines.append(f'{snapshot["as_of_date"]}: {show_signal(signal)}')
    maps = [{r["month_measured"]:r["index"] for r in s["observations"]} for s in snapshots]
    lines += ["","Index observations (missing means unavailable, not zero):",
              "Month       March 31       April 15       October 27"]
    for month in sorted(set().union(*(set(m) for m in maps))):
        values = [m.get(month) for m in maps]
        lines.append(f'{month:<10}' + ''.join(f'{v:>15.3f}' if v is not None else f'{"unavailable":>15}' for v in values))
    comparable = [m for m in maps[0] if maps[0][m] is not None and maps[2].get(m) is not None]
    revisions = {m:maps[2][m]-maps[0][m] for m in comparable}
    result["same_month_revisions_october_minus_march"] = revisions
    result["published_after_decision_in_saved_window"] = [m for m in maps[2]
        if maps[2][m] is not None and maps[0].get(m) is None]
    result["validation"] = "PASS: vintage-specific headers; date order; numeric validity; independent signal calculations."
    lines += ["",result["validation"],
              "First publication dates/full revision histories are not supplied by these snapshots.",
              "Do not label the selected vintage dates as actual publication dates.",
              "Original fictional asof.py and six-fund portfolio inputs are unchanged."]
    output = "\n".join(lines)+"\n"
    print(output)
    (ROOT/"Lab_16_ALFRED_output.txt").write_text(output,encoding="utf-8")
    (ROOT/"Lab_16_ALFRED_results.json").write_text(json.dumps(result,indent=2),encoding="utf-8")


if __name__ == "__main__":
    main()

