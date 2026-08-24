import pandas as pd
from pathlib import Path


CSV_FILE = Path("data/raw/demand.csv")


def parse_demand_data(file_path):

    df = pd.read_csv(
        file_path,
        skiprows=3
    )

    df = df.rename(
        columns={
            "Date": "day",
            "Hour": "hour",
            "Market Demand": "market_demand_mw",
            "Ontario Demand": "demand_mw"
        }
    )

    df["timestamp"] = (
        pd.to_datetime(df["day"])
        + pd.to_timedelta(
            df["hour"] - 1,
            unit="h"
        )
    )

    df = df[
        [
            "timestamp",
            "demand_mw",
            "market_demand_mw"
        ]
    ]

    return df


if __name__ == "__main__":

    df = parse_demand_data(CSV_FILE)

    print(f"Records parsed: {len(df)}")

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 10 records:")
    print(df.head(10))

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isna().sum())