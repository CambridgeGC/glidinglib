import json
import os
from datetime import date

from glidinglib.services.aerolog_flight_service import AerologFlightService


def load_config() -> dict:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.abspath(os.path.join(base_dir, "..", "config.json"))

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_time(value) -> str:
    return value.strftime("%H:%M") if value else ""


def print_flight_summary(flight) -> None:
    print(
        f"date={flight.flight_date}, "
        f"seq={flight.sequence_number}, "
        f"reg={flight.registration}, "
        f"callsign={flight.callsign}, "
        f"p1={flight.pic_membership_number}, "
        f"p2={flight.p2_membership_number}, "
        f"takeoff={format_time(flight.takeoff_time)}, "
        f"landing={format_time(flight.landing_time)}, "
        f"launch={flight.launch_method}, "
        f"duration={flight.duration_minutes}, "
        f"remarks={flight.remarks}, "
        f"launch_height_ft={flight.launch_height_ft}, "
    )


def main() -> int:
    try:
        config = load_config()
        service = AerologFlightService(config)

        test_date = date(2026, 4, 24)

        for data_source in ("config", "live", "test"):
            print()
            print(f"Fetching Aerolog {data_source} flights for {test_date}...")

            flights = service.get_flights_for_date(
                test_date,
                data_source=data_source,
            )

            print(f"Returned {len(flights)} flights")

            for flight in flights:
                print_flight_summary(flight)

        return 0

    except Exception:
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())