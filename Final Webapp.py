import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import re
import os
import altair as alt
from scipy.stats import pearsonr


st.set_page_config(layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 2.5rem; padding-bottom: 1rem;}
h3 {margin-top: 0.2rem; margin-bottom: 0.2rem; font-size: 16px;}
.stTable table {font-size: 11px;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# SHARED HELPERS
# ---------------------------------------------------------------

def resistant_pct(df, group_col, inf_col, res_col, exclude_unknown=True):
    d = df.copy()
    if exclude_unknown:
        d = d[~d[group_col].astype(str).str.contains("Unknown", case=False, na=False)]
    agg = d.groupby(group_col)[[inf_col, res_col]].sum()
    agg["Percent Resistant"] = agg[res_col] / agg[inf_col] * 100
    return agg["Percent Resistant"]

def gradient_bar_chart(series, order=None, scheme="blues", title=""):
    data = series.reset_index()
    data.columns = [data.columns[0], "Percent Resistant"]
    category_col = data.columns[0]

    x_enc = alt.X(f"{category_col}:N", title=None, sort=order if order else "-y",
                   axis=alt.Axis(labelAngle=-40, labelFontSize=9))

    chart = alt.Chart(data).mark_bar().encode(
        x=x_enc,
        y=alt.Y("Percent Resistant:Q", title="% Resistant"),
        color=alt.Color("Percent Resistant:Q", scale=alt.Scale(scheme=scheme), legend=None),
        tooltip=[category_col, alt.Tooltip("Percent Resistant:Q", format=".1f")]
    ).properties(title=title, height=180)

    return chart

# ---------------------------------------------------------------
# TOP-LEVEL 3-COLUMN LAYOUT
# ---------------------------------------------------------------

st.title("Antibiotic Resistance Analysis")
section1, section2, section3 = st.columns([2, 1.3, 2])

# =================================================================
# SECTION 1 — AMR MAP BY REGION
# =================================================================
with section1:
    st.subheader("AMR Burden by Region")

    @st.cache_data
    def load_geojson():
        url = "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/Regions_December_2025_Boundaries_EN_BGC/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"
        return requests.get(url).json()

    geojson = load_geojson()

    map_df = pd.read_csv("AMR Incidence per 100000/AMR_incidence_per_100000_with_totals.csv")
    map_df = map_df[map_df["Region"] != "Total by Year"].copy()

    region_name_fixes = {"Yorkshire and Humber": "Yorkshire and The Humber"}
    map_df["Region"] = map_df["Region"].replace(region_name_fixes)

    fig = px.choropleth(
        map_df,
        geojson=geojson,
        locations="Region",
        featureidkey="properties.RGN25NM",
        color="Avg by Region",
        color_continuous_scale="reds",
        hover_name="Region"
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0))

    st.plotly_chart(fig, use_container_width=True)

    table_df = map_df.drop(columns=["Unnamed: 0"], errors="ignore")
    table_df.columns = pd.MultiIndex.from_tuples([
    ("Region", ""),
    ("AMR Burden per 100000 population", "2020"),
    ("AMR Burden per 100000 population", "2021"),
    ("AMR Burden per 100000 population", "2022"),
    ("AMR Burden per 100000 population", "2023"),
    ("AMR Burden per 100000 population", "2024"),
    ("Avg by Region", "")])
    st.dataframe(table_df, hide_index=True, height=180, use_container_width=True)

