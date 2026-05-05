import json
import os
from datetime import date

from glidinglib.clients.ktrax_flight_client import KtraxFlightClient
from glidinglib.services.ktrax_flight_service import KtraxFlightService


def load_config() -> dict:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.abspath(os.path.join(base_dir, "..", "config.json"))

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def print_flight_summary(flight) -> None:
    print(
        f"uuid={flight.uuid}, "
        f"flarm_id={flight.flarm_id}, "        
        f"seq={flight.sequence_number}, "
        f"date={flight.flight_date}, "
        f"callsign={flight.callsign}, "
        f"registration={flight.registration}, "        
        f"launch={flight.launch_method}, "
        f"takeoff={flight.takeoff_time}, "
        f"landing={flight.landing_time}, "
        f"tow_uuid={flight.tow_flight_uuid}, "
        f"height_ft={flight.launch_height_ft}"

    )


def main() -> int:
    try:
        config = load_config()
        kt_config = config.get("ktrax", {})

        client = KtraxFlightClient(
            ktrax_id=kt_config.get("id", "GRANSDEN LODGE"),
            tz=kt_config.get("tz", "1"),
        )

        service = KtraxFlightService(client)

        test_date = date(2026, 4, 23)

        print(f"Fetching Ktrax flights for {test_date}...")
        flights = service.get_flights_for_date(test_date)

        print(f"Returned {len(flights)} flights")

        for flight in flights[:20]:
            print_flight_summary(flight)

        return 0

    except Exception:
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())