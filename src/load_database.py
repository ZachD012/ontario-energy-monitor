import sqlite3
from pathlib import Path

import pandas as pd

from parse_ieso_generation import parse_generation_data
from parse_ieso_demand import parse_demand_data


XML_FILE = Path("data/raw/generation.xml")
DEMAND_FILE = Path("data/raw/demand.csv")
DATABASE_FILE = Path("data/processed/energy.db")


def validate_generation_data(df):

    print("\nValidating generation data...")

    if df.empty:
        raise ValueError(
            "Generation validation failed: DataFrame is empty."
        )

    if df["timestamp"].isna().any():
        raise ValueError(
            "Generation validation failed: Missing timestamps found."
        )

    if df["output_mwh"].isna().all():
        raise ValueError(
            "Generation validation failed: "
            "No generation output values found."
        )

    minimum_records = 10000

    if len(df) < minimum_records:
        raise ValueError(
            f"Generation validation failed: Only {len(df):,} "
            f"records found. Expected at least {minimum_records:,}."
        )

    print("Generation data validation passed.")


def validate_demand_data(df):

    print("\nValidating demand data...")

    if df.empty:
        raise ValueError(
            "Demand validation failed: DataFrame is empty."
        )

    if df["timestamp"].isna().any():
        raise ValueError(
            "Demand validation failed: Missing timestamps found."
        )

    if df["demand_mw"].isna().any():
        raise ValueError(
            "Demand validation failed: Missing demand values."
        )

    minimum_records = 1000

    if len(df) < minimum_records:
        raise ValueError(
            f"Demand validation failed: Only {len(df):,} "
            f"records found. Expected at least {minimum_records:,}."
        )

    print("Demand data validation passed.")



def create_database():

    DATABASE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    records = parse_generation_data(XML_FILE)

    df = pd.DataFrame(records)

    print(f"Records loaded into DataFrame: {len(df)}")

    demand_df = parse_demand_data(DEMAND_FILE)
    
    print(f"Demand records loaded into DataFrame: {len(demand_df)}")

    def classify_fuel(fuel):

        if fuel == "NUCLEAR":
            return "Nuclear"

        if fuel in ["HYDRO", "WIND", "SOLAR", "BIOFUEL"]:
            return "Renewable"

        if fuel == "GAS":
            return "Fossil"

        return "Other"

    df["generation_type"] = df["fuel_type"].apply(
        classify_fuel
    )

    df["timestamp"] = pd.to_datetime(
        df["day"]
    ) + pd.to_timedelta(
         df["hour"] - 1,
        unit="h"
    )

    validate_generation_data(df)

    validate_demand_data(demand_df)

    print("\nGeneration columns being loaded:")
    print(df.columns.tolist())

    print("\nDemand columns being loaded:")
    print(demand_df.columns.tolist())

    connection = sqlite3.connect(DATABASE_FILE)

    df.to_sql(
        "generation",
        connection,
        if_exists="replace",
        index=False
    )

    demand_df.to_sql(
        "demand",
        connection,
        if_exists="replace",
        index=False
    )

    connection.close()

    print(f"Database created: {DATABASE_FILE}")


if __name__ == "__main__":
    create_database()