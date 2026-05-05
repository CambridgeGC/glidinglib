from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Any, Optional


@dataclass
class GlidingAppFlight:
    # Identifiers
    id: Optional[int] = None
    uuid: str = ""
    sequence_number: Optional[int] = None      # volg_nummer
    day_id: Optional[int] = None               # dag_id

    # State
    is_deleted: bool = False
    is_locked: bool = False
    is_private: bool = False                   # is_prive

    # Dates
    flight_date: Optional[date] = None                # datum
    date_created: Optional[datetime] = None
    date_updated: Optional[datetime] = None

    # Airfields
    departure_airfield: str = ""               # vertrek_vliegveld
    arrival_airfield: str = ""                 # aankomst_vliegveld

    # Aircraft
    aircraft_id: int = 0                       # kist_id
    callsign: str = ""
    registration: str = ""                     # registratie
    aircraft_type: str = ""                    # type
    flarm_id: str = ""                         # flarm

    # Crew
    pic_membership_number: str = ""            # pic_m_id
    pic_id: int = 0               # gezagvoerder_id
    pic_name: str = ""            # gezagvoerder_naam

    p2_membership_number: str = ""   # second_pilot_m_id
    p2_id: Optional[int] = None         # tweede_inzittende_id
    p2_name: str = ""                   # tweede_inzittende_naam

    paying_pilot_membership_number: str = ""   # paying_pilot_m_id
    paying_pilot_name: str = ""
    paying_pilot_member_id: Optional[int] = None     # betalend_lid_id

    # Launch
    launch_method: str = ""                    # start_methode, translated
    raw_launch_method: str = ""                # original start_methode
    tow_flight_uuid: str = ""                  # sleep_uuid

    # Flags/category
    category: str = ""
    is_flight_instruction: bool = False        # is_fis
    is_training: bool = False
    is_exam: bool = False
    is_proficiency_check: bool = False
    is_cross_country: bool = False

    # Metrics
    distance_km: int = 0                       # afstand
    launch_count: int = 1                      # starts
    duration_minutes: int = 0                  # vluchtduur
    block_time_minutes: int = 0                # blocktime
    motor_end: float = 0.0
    motor_minutes: float = 0.0
    launch_height_ft: Optional[float] = None    # height

    # Timing
    takeoff_time: Optional[time] = None        # start_tijd
    landing_time: Optional[time] = None        # landings_tijd

    # Additional
    notes: str = ""                            # bijzonderheden
    igc_path: str = ""                         # igc
    voucher: Any = None

    # Change/signing data
    changes: list[dict[str, Any]] = field(default_factory=list)
    auth_date: Optional[datetime] = None
    auth_name: Optional[str] = None
    signed_date: Optional[datetime] = None
    signed_cert: Optional[str] = None
    signed_remark: Optional[str] = None
    badges: list[Any] = field(default_factory=list)