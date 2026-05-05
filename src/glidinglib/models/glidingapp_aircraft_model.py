from dataclasses import dataclass
from typing import Optional


@dataclass
class GlidingAppAircraft:
    id: Optional[int] = None

    callsign: str = ""
    registration: str = ""
    flarm_id: str = ""
    aircraft_type: str = ""

    category: str = ""
    configuration: str = ""

    pilots: int = 0
    launch_method: str = ""

    in_dto: bool = False