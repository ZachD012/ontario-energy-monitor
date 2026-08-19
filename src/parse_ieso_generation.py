import xml.etree.ElementTree as ET
from pathlib import Path


XML_FILE = Path("data/raw/generation.xml")

NAMESPACE = "{http://www.ieso.ca/schema}"


def parse_generation_data(file_path):

    tree = ET.parse(file_path)
    root = tree.getroot()

    doc_body = root.find(f"{NAMESPACE}DocBody")

    records = []

    for daily_data in doc_body.findall(f"{NAMESPACE}DailyData"):

        day_element = daily_data.find(f"{NAMESPACE}Day")
        day = day_element.text

        for hourly_data in daily_data.findall(
            f"{NAMESPACE}HourlyData"
        ):

            hour_element = hourly_data.find(
                f"{NAMESPACE}Hour"
            )
            hour = int(hour_element.text)

            for fuel_total in hourly_data.findall(
                f"{NAMESPACE}FuelTotal"
            ):

                fuel_element = fuel_total.find(
                    f"{NAMESPACE}Fuel"
                )

                energy_element = fuel_total.find(
                    f"{NAMESPACE}EnergyValue"
                )

                output_element = None
                
                if energy_element is not None:
                    output_element = energy_element.find(
                        f"{NAMESPACE}Output"
                    )

                output_mwh = None

                if output_element is not None and output_element.text:
                    output_mwh = int(output_element.text)

                quality_element = energy_element.find(
                    f"{NAMESPACE}OutputQuality"
                )

                output_quality = None

                if quality_element is not None and quality_element.text:
                    output_quality = int(quality_element.text)

                record = {
                    "day": day,
                    "hour": hour,
                    "fuel_type": fuel_element.text,
                    "output_mwh": output_mwh,
                    "output_quality": output_quality,
                }

                records.append(record)

    return records


if __name__ == "__main__":

    records = parse_generation_data(XML_FILE)

    print(f"Records extracted: {len(records)}")

    print("\nFirst 10 records:")

    for record in records[:10]:
        print(record)