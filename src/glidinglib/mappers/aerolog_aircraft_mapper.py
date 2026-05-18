from typing import Any

from glidinglib.models.aerolog_aircraft_model import AerologAircraft


def _text(value: Any) -> str:
    return str(value or "").strip()


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    return str(value or "").strip().upper() in {"TRUE", "YES", "Y", "1"}


def map_aerolog_aircraft(row: dict[str, Any]) -> AerologAircraft:
    return AerologAircraft(
        model=_text(row.get("MODEL")),
        aircraft_type=_text(row.get("TYPE")),
        owner=_text(row.get("OWNER")),
        ledger_account=_text(row.get("LEDGER ACCOUNT")),

        registration=_text(row.get("REGISTRATION")),
        short_registration=_text(row.get("SHORT REGISTRATION")),
        competition_registration=_text(row.get("COMPETITION REGISTRATION")),

        third_party_owned_but_used_by_club=_bool(
            row.get("THIRD PARTY OWNED BUT USED BY THE CLUB")
        ),
        club_owned_but_used_by_third_party=_bool(
            row.get("CLUB OWNED BUT USED BY THIRD PARTY")
        ),

        tach_unit=_text(row.get("TACH UNIT")),
        hobbs_unit=_text(row.get("HOBBS UNIT")),

        is_tug=_bool(row.get("AIRCRAFT IS USED AS TUG")),
        flight_time_charge_mode=_text(row.get("FLIGHT TIME CHARGE MODE")),
        visitor_aircraft=_bool(row.get("VISITOR AIRCRAFT")),
        apply_aircraft_ledger_account_to_all_activity_charges=_bool(
            row.get("APPLY AIRCRAFT LEDGER ACCOUNT TO ALL ACTIVITY CHARGES")
        ),
        ignore_conflicts_on_flight_log=_bool(
            row.get("IGNORE CONFLICTS ON FLIGHT LOG")
        ),
    )