import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from glidinglib.services.glidingapp_aircraft_service import GlidingAppAircraftService


def load_config() -> dict:
    p = Path(__file__).resolve()

    for parent in p.parents:
        config_path = parent / "config.json"
        if config_path.exists():
            with config_path.open("r", encoding="utf-8") as f:
                return json.load(f)

    raise FileNotFoundError("config.json not found in any parent directory")


def json_default(value: Any):
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
    config = load_config()

    service = GlidingAppAircraftService(config)

    aircraft = service.get_aircraft()
    by_registration = service.get_aircraft_by_registration()
    by_callsign = service.get_aircraft_by_callsign()

    print(f"Aircraft count: {len(aircraft)}")
    print(f"By registration count: {len(by_registration)}")
    print(f"By callsign count: {len(by_callsign)}")

    dump("All aircraft", aircraft)
    dump("First 5 aircraft", aircraft[:5])

    print()
    print("Lookup examples:")
    for key in ["G-BODU", "G-CGWP", "DU", "WP"]:
        match = by_registration.get(key.upper()) or by_callsign.get(key.upper())
        print(f"{key}: {match}")


if __name__ == "__main__":
    main()