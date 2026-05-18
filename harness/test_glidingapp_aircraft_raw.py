import json
from pathlib import Path
from pprint import pprint

from glidinglib.clients.glidingapp_client import GlidingAppClient
from glidinglib.mappers.glidingapp_aircraft_mapper import (
    map_glidingapp_aircraft,
)


def load_config() -> dict:
    root = Path(__file__).resolve().parents[1]
    config_path = root / "config.json"

    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    config = load_config()

    ga_config = config["glidingapp"]

    data_source = ga_config.get("data_source", "live")

    if data_source == "test":
        base_url = ga_config["test_server"]
        api_key = ga_config["test_api_key"]
    else:
        base_url = ga_config["server"]
        api_key = ga_config["api_key"]

    client = GlidingAppClient(
        base_url=base_url,
        api_key=api_key,
    )

    raw_aircraft = client.fetch_aircraft()

    print(f"Aircraft count: {len(raw_aircraft)}")
    print()

    mapped_aircraft = [
        map_glidingapp_aircraft(row)
        for row in raw_aircraft
    ]

    for aircraft in mapped_aircraft:
        print("=" * 80)

        print(
            f"{aircraft.registration:8} | "
            f"{aircraft.callsign:6} | "
            f"{aircraft.aircraft_type}"
        )

        print("-" * 80)

        pprint(vars(aircraft))

        print()


if __name__ == "__main__":
    main()