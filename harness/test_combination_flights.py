# tools/test_combination_flights.py

import argparse
import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime, time
from pathlib import Path
from typing import Any

from glidinglib.clients.ktrax_flight_client import KtraxFlightClient
from glidinglib.services.glidingapp_flight_service import GlidingAppFlightService
from glidinglib.services.ktrax_flight_service import KtraxFlightService
from glidinglib.services.aerolog_flight_service import AerologFlightService

from glidinglib.mappers.glidingapp_combination_flight_mapper import (
    map_glidingapp_flights_to_combination_flights,
)
from glidinglib.mappers.ktrax_combination_flight_mapper import (
    map_ktrax_flights_to_combination_flights,
)
from glidinglib.mappers.aerolog_combination_flight_mapper import (
    map_aerolog_flights_to_combination_flights,
)


def load_config() -> dict:
    root = Path(__file__).resolve().parents[1]
    config_path = root / "config.json"

    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def json_default(value: Any):
    if isinstance(value, (date, time, datetime)):
        return value.isoformat()

    if is_dataclass(value):
        return asdict(value)

    return str(value)


def dump(title: str, data: Any) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(data, default=json_default, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "flight_date",
        nargs="?",
        default="2026-04-24",
        help="Date in YYYY-MM-DD format",
    )    
    parser.add_argument(
        "--data-source",
        choices=["live", "test", "config"],
        default="config",
        help="Use live, test, or whatever config.json specifies",
    )

    args = parser.parse_args()
    flight_date = date.fromisoformat(args.flight_date)

    config = load_config()

    # ------------------------------------------------------------------
    # Gliding.App
    # ------------------------------------------------------------------
    ga_service = GlidingAppFlightService(config)

    ga_flights = ga_service.get_flights_for_date(
        flight_date=flight_date,
        data_source=args.data_source,
    )

    ga_combined = map_glidingapp_flights_to_combination_flights(ga_flights)

    dump(
        f"Gliding.App Combination Flights - {flight_date}",
        ga_combined,
    )

    # ------------------------------------------------------------------
    # KTrax
    # ------------------------------------------------------------------
    kt_client = KtraxFlightClient()
    kt_service = KtraxFlightService(kt_client)

    kt_flights = kt_service.get_flights_for_date(flight_date)

    kt_combined = map_ktrax_flights_to_combination_flights(kt_flights)

    dump(
        f"KTrax Combination Flights - {flight_date}",
        kt_combined,
    )

    # ------------------------------------------------------------------
    # Aerolog
    # ------------------------------------------------------------------
    al_service = AerologFlightService(config)

    al_flights = al_service.get_flights_for_date(
        flight_date=flight_date,
        data_source=args.data_source,
    )

    al_combined = map_aerolog_flights_to_combination_flights(al_flights)

    dump(
        f"Aerolog Combination Flights - {flight_date}",
        al_combined,
    )


if __name__ == "__main__":
    main()