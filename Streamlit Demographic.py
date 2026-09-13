import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(layout="wide")

@st.cache_data
def load_imd_sex_data():
    df = pd.read_csv("2024-2025 Analysis/CLEAN AMR Sex, Age, IMD - ESPAUR-2024-2025.csv")  # adjust path
    df.columns = df.columns.str.strip()
    return df

@st.cache_data
def load_ethnicity_data():
    df = pd.read_csv("2024-2025 Analysis/CLEAN AMR Sex, Age, Ethnicity - ESPAUR-2024-2025.csv")  # adjust path
    df.columns = df.columns.str.strip()
    return df

def gradient_bar_chart(series, order=None, scheme="blues", title=""):
    data = series.reset_index()
    data.columns = [data.columns[0], "Percent Resistant"]
    category_col = data.columns[0]

    x_enc = alt.X(f"{category_col}:N", title=None, sort=order if order else "-y")

    chart = alt.Chart(data).mark_bar().encode(
        x=x_enc,
        y=alt.Y("Percent Resistant:Q", title="% Resistant"),
        color=alt.Color("Percent Resistant:Q", scale=alt.Scale(scheme=scheme), legend=None),
        tooltip=[category_col, alt.Tooltip("Percent Resistant:Q", format=".1f")]
    ).properties(title=title)

    return chart

imd_sex_df = load_imd_sex_data()
eth_df = load_ethnicity_data()

infections_col = [c for c in imd_sex_df.columns if "Estimated number of bacteraemia" in c and "resistant" not in c.lower()][0]
resistant_col = [c for c in imd_sex_df.columns if "resistant bacteraemia" in c.lower()][0]

eth_infections_col = "Estimated number of bacteraemia infections"
eth_resistant_col = "Estimated number of resistant bacteraemia infections"

def resistant_pct(df, group_col, inf_col, res_col, exclude_unknown=True):
    d = df.copy()
    if exclude_unknown:
        d = d[~d[group_col].astype(str).str.contains("Unknown", case=False, na=False)]
    agg = d.groupby(group_col)[[inf_col, res_col]].sum()
    agg["Percent Resistant"] = agg[res_col] / agg[inf_col] * 100
    return agg["Percent Resistant"]

st.title("AMR Resistance Rate by Demographic Factor")

sex_data = resistant_pct(imd_sex_df, "Sex", infections_col, resistant_col).reset_index()
sex_data.columns = ["Sex", "Percent Resistant"]
sex_chart = alt.Chart(sex_data).mark_bar().encode(
    x=alt.X("Sex:N", title=None),
    y=alt.Y("Percent Resistant:Q", title="% Resistant"),
    color=alt.Color("Sex:N", scale=alt.Scale(domain=["Female", "Male"], range=["#e05d8c", "#4a7fbf"]), legend=None)
)

# IMD Quantile
imd_col = [c for c in imd_sex_df.columns if "IMD" in c][0]
imd_order = ["1 (most deprived)", "2", "3", "4", "5 (least deprived)"]
imd_data = resistant_pct(imd_sex_df, imd_col, infections_col, resistant_col).reindex(imd_order)

# Age Group
age_order = ["less than 1", "1 to 4", "5 to 9", "10 to 14", "15 to 44", "45 to 64", "65 to 74", "75 and over"]
age_data = resistant_pct(imd_sex_df, "Age group (years)", infections_col, resistant_col).reindex(age_order)

# Ethnicity
eth_col = [c for c in eth_df.columns if "Ethnic" in c][0]
eth_data = resistant_pct(eth_df, eth_col, eth_infections_col, eth_resistant_col)

#Put in Grid
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

with row1_col1:
    st.subheader("By Sex")
    st.altair_chart(sex_chart, use_container_width=True)

with row1_col2:
    st.subheader("By IMD Deprivation Quintile")
    st.altair_chart(gradient_bar_chart(imd_data, order=imd_order, scheme="oranges", title="By IMD Quintile"), use_container_width=True)
    

with row2_col1:
    st.subheader("By Age Group")
    st.altair_chart(gradient_bar_chart(age_data, order=age_order, scheme="greens", title="By Age Group"), use_container_width=True)

with row2_col2:
    st.subheader("By Ethnicity")
    st.altair_chart(gradient_bar_chart(eth_data, scheme="purples", title="By Ethnicity"), use_container_width=True)