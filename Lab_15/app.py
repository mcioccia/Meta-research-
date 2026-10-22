"""Lab 15 Streamlit page.

AI-use disclosure: Prepared with OpenAI Codex assistance; verify results.
Educational purposes only. Not financial or investment advice.
"""

import copy
import hashlib
import io

import streamlit as st

from portfolio import SLEEVES, CORRELATIONS, OBJECTIVE_RETURN, estimate_from_csv, search_portfolios


@st.cache_data(show_spinner=False)
def load_estimates(contents, recent):
    return estimate_from_csv(io.BytesIO(contents), last_36_months=recent)


@st.cache_data(show_spinner=False)
def find_mix(sleeves, correlations, objective, reserve):
    return search_portfolios(sleeves, correlations, objective, reserve)


def show_result(title, result, sleeves):
    st.subheader(title)
    if result is None:
        st.warning("no mix meets the objective")
        st.caption("No 5-point mix satisfies BOTH the return objective and reserve minimum.")
        return
    st.metric("Expected annual return", f"{result['return'] * 100:.2f}%")
    st.metric("Annual volatility", f"{result['volatility'] * 100:.2f}%")
    st.metric("Reserve-eligible weight", f"{result['reserve'] * 100:.2f}%")
    st.table([{"Asset": s["name"], "Weight (%)": f"{w * 100:.2f}"}
              for s, w in zip(sleeves, result["weights"])])
    st.caption(f"{result['feasible']:,} feasible mixes out of {result['tried']:,} tested.")


