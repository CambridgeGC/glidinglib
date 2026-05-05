# src/glidinglib/mappers/aerolog_flight_mapper.py

from datetime import datetime, date, time
from typing import Any, Optional

from glidinglib.models.aerolog_flight_model import AerologFlight


GET_LAUNCH_METHOD_MAP = {
    "W": "winch",
    "A": "aerotow",
    "T": "aerotow",
    "B": "bungee",
    "S": "self-launch",
}

PUT_LAUNCH_METHOD_MAP = {
    "winch": "W",
    "aerotow": "A",
    "bungee": "B",
    "self-launch": "S",
}

TUG_MAPPING = {
    "G-OCGC": "TUG GC",
    "GOCGC": "TUG GC",
    "G-ELSB": "TUG SB",
    "GELSB": "TUG SB",
}

CALLSIGN_MAPPING = {
    "GOCGC": "GC",
    "G-OCGC": "GC",
    "GELSB": "SB",
    "G-ELSB": "SB",
    "GBODU": "DU",
    "G-BODU": "DU",
    "GCGWP": "WP",
    "G-CGWP": "WP",
    "GDKDP": "DP",
    "G-DKDP": "DP",
}

def _normalise_tug(value: Any) -> str:
    raw = str(value or "").upper().replace("-", "")
    return TUG_MAPPING.get(raw, str(value or ""))

def _normalise_callsign(value: Any) -> str:
    raw = str(value or "").strip().upper()
    raw_no_dash = raw.replace("-", "")

    return CALLSIGN_MAPPING.get(raw, CALLSIGN_MAPPING.get(raw_no_dash, raw))

def _parse_datetime(value: Any) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _parse_date(value: Any):
    dt = _parse_datetime(value)
    return dt.date() if dt else None


def _parse_time(value: Any):
    if not value:
        return None

    value = str(value).strip()
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            pass

    return None


def _format_date(value: date | None) -> str:
    return value.strftime("%d/%m/%Y") if value else ""


def _format_time(value: time | None) -> str:
    return value.strftime("%H:%M") if value else ""


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _put_if_present(payload: dict[str, Any], key: str, value: Any) -> None:
    if value not in (None, ""):
        payload[key] = value


def map_aerolog_flight(api_row: dict[str, Any]) -> AerologFlight:
    raw_launch = str(api_row.get("indLaunchType") or "")
    launch_method = GET_LAUNCH_METHOD_MAP.get(raw_launch, raw_launch)

    return AerologFlight(
        flight_date=_parse_date(api_row.get("date")),
        sequence_number=_to_int(api_row.get("seqInDate")),

        registration=str(api_row.get("registration") or ""),
        callsign=_normalise_callsign(
            api_row.get("regShort") or api_row.get("registration")
        ),
        flight_type_code=str(api_row.get("flightTypeCode") or ""),
        flight_type_description=str(api_row.get("flightTypeDesc") or ""),

        pic_membership_number=str(api_row.get("accountCodeP1") or ""),
        p2_membership_number=str(api_row.get("accountCodeP2") or ""),

        voucher_number=str(api_row.get("voucherSerialCode") or ""),
        special_charge_code=str(api_row.get("specialChargeCode") or ""),
        special_charge_description=str(api_row.get("specialChargeDescription") or ""),

        takeoff_time=_parse_time(api_row.get("timeTakeOff")),
        landing_time=_parse_time(api_row.get("timeLanding")),
        duration_minutes=_to_int(api_row.get("durationMinutes")),

        raw_launch_method=raw_launch,
        launch_method=launch_method,

        launch_height_ft=_to_int(api_row.get("heightRelease")),
        landing_count=_to_int(api_row.get("qtyLandings")),

        tug_registration=_normalise_tug(api_row.get("tugRegistration")),
        tug_time_minutes=_to_int(api_row.get("tugTimeMinutes")),
        tug_pilot=str(api_row.get("tugPilot") or ""),

        guest_name=str(api_row.get("guestName") or ""),
        remarks=str(api_row.get("remarks") or ""),

        runway_takeoff=str(api_row.get("runwayTakeOff") or ""),
        runway_landing=str(api_row.get("runwayLanding") or ""),
    )

def map_aerolog_flight_to_import_payload(flight: AerologFlight) -> dict[str, Any]:
    if flight.sync_key is None:
        raise ValueError("sync_key is required for Aerolog import")

    payload: dict[str, Any] = {
        "FlightDate": _format_date(flight.flight_date),
        "SyncKey": flight.sync_key,
        "AircraftRegistration": flight.registration,
        "AircraftType": flight.aircraft_type,
        "AircraftModel": flight.aircraft_model,
        "AccCodeP1": flight.pic_membership_number,
        "TimeTakeOff": _format_time(flight.takeoff_time),
        "LaunchType": PUT_LAUNCH_METHOD_MAP.get(
            flight.launch_method,
            flight.raw_launch_method or flight.launch_method,
        ),
        "OriginDataEntry": flight.origin_data_entry,
    }

    _put_if_present(payload, "FlightType", flight.flight_type_code)
    _put_if_present(payload, "AccCodeP2", flight.p2_membership_number)
    _put_if_present(payload, "VoucherNumber", flight.voucher_number)
    _put_if_present(payload, "SpecialChargeCode", flight.special_charge_code)
    _put_if_present(payload, "AirfieldTakeOff", flight.airfield_takeoff)
    _put_if_present(payload, "AirfieldLanding", flight.airfield_landing)
    _put_if_present(payload, "LandoutSite", flight.landout_site)
    _put_if_present(payload, "TimeLanding", _format_time(flight.landing_time))
    _put_if_present(payload, "FlightTimeMinutes", flight.duration_minutes)
    _put_if_present(payload, "OriginDataEntryDesc", flight.origin_data_entry_description)
    _put_if_present(payload, "ReleaseHeight", flight.launch_height_ft)
    _put_if_present(payload, "QtyLandings", flight.landing_count)
    _put_if_present(payload, "TugRegistration", flight.tug_registration)
    _put_if_present(payload, "TugTimeLanding", _format_time(flight.tug_landing_time))
    _put_if_present(payload, "TugTimeMinutes", flight.tug_time_minutes)
    _put_if_present(payload, "GuestName", flight.guest_name)
    _put_if_present(payload, "P1SharePay", flight.p1_share_pay)
    _put_if_present(payload, "P2SharePay", flight.p2_share_pay)
    _put_if_present(payload, "GuestSharePay", flight.guest_share_pay)
    _put_if_present(payload, "AccCode3pp", flight.third_party_payer_account)
    _put_if_present(payload, "Remarks", flight.remarks[:500])
    _put_if_present(payload, "WindSpeed", flight.wind_speed)
    _put_if_present(payload, "WindDirection", flight.wind_direction)
    _put_if_present(payload, "RwyTakeOff", flight.runway_takeoff)
    _put_if_present(payload, "RwyLanding", flight.runway_landing)

    return payload