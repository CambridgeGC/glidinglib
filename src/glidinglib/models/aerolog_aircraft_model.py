from dataclasses import dataclass


@dataclass
class AerologAircraft:
    model: str = ""
    aircraft_type: str = ""
    owner: str = ""
    ledger_account: str = ""

    registration: str = ""
    short_registration: str = ""
    competition_registration: str = ""

    third_party_owned_but_used_by_club: bool = False
    club_owned_but_used_by_third_party: bool = False

    tach_unit: str = ""
    hobbs_unit: str = ""

    is_tug: bool = False
    flight_time_charge_mode: str = ""
    visitor_aircraft: bool = False
    apply_aircraft_ledger_account_to_all_activity_charges: bool = False
    ignore_conflicts_on_flight_log: bool = False