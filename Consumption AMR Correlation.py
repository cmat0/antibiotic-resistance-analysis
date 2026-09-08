import pandas as pd
import matplotlib.pyplot as plt
import re

def perc_column(file1):

    matches = re.search(r"(\d+)-(\d+).csv",file1)
    year1,year2 = matches.groups()
    year3 = int(year2)+1

    df1 = pd.read_csv(f"joined_tables/{year1}-{year2}.csv")
    df2 = pd.read_csv(f"joined_tables/{year2}-{year3}.csv")
    print(df2)

perc_column("2020-2021.csv")

