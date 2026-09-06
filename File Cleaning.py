import pandas as pd

def clean_data(file):

    #clean " from the file

    with open(file, "r") as f:
        content = f.read()

    content = content.replace('"','').strip()

    with open(file, "w") as f:
        f.write(content)

    #clean unneccessary columns and rows with empty entries

    df = pd.read_csv(f"{file}")

    df = df.dropna()

    df.to_csv(f"CLEAN {file}", index=False)


clean_data("AMR 2024.csv")