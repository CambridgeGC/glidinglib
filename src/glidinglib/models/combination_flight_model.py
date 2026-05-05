from dataclasses import dataclass
from datetime import date, time
from typing import Optional


@dataclass
class CombinationFlight:
    # --- identity ---
    source: str = ""                 # GA / KT / AL
    uuid: str = ""            # GA uuid / KT id etc
    sequence_number: Optional[int] = None
    sync_key: Optional[int] = None   # Aerolog

    # --- glider flight ---
    flight_date: Optional[date] = None

    registration: str = ""
    callsign: str = ""
    aircraft_type: str = ""

    launch_method: str = ""

    takeoff_time: Optional[time] = None
    landing_time: Optional[time] = None
    duration_minutes: int = 0

    # --- crew ---
    pic_membership_number: str = ""
    pic_name: str = ""
    p2_membership_number: str = ""
    p2_name: str = ""
    paying_pilot_membership_number: str = ""

    # --- tow (if aerotow) ---
    tow_uuid: str = ""
    tow_registration: str = ""
    tow_callsign: str = ""
    tow_aircraft_type: str = ""
    tow_pilot_account: str = ""
    tow_pilot_name: str = ""
    tow_takeoff_time: Optional[time] = None
    tow_landing_time: Optional[time] = None
    tow_duration_minutes: int = 0
    tow_release_height_ft: Optional[float] = None

    # --- misc ---
    airfield_takeoff: str = ""
    airfield_landing: str = ""
    runway_takeoff: str = ""
    runway_landing: str = ""
    category: str = ""
    remarks: str = ""

    # --- helpers (domain-safe, not UI) ---
    def is_aerotow(self) -> bool:
        return self.launch_method == "aerotow"

    def has_tow(self) -> bool:
        return bool(self.tow_registration)

    def duration_or_zero(self) -> int:
        return self.duration_minutes or 0