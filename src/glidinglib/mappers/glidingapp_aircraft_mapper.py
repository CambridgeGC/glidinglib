from typing import Any

from glidinglib.models.glidingapp_aircraft_model import GlidingAppAircraft


LAUNCH_METHOD_MAP = {
    "lier": "winch",
    "sleep": "aerotow",
    "zelf": "self-launch",
    "tmg": "tmg",
    "tmg-a": "tmg-aerotow",
    "sep": "sep",
    "sep-a": "sep-aerotow",
    "car": "car",
    "bungee": "bungee",
    "overig": "other",
}

CATEGORY_MAP = {
    "prive": "private",
    "club": "club",
    "sleep": "tug",
    "tug": "tug",
}


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def map_glidingapp_aircraft(api_row: dict[str, Any]) -> GlidingAppAircraft:
    raw_launch_method = str(api_row.get("start_methode") or "").lower()

    return GlidingAppAircraft(
        id=api_row.get("id"),

        callsign=str(api_row.get("callsign") or ""),
        registration=str(api_row.get("registratie") or ""),
        flarm_id=str(api_row.get("flarm") or ""),
        aircraft_type=str(api_row.get("type") or ""),

        category=CATEGORY_MAP.get(str(api_row.get("category") or "").lower(), str(api_row.get("category") or "")),
        configuration=str(api_row.get("configuration") or ""),

        pilots=_to_int(api_row.get("pilots")),
        launch_method=LAUNCH_METHOD_MAP.get(raw_launch_method, raw_launch_method),

        in_dto=bool(api_row.get("in_dto", False)),
    )