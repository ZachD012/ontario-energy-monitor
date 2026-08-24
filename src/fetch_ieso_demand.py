import requests
from pathlib import Path


IESO_DEMAND_URL = (
    "https://reports-public.ieso.ca/public/"
    "Demand/PUB_Demand.csv"
)

RAW_DATA_DIR = Path("data/raw")


def download_ieso_demand():
    print("Downloading latest IESO demand data...")

    response = requests.get(
        IESO_DEMAND_URL,
        timeout=30
    )

    response.raise_for_status()

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = RAW_DATA_DIR / "demand.csv"

    output_file.write_bytes(
        response.content
    )

    print(
        f"Downloaded {len(response.content):,} bytes"
    )

    print(
        f"Saved to: {output_file}"
    )

    return output_file


if __name__ == "__main__":
    download_ieso_demand()