import pandas as pd

def clean_data(file):

    #clean " from the file

    # with open(file, "r") as f:
    #     content = f.read()

    # content = content.replace('"','').strip()

    # with open(file, "w") as f:
    #     f.write(content)

    #clean unneccessary columns and rows with empty entries

    df = pd.read_csv(f"{file}")

    df = df.dropna()

    df.to_csv(f"{file}-copy", index=False)


clean_data("AMR Location - ESPAUR-2024-2025.csv")