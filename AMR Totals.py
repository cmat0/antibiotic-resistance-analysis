import pandas as pd
import matplotlib.pyplot as plt
import os

df = pd.read_csv("AMR Incidence per 100000/AMR_incidence_per_100000_all_years.csv")
df.loc['Total by Year'] = df.sum(numeric_only=True) #add a total row
df['Avg by Region'] = df[['AMR Burden rate per 100000 population 2020',
       'AMR Burden rate per 100000 population 2021',
       'AMR Burden rate per 100000 population 2022',
       'AMR Burden rate per 100000 population 2023',
       'AMR Burden rate per 100000 population 2024']].mean(axis=1)

df.to_csv("AMR Incidence per 100000/AMR_incidence_per_100000_with_totals.csv")
                 