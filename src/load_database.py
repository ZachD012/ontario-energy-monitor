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