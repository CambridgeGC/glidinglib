from datetime import datetime
from typing import Any, Optional

from glidinglib.models.ktrax_flight_model import KtraxFlight


AIRCRAFT_MAPPING = {
    "GBODU": "G-BODU",
    "GCGWP": "G-CGWP",
    "SB": "TUG SB",
    "GC": "TUG GC",
    "GELSB": "TUG SB",
    "GOCGC": "TUG GC",
}

TMG_CALLSIGNS = {"G-BODU", "G-CGWP", "G-DKDP"}
TUG_CALLSIGNS = {"TUG SB", "TUG GC"}

LAUNCH_METHOD_MAP = {
    "S": "self-launch",
    "T": "aerotow",
    "W": "winch",
}


def _normalise_aircraft(value: Any) -> str:
    raw = str(value or "").upper().replace("-", "")
    return AIRCRAFT_MAPPING.get(raw, str(value or ""))


def _launch_method_for_ktrax(
    raw_launch: str,
    callsign: str,
    tow_callsign: str,
) -> str:
    if callsign in TMG_CALLSIGNS:
        return "tmg"

    if callsign in TUG_CALLSIGNS:
        return "sep-aerotow" if tow_callsign else "sep"

    return LAUNCH_METHOD_MAP.get(raw_launch, raw_launch)


def _parse_date(value: Any):
    if not value:
        return None
    return datetime.fromisoformat(str(value)).date()


def _parse_time(value: Any):
    if not value:
        return None
    return datetime.strptime(str(value), "%H:%M").time()


def _height_ft_from_metres(value: Any) -> Optional[int]:
    if value in (None, "", 0):
        return None

    try:
        feet = float(value) * 3.28084
        return int(round(feet / 100) * 100)
    except (TypeError, ValueError):
        return None


def _height_m(value: Any) -> Optional[float]:
    if value in (None, "", 0):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _person_name(person: Any) -> str:
    if not isinstance(person, dict):
        return ""
    return str(person.get("name") or "")


def _person_number(person: Any) -> str:
    if not isinstance(person, dict):
        return ""
    return str(person.get("nr") or "")


def map_ktrax_flight(
    api_row: dict[str, Any],
    sequence_number: int,
    seq_index: dict[Any, dict[str, Any]],
) -> KtraxFlight:
    raw_launch = str(api_row.get("launch") or "")
    raw_cn = str(api_row.get("cn") or "")

    callsign = _normalise_aircraft(raw_cn)
    registration = api_row.get("cs") or ""
    tow_registration = api_row.get("tow_cs") or ""

    tow_seq = api_row.get("tow_seq")
    tow_id = api_row.get("tow_id") or ""
    tow_cn = api_row.get("tow_cn") or api_row.get("tow_cs") or ""
    tow_registration = api_row.get("tow_cs") or ""

    tow_callsign = _normalise_aircraft(tow_cn)

    if not tow_callsign and tow_seq not in (None, "", 0):
        tow = seq_index.get(tow_seq)
        if tow:
            tow_callsign = _normalise_aircraft(tow.get("cn") or tow.get("cs"))

    launch_method = _launch_method_for_ktrax(
        raw_launch=raw_launch,
        callsign=callsign,
        tow_callsign=tow_callsign,
    )

    dalt = api_row.get("dalt")

    return KtraxFlight(
        uuid=str(api_row.get("seq") or ""),
        sequence_number=int(api_row.get("seqnr") or sequence_number),

        flight_date=_parse_date(api_row.get("date")),

        flarm_id=str(api_row.get("id") or "").split(":")[-1].upper(),
        callsign=callsign,
        raw_callsign=raw_cn,
        registration=registration,
        aircraft_type=str(api_row.get("actype") or ""),

        raw_launch_method=raw_launch,
        launch_method=launch_method,

        tow_flight_uuid=str(tow_seq or tow_id or ""),
        tow_callsign=tow_callsign,
        tow_registration=tow_registration,

        takeoff_time=_parse_time((api_row.get("tkof") or {}).get("time")),
        landing_time=_parse_time((api_row.get("ldg") or {}).get("time")),

        launch_height_m=_height_m(dalt),
        launch_height_ft=_height_ft_from_metres(dalt),

        pic_name=_person_name(api_row.get("p1")),
        pic_membership_number=_person_number(api_row.get("p1")),

        p2_name=_person_name(api_row.get("p2")),
        p2_membership_number=_person_number(api_row.get("p2")),
    )