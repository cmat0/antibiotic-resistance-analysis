import pandas as pd
import re
import os
import streamlit as st
from scipy.stats import pearsonr

@st.cache_data
def load_combined():
    folder = "AMR & Consumption"
    files = sorted(f for f in os.listdir(folder) if f.endswith(".csv"))

    dfs = []
    for file in files:
        matches = re.search(r"CLEAN AMR (\d+)\.csv", file)
        if matches is None:
            continue
        start_year = matches.group(1)
        year = f"{start_year} - {int(start_year) + 1}"

        df = pd.read_csv(os.path.join(folder, file))
        df["Year"] = year
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)

@st.cache_data
def compute_all_lags(combined):
    def lagged_correlation(lag):
        cons = combined[["Local area region", "Year", "Total incidence rate per 100000 population"]].rename(
            columns={"Total incidence rate per 100000 population": "Consumption"}
        )
        amr = combined[["Local area region", "Year", "Rate per 100000 population resistant bloodstream infections"]].rename(
            columns={"Rate per 100000 population resistant bloodstream infections": "AMR"}
        )
        years_sorted = sorted(combined["Year"].unique())
        if lag == 0:
            merged = cons.merge(amr, on=["Local area region", "Year"]).dropna(subset=["Consumption", "AMR"])
        else:
            year_map = dict(zip(years_sorted, years_sorted[lag:]))
            cons["Target Year"] = cons["Year"].map(year_map)
            merged = cons.merge(
                amr.rename(columns={"Year": "Target Year", "AMR": "AMR"}),
                on=["Local area region", "Target Year"]
            ).dropna(subset=["Consumption", "AMR"])
        if len(merged) < 3:
            return None, None, len(merged)
        r, p = pearsonr(merged["Consumption"], merged["AMR"])
        return r, p, len(merged)

    results = []
    for lag in [0, 1, 2]:
        r, p, n = lagged_correlation(lag)
        label = "Same year" if lag == 0 else f"{lag}-year lag"
        results.append({"Lag": label, "Correlation (r)": r, "p-value": p, "n": n})
    return pd.DataFrame(results)

combined = load_combined()
results_df = compute_all_lags(combined)

st.title("Does Consumption Influence AMR Burden?")
st.bar_chart(results_df.set_index("Lag")["Correlation (r)"])
st.dataframe(results_df)

alpha = 0.05
for _, row in results_df.iterrows():
    if pd.notna(row["p-value"]):
        sig = "significant" if row["p-value"] < alpha else "not significant"
        st.write(f"**{row['Lag']}**: r = {row['Correlation (r)']:.3f}, p = {row['p-value']:.3f}, n = {int(row['n'])} → {sig} at α=0.05")
    else:
        st.write(f"**{row['Lag']}**: insufficient data (n={int(row['n'])})")