from datetime import datetime
from typing import Any, Optional

from glidinglib.models.glidingapp_flight_model import GlidingAppFlight


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


def _parse_date(value: Any):
    if not value:
        return None
    return datetime.fromisoformat(str(value)).date()


def _parse_datetime(value: Any) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(str(value))


def _parse_time(value: Any):
    if not value:
        return None
    return datetime.strptime(str(value), "%H:%M").time()


def _to_float(value: Any) -> Optional[float]:
    if value in (None, ""):
        return None
    return float(value)

def _to_feet(value: Any) -> Optional[int]:
    if value in (None, "", 0):
        return None
    try:
        return int(round(float(value) * 3.28084))
    except (TypeError, ValueError):
        return None

def map_glidingapp_flight(api_row: dict) -> GlidingAppFlight:
    raw_method = (api_row.get("start_methode") or "").lower()
    launch_method = LAUNCH_METHOD_MAP.get(raw_method, raw_method)

    return GlidingAppFlight(
        id=api_row.get("id"),
        uuid=api_row.get("uuid", ""),
        sequence_number=api_row.get("volg_nummer"),
        is_deleted=api_row.get("is_deleted", False),
        is_locked=api_row.get("is_locked", False),
        day_id=api_row.get("dag_id"),

        flight_date=_parse_date(api_row.get("datum")),
        date_created=_parse_datetime(api_row.get("date_created")),
        date_updated=_parse_datetime(api_row.get("date_updated")),
        is_private=api_row.get("is_prive", False),

        departure_airfield=api_row.get("vertrek_vliegveld", ""),
        arrival_airfield=api_row.get("aankomst_vliegveld", ""),

        aircraft_id=api_row.get("kist_id", 0),
        callsign=api_row.get("callsign", ""),
        registration=api_row.get("registratie", ""),
        aircraft_type=api_row.get("type", ""),
        flarm_id=api_row.get("flarm", ""),

        pic_membership_number=api_row.get("pic_m_id", ""),
        pic_id=api_row.get("gezagvoerder_id", 0),
        pic_name=api_row.get("gezagvoerder_naam", ""),

        p2_membership_number=api_row.get("second_pilot_m_id", ""),
        p2_id=api_row.get("tweede_inzittende_id"),
        p2_name=api_row.get("tweede_inzittende_naam", ""),

        paying_pilot_membership_number=api_row.get("paying_pilot_m_id", ""),
        paying_pilot_name=api_row.get("paying_pilot_name", ""),
        paying_pilot_member_id=api_row.get("betalend_lid_id"),

        raw_launch_method=raw_method,
        launch_method=launch_method,
        tow_flight_uuid=api_row.get("sleep_uuid", ""),

        category=api_row.get("category", ""),
        is_flight_instruction=api_row.get("is_fis", False),
        is_training=api_row.get("is_training", False),
        is_exam=api_row.get("is_examen", False),
        is_proficiency_check=api_row.get("is_profcheck", False),
        is_cross_country=api_row.get("is_overland", False),

        distance_km=api_row.get("afstand", 0),
        launch_count=api_row.get("starts", 1),
        takeoff_time=_parse_time(api_row.get("start_tijd")),
        landing_time=_parse_time(api_row.get("landings_tijd")),
        duration_minutes=api_row.get("vluchtduur", 0),
        block_time_minutes=api_row.get("blocktime", 0),
        motor_end=float(api_row.get("motor_end") or 0.0),
        motor_minutes=float(api_row.get("motor_minutes") or 0.0),
        launch_height_ft=_to_feet(api_row.get("height")),

        notes=api_row.get("bijzonderheden", ""),
        igc_path=api_row.get("igc", ""),
        voucher=api_row.get("voucher"),

        changes=api_row.get("changes") or [],
        auth_date=_parse_datetime(api_row.get("auth_date")),
        auth_name=api_row.get("auth_name"),
        signed_date=_parse_datetime(api_row.get("signed_date")),
        signed_cert=api_row.get("signed_cert"),
        signed_remark=api_row.get("signed_remark"),
        badges=api_row.get("badges") or [],
    )

