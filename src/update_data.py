from fetch_ieso_generation import download_ieso_data
from load_database import create_database


def update_data():

    print("Starting Ontario Energy Monitor data update...")

    print("\n1. Downloading latest IESO data...")
    download_ieso_data()

    print("\n2. Rebuilding database...")
    create_database()

    print("\nData update complete!")


if __name__ == "__main__":
    update_data()