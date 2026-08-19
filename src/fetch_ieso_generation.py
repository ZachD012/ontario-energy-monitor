import requests
import xml.etree.ElementTree as ET
from pathlib import Path


IESO_URL = (
    "https://reports-public.ieso.ca/public/"
    "GenOutputbyFuelHourly/PUB_GenOutputbyFuelHourly.xml"
)

RAW_DATA_DIR = Path("data/raw")


def download_ieso_data():
    print("Downloading IESO generation data...")

    response = requests.get(IESO_URL, timeout=30)
    response.raise_for_status()

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_file = RAW_DATA_DIR / "generation.xml"

    output_file.write_bytes(response.content)

    print(f"Downloaded {len(response.content):,} bytes")
    print(f"Saved to: {output_file}")

    return output_file


def inspect_xml(file_path):
    print("\nInspecting XML structure...")

    tree = ET.parse(file_path)
    root = tree.getroot()

    doc_body = list(root)[1]
    daily_data = list(doc_body)[1]
    hourly_data = list(daily_data)[1]

    print("\nFirst HourlyData record:")

    hour = list(hourly_data)[0]
    print(f"Hour: {hour.text}")

    print("\nRaw FuelTotal XML:")

    for fuel_total in list(hourly_data)[1:]:
        fuel = list(fuel_total)[0]
        energy = list(fuel_total)[1]

        print("\n------------------------------")
        print(f"Fuel: {fuel.text}")
        print("Raw EnergyValue element:")
        print(ET.tostring(energy, encoding="unicode"))

if __name__ == "__main__":
    file_path = download_ieso_data()
    inspect_xml(file_path)