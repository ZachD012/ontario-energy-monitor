import sqlite3
from pathlib import Path

import pandas as pd

from parse_ieso_generation import parse_generation_data


XML_FILE = Path("data/raw/generation.xml")
DATABASE_FILE = Path("data/processed/energy.db")


def create_database():

    DATABASE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    records = parse_generation_data(XML_FILE)

    df = pd.DataFrame(records)

    print(f"Records loaded into DataFrame: {len(df)}")

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

    print("\nColumns being loaded into database:")
    print(df.columns.tolist())

    connection = sqlite3.connect(DATABASE_FILE)

    df.to_sql(
        "generation",
        connection,
        if_exists="replace",
        index=False
    )

    connection.close()

    print(f"Database created: {DATABASE_FILE}")


if __name__ == "__main__":
    create_database()