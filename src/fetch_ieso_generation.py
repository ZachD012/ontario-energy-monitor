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

    print(f"Root element: {root.tag}")
    print(f"Number of child elements: {len(root)}")

    print("\nFirst-level elements:")

    for child in list(root)[:10]:
        print(f"  {child.tag}")


if __name__ == "__main__":
    file_path = download_ieso_data()
    inspect_xml(file_path)