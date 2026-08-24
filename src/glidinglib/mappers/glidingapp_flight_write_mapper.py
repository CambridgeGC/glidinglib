from __future__ import annotations

from typing import Any

from glidinglib.models.glidingapp_flight_model import GlidingAppFlight


RAW_LAUNCH_METHOD_BY_DISPLAY = {
    "winch": "lier",
    "aerotow": "sleep",
    "self-launch": "zelf",
    "tmg": "tmg",
    "tmg-aerotow": "tmg-a",
    "sep": "sep",
    "sep-aerotow": "sep-a",
    "car": "car",
    "bungee": "bungee",
    "other": "overig",
}


def _time_string(value: Any) -> str:
    return value.strftime("%H:%M") if value is not None else ""


def _height_metres(flight: GlidingAppFlight) -> int | float:
    # Preserve GA's original metre value unless the editor explicitly changes it.
    if flight.launch_height_m not in (None, ""):
        value = float(flight.launch_height_m)
        return int(value) if value.is_integer() else value
    if flight.launch_height_ft in (None, "", 0):
        return 0
    return int(round(float(flight.launch_height_ft) / 3.28084))


def _raw_launch_method(flight: GlidingAppFlight) -> str:
    raw = (flight.raw_launch_method or "").strip().lower()
    if raw:
        return raw
    return RAW_LAUNCH_METHOD_BY_DISPLAY.get(
        (flight.launch_method or "").strip().lower(),
        (flight.launch_method or "").strip().lower(),
    )


def map_glidingapp_flight_to_write_payload(
    flight: GlidingAppFlight,
) -> dict[str, Any]:
    """Build the complete payload required by GA's flight PUT endpoint."""
    if not flight.uuid:
        raise ValueError("Cannot update a Gliding.App flight without a uuid.")
    if flight.flight_date is None:
        raise ValueError(f"Flight {flight.uuid} has no flight date.")

    return {
        "uuid": flight.uuid,
        "volg_nummer": flight.sequence_number,
        "is_deleted": bool(flight.is_deleted),
        "dag_id": flight.day_id,
        "datum": flight.flight_date.isoformat(),
        "vertrek_vliegveld": flight.departure_airfield or "",
        "aankomst_vliegveld": flight.arrival_airfield or "",
        "kist_id": flight.aircraft_id,
        "callsign": flight.callsign or "",
        "registratie": flight.registration or "",
        "type": flight.aircraft_type or "",
        "flarm": flight.flarm_id or "",
        "gezagvoerder_id": flight.pic_id,
        "gezagvoerder_naam": flight.pic_name or "",
        "tweede_inzittende_id": flight.p2_id,
        "tweede_inzittende_naam": flight.p2_name or "",
        "betalend_lid_id": flight.paying_pilot_member_id,
        "start_methode": _raw_launch_method(flight),
        "sleep_uuid": flight.tow_flight_uuid or "",
        "category": flight.category or "",
        "is_fis": bool(flight.is_flight_instruction),
        "is_training": bool(flight.is_training),
        "is_examen": bool(flight.is_exam),
        "is_profcheck": bool(flight.is_proficiency_check),
        "is_overland": bool(flight.is_cross_country),
        "afstand": int(flight.distance_km or 0),
        "starts": int(flight.launch_count or 1),
        "start_tijd": _time_string(flight.takeoff_time),
        "landings_tijd": _time_string(flight.landing_time),
        "vluchtduur": int(flight.duration_minutes or 0),
        "blocktime": int(flight.block_time_minutes or 0),
        "height": _height_metres(flight),
        "bijzonderheden": flight.notes or "",
    }

    if flight.voucher:
        payload["voucher"] = flight.voucher

    return payload
