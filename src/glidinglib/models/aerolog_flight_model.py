# src/glidinglib/models/aerolog_flight_model.py

from dataclasses import dataclass
from datetime import date, time
from typing import Optional


@dataclass
class AerologFlight:
    flight_date: Optional[date] = None
    sync_key: Optional[int] = None

    sequence_number: int = 0

    registration: str = ""
    callsign: str = ""
    aircraft_type: str = ""
    aircraft_model: str = ""

    flight_type_code: str = ""
    flight_type_description: str = ""

    pic_membership_number: str = ""
    p2_membership_number: str = ""

    voucher_number: str = ""
    special_charge_code: str = ""
    special_charge_description: str = ""

    airfield_takeoff: str = ""
    airfield_landing: str = ""
    landout_site: str = ""

    takeoff_time: Optional[time] = None
    landing_time: Optional[time] = None
    duration_minutes: int = 0

    launch_method: str = ""
    raw_launch_method: str = ""

    origin_data_entry: str = "3"
    origin_data_entry_description: str = "GlidingLib"

    launch_height_ft: Optional[int] = None
    landing_count: int = 0

    tug_registration: str = ""
    tug_landing_time: Optional[time] = None
    tug_time_minutes: int = 0
    tug_pilot: str = ""

    guest_name: str = ""

    p1_share_pay: Optional[int] = None
    p2_share_pay: Optional[int] = None
    guest_share_pay: Optional[int] = None
    third_party_payer_account: str = ""

    remarks: str = ""

    wind_speed: Optional[int] = None
    wind_direction: Optional[int] = None

    runway_takeoff: str = ""
    runway_landing: str = ""