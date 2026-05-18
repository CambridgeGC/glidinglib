from pathlib import Path
from pprint import pprint

from glidinglib.clients.aerolog_aircraft_client import AerologAircraftClient


def main() -> None:
    excel_path = Path(input("Path to Aerolog aircraft Excel file: ").strip('"'))

    client = AerologAircraftClient(app_name="FlightUpdater")

    records = client.update_cache_from_excel(excel_path)

    print(f"Aircraft loaded: {len(records)}")
    print(f"JSON cache: {client.cache_path}")
    print(f"Excel cache: {client.excel_cache_path}")

    print("\nFirst few records:")
    for aircraft in records[:10]:
        print("-" * 80)
        pprint(aircraft)

    print("\nLookup examples:")

    for reg in ("267", "841", "GOCGC", "GC"):
        aircraft = (
            client.find_by_registration(reg)
            or client.find_by_short_registration(reg)
            or client.find_by_competition_registration(reg)
        )

        print(f"\nLookup {reg}:")
        pprint(aircraft)


if __name__ == "__main__":
    main()