def main():
    st.set_page_config(page_title="Lab 15 | Portfolio explorer", page_icon="📊", layout="wide")
    st.title("Lab 15 · Portfolio explorer")
    st.caption("Built with AI help · A learning demonstration · Not financial or investment advice.")
    st.write("Find the lowest-volatility allocation on a 5-percentage-point grid, then see how it changes when your inputs change.")

    with st.sidebar:
        st.header("Mandate & data")
        objective = st.number_input("Expected annual return objective (%)", value=OBJECTIVE_RETURN * 100,
                                    step=0.1, format="%.2f", key="objective") / 100
        minimum = st.number_input("Minimum reserve-eligible weight (%)", min_value=0.0, max_value=100.0,
                                  value=3.0, step=1.0, format="%.2f", key="reserve") / 100
        uploaded = st.file_uploader("Upload monthly adjusted prices", type=["csv"], key="prices")
        recent = st.checkbox("Use last 36 months of returns", value=False,
                             disabled=uploaded is None, key="recent")
        st.caption("The 6.5% and 3% starting values belong to Meridian. For your CSV, enter your own mandate. "
                   "Choose 0% for no reserve constraint. Reserve eligibility must come from your mandate.")

    contents = uploaded.getvalue() if uploaded is not None else None
    source_key = hashlib.sha256(contents).hexdigest()[:16] if contents is not None else "meridian"
    try:
        if contents is None:
            loaded = copy.deepcopy(SLEEVES)
            current = copy.deepcopy(SLEEVES)
            loaded_correlations = copy.deepcopy(CORRELATIONS)
            current_correlations = copy.deepcopy(CORRELATIONS)
            st.info("Meridian training case · Course-authored annual inputs, not market estimates.")
        else:
            full = load_estimates(contents, False)
            selected = load_estimates(contents, recent)
            loaded = copy.deepcopy(full["sleeves"])
            current = copy.deepcopy(selected["sleeves"])
            loaded_correlations = full["correlations"]
            current_correlations = selected["correlations"]
            st.info(f"{uploaded.name} · Historical estimates, not forecasts. "
                    f"{full['price_count']} monthly prices: {full['price_start']} to {full['price_end']}.")
            st.caption(f"Current estimates use {selected['return_count']} monthly returns ending "
                       f"{selected['return_start']} through {selected['return_end']}. "
                       f"The loaded comparison uses all {full['return_count']} returns.")
            if len(current) < 3:
                st.warning("Lab 15 asks for 3–6 funds. This upload has fewer than three assets.")
            if full["price_count"] < 60:
                st.warning("This upload has fewer than 60 monthly prices; it does not cover the requested five years.")
            st.caption("The app cannot verify that each ticker is a fund or that prices are adjusted. Document sources and download dates in your notes.")
    except (ValueError, UnicodeError) as error:
        st.error(f"Cannot use this CSV: {error}")
        st.stop()

    st.subheader("Expected returns & reserve eligibility")
    st.caption("Returns are annual percentages. A change from 8.00 to 7.00 is a one-percentage-point decrease. "
               "Changing the estimation window resets the return boxes to that window's estimates.")
    input_key = source_key + ("_36" if contents is not None and recent else "_all")
    for i, sleeve in enumerate(current):
        left, middle, right = st.columns([3, 2, 2])
        with left:
            st.write(f"**{sleeve['name']}**")
            st.caption(f"Annual volatility: {sleeve['volatility'] * 100:.2f}%")
        with middle:
            sleeve["return"] = st.number_input(
                f"{sleeve['name']} expected return (%)", value=float(sleeve["return"] * 100),
                step=1.0, format="%.2f", key=f"return_{input_key}_{i}") / 100
        with right:
            eligible = st.checkbox(f"{sleeve['name']} reserve-eligible",
                                   value=bool(sleeve["reserve_eligible"]), key=f"eligible_{source_key}_{i}")
            sleeve["reserve_eligible"] = eligible
            loaded[i]["reserve_eligible"] = eligible

    st.caption(f"Comparison holds the mandate fixed: {objective * 100:.2f}% objective, "
               f"{minimum * 100:.2f}% reserve minimum, and the same selected reserve-eligible assets. "
               "Only returns and the estimation window differ between the two answers.")
    try:
        base = find_mix(loaded, loaded_correlations, objective, minimum)
        edited = find_mix(current, current_correlations, objective, minimum)
    except ValueError as error:
        st.error(f"Cannot calculate this mix: {error}")
        st.stop()

    left, right = st.columns(2)
    with left:
        show_result("Inputs as loaded · all months", base, loaded)
    with right:
        show_result("Your current inputs", edited, current)
    if base is not None and edited is not None:
        changes = [(new - old) * 100 for old, new in zip(base["weights"], edited["weights"])]
        largest = max(abs(change) for change in changes)
        names = [s["name"] for s, change in zip(current, changes) if abs(abs(change) - largest) < 1e-9]
        st.metric("Largest absolute weight change", f"{largest:.2f} percentage points")
        if largest > 0:
            st.caption("Largest change: " + ", ".join(names))
        st.table([{"Asset": s["name"], "Change from loaded (percentage points)": f"{change:+.2f}"}
                  for s, change in zip(current, changes)])
    else:
        st.info("Largest weight change: unavailable because one or both answers are infeasible.")

    with st.expander("See the inputs behind these answers"):
        st.table([{"Asset": s["name"], "Loaded return (%)": f"{b['return'] * 100:.4f}",
                   "Current return (%)": f"{s['return'] * 100:.4f}",
                   "Loaded volatility (%)": f"{b['volatility'] * 100:.4f}",
                   "Current volatility (%)": f"{s['volatility'] * 100:.4f}",
                   "Reserve eligible": s["reserve_eligible"]} for b, s in zip(loaded, current)])
        st.write("Current correlations (asset order above)")
        st.table(current_correlations)
        st.write("Loaded correlations (all months)")
        st.table(loaded_correlations)
    st.caption("Lowest risk means lowest volatility among tested 5-point mixes. A finer grid may give a different answer. "
               "This app checks long-only, full investment, expected return and reserve weight; it does not certify the full mandate or guarantee a maximum loss.")


if __name__ == "__main__":
    main()