# =================================================================
# SECTION 2 — LAG CORRELATION
# =================================================================
with section2:
    st.subheader("Consumption → AMR Lag")

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
            label = "Same year" if lag == 0 else f"{lag}-yr lag"
            results.append({"Lag": label, "Correlation (r)": r, "p-value": p, "n": n})
        return pd.DataFrame(results)

    combined = load_combined()
    results_df = compute_all_lags(combined)

    corr_chart = alt.Chart(results_df).mark_bar().encode(
        x=alt.X("Lag:N", title=None, sort=None),
        y=alt.Y("Correlation (r):Q"),
        color=alt.Color("Correlation (r):Q", scale=alt.Scale(scheme="redblue", domainMid=0), legend=None),
        tooltip=["Lag", alt.Tooltip("Correlation (r):Q", format=".3f"), alt.Tooltip("p-value:Q", format=".3f"), "n"]
    ).properties(height=200)

    st.altair_chart(corr_chart, use_container_width=True)

    with st.expander("Details (r, p, n)"):
        alpha = 0.05
        for _, row in results_df.iterrows():
            if pd.notna(row["p-value"]):
                sig = "significant" if row["p-value"] < alpha else "not significant"
                st.write(f"**{row['Lag']}**: r={row['Correlation (r)']:.3f}, p={row['p-value']:.3f}, n={int(row['n'])} → {sig}")
            else:
                st.write(f"**{row['Lag']}**: insufficient data (n={int(row['n'])})")

# =================================================================
# SECTION 3 — DEMOGRAPHIC 2x2 GRID
# =================================================================
with section3:
    st.subheader("Resistance by Demographic Factor")

    @st.cache_data
    def load_imd_sex_data():
        df = pd.read_csv("2024-2025 Analysis/CLEAN AMR Sex, Age, IMD - ESPAUR-2024-2025.csv")
        df.columns = df.columns.str.strip()
        return df

    @st.cache_data
    def load_ethnicity_data():
        df = pd.read_csv("2024-2025 Analysis/CLEAN AMR Sex, Age, Ethnicity - ESPAUR-2024-2025.csv")
        df.columns = df.columns.str.strip()
        return df

    imd_sex_df = load_imd_sex_data()
    eth_df = load_ethnicity_data()

    infections_col = [c for c in imd_sex_df.columns if "Estimated number of bacteraemia" in c and "resistant" not in c.lower()][0]
    resistant_col = [c for c in imd_sex_df.columns if "resistant bacteraemia" in c.lower()][0]
    imd_col = [c for c in imd_sex_df.columns if "IMD" in c][0]

    eth_infections_col = "Estimated number of bacteraemia infections"
    eth_resistant_col = "Estimated number of resistant bacteraemia infections"
    eth_col = [c for c in eth_df.columns if "Ethnic" in c][0]

    sex_data = resistant_pct(imd_sex_df, "Sex", infections_col, resistant_col).reset_index()
    sex_data.columns = ["Sex", "Percent Resistant"]
    sex_chart = alt.Chart(sex_data).mark_bar().encode(
        x=alt.X("Sex:N", title=None),
        y=alt.Y("Percent Resistant:Q", title="% Resistant"),
        color=alt.Color("Sex:N", scale=alt.Scale(domain=["Female", "Male"], range=["#e05d8c", "#4a7fbf"]), legend=None)
    ).properties(height=180)

    imd_order = ["1 (most deprived)", "2", "3", "4", "5 (least deprived)"]
    imd_data = resistant_pct(imd_sex_df, imd_col, infections_col, resistant_col).reindex(imd_order)

    age_order = ["less than 1", "1 to 4", "5 to 9", "10 to 14", "15 to 44", "45 to 64", "65 to 74", "75 and over"]
    age_data = resistant_pct(imd_sex_df, "Age group (years)", infections_col, resistant_col).reindex(age_order)

    eth_data = resistant_pct(eth_df, eth_col, eth_infections_col, eth_resistant_col)

    g1, g2 = st.columns(2)
    g3, g4 = st.columns(2)

    with g1:
        st.caption("By Sex")
        st.altair_chart(sex_chart, use_container_width=True)
    with g2:
        st.caption("By IMD Quintile")
        st.altair_chart(gradient_bar_chart(imd_data, order=imd_order, scheme="oranges"), use_container_width=True)
    with g3:
        st.caption("By Age Group")
        st.altair_chart(gradient_bar_chart(age_data, order=age_order, scheme="greens"), use_container_width=True)
    with g4:
        st.caption("By Ethnicity")
        st.altair_chart(gradient_bar_chart(eth_data, scheme="purples"), use_container_width=True)
