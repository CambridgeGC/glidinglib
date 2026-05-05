from dataclasses import dataclass
from datetime import date, time
from typing import Optional


@dataclass
class KtraxFlight:
    uuid: str = ""                     # seq
    sequence_number: int = 0           # seqnr if present, otherwise generated

    flight_date: Optional[date] = None

    flarm_id: str = ""                 # id, e.g. icao:406256
    callsign: str = ""                 # normalised cn
    raw_callsign: str = ""             # original cn
    registration: str = ""             # registration (G-reg)
    aircraft_type: str = ""            # actype

    launch_method: str = ""
    raw_launch_method: str = ""

    tow_flight_uuid: str = ""          # tow_seq / tow_id
    tow_callsign: str = ""             # tow_cn / tow_cs
    tow_registration: str = ""             # tow registration

    takeoff_time: Optional[time] = None
    landing_time: Optional[time] = None

    launch_height_m: Optional[float] = None
    launch_height_ft: Optional[int] = None

    pic_name: str = ""
    pic_membership_number: str = ""

    p2_name: str = ""
    p2_membership_number: str = ""
