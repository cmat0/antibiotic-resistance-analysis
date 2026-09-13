import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(layout="wide")

#MAP OF AMR BY REGION

@st.cache_data
def load_geojson():
    url = "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/Regions_December_2025_Boundaries_EN_BGC/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"
    return requests.get(url).json()
    
geojson = load_geojson()

df = pd.read_csv("Final Files/AMR_incidence_per_100000_with_totals.csv")
df_map = df[df["Region"] != "Total by Year"]

print(df.columns)

region_coords = {
    "London": (51.5074, -0.1278),
    "South East": (51.3, -0.5),
    "South West": (50.9, -3.5),
    "East of England": (52.2, 0.5),
    "East Midlands": (52.8, -1.0),
    "West Midlands": (52.5, -2.0),
    "North West": (53.8, -2.7),
    "North East": (54.9, -1.6),
    "Yorkshire and The Humber": (53.9, -1.3)
}

df_map["lat"] = df_map["Region"].map(lambda r: region_coords[r][0])
df_map["long"] = df_map["Region"].map(lambda r: region_coords[r][1])

fig = px.choropleth(
    df_map,
    geojson = geojson,
    locations="Region",
    featureidkey="properties.RGN25NM",
    color="Avg by Region",
    color_continuous_scale="reds",
    hover_name="Region"
)

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(height=500,width=500)

col1, col2 = st.columns([3,2])

with col1:
    st.plotly_chart(fig, use_container_width=True)

with col2:
    df = df.drop("Unnamed: 0",axis=1)

    st.markdown("""
    <style>
    .stTable table { font-size: 12px; }
    </style>
""", unsafe_allow_html=True)
    
    df.columns = pd.MultiIndex.from_tuples([
    ("Region", ""),
    ("AMR Burden per 100000 people per year", "2020"),
    ("AMR Burden per 100000 people per year", "2021"),
    ("AMR Burden per 100000 people per year", "2022"),
    ("AMR Burden per 100000 people per year", "2023"),
    ("AMR Burden per 100000 people per year", "2024"),
    ("Avg by Region", "")])
    st.table(df, hide_index=True,height=300)

# AMR LAG EFFECT ON CONSUMPTION

