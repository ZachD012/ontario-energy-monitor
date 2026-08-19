import pandas as pd

from parse_ieso_generation import (
    parse_generation_data
)


XML_FILE = "data/raw/generation.xml"


records = parse_generation_data(XML_FILE)

df = pd.DataFrame(records)

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

print("\nDataFrame created!")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 10 rows:")
print(df.head(10))
print("\nGeneration by fuel type:")

generation_by_fuel = (
    df.groupby("fuel_type")["output_mwh"]
      .sum()
      .sort_values(ascending=False)
)

print(generation_by_fuel)

print("\nGeneration percentage by fuel type:")

generation_percentage = (
    generation_by_fuel
    / generation_by_fuel.sum()
    * 100
)

print(generation_percentage.round(2))

print("\nGeneration by generation type:")

generation_by_type = (
    df.groupby("generation_type")["output_mwh"]
      .sum()
      .sort_values(ascending=False)
)

print(generation_by_type)

print("\nGeneration percentage by generation type:")

generation_type_percentage = (
    generation_by_type
    / generation_by_type.sum()
    * 100
)

print(generation_type_percentage.round(2))