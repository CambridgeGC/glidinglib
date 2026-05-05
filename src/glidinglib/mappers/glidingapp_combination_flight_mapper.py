from typing import Iterable

from glidinglib.models.glidingapp_flight_model import GlidingAppFlight
from glidinglib.models.combination_flight_model import CombinationFlight
from glidinglib.mappers.glidingapp_flight_mapper import map_glidingapp_flight

def _round_height_ft(value: int | float | None) -> int | None:
    if value in (None, 0):
        return None
    try:
        return int(round(float(value) / 100) * 100)
    except (TypeError, ValueError):
        return None
    
def map_glidingapp_day_to_combination_flights(
    api_rows: Iterable[dict],
) -> list[CombinationFlight]:
    """
    Map a full day's Gliding.App flight rows into combination flight records.

    For aerotows:
      - the glider flight has tow_flight_uuid / sleep_uuid
      - the tow flight is matched by uuid
      - the resulting record contains both glider and tow-plane details

    Non-aerotow flights become records with only the glider-flight fields.
    """

    flights = [map_glidingapp_flight(row) for row in api_rows]
    return combine_glidingapp_flights(flights)


def combine_glidingapp_flights(
    flights: Iterable[GlidingAppFlight],
) -> list[CombinationFlight]:
    flights = list(flights)
    flights_by_uuid = {f.uuid: f for f in flights if f.uuid}

    combination_flights: list[CombinationFlight] = []

    for flight in flights:
        # Tow-plane flights are supporting records, not primary output records.
        if _is_tow_plane_flight(flight):
            continue

        tow_flight = None
        if flight.tow_flight_uuid:
            tow_flight = flights_by_uuid.get(flight.tow_flight_uuid)

        combination_flights.append(
            map_glidingapp_flight_to_combination_flight(
                flight,
                tow_flight=tow_flight,
            )
        )

    return combination_flights


def map_glidingapp_flight_to_combination_flight(
    flight: GlidingAppFlight,
    tow_flight: GlidingAppFlight | None = None,
) -> CombinationFlight:
    record = CombinationFlight(
        # --- identity ---
        source="GA",
        uuid=flight.uuid,
        sequence_number=flight.sequence_number,
        sync_key=flight.id,        

        # --- glider flight ---
        flight_date=flight.flight_date,

        registration=flight.registration,
        callsign=flight.callsign,
        aircraft_type=flight.aircraft_type,

        launch_method=flight.launch_method,

        takeoff_time=flight.takeoff_time,
        landing_time=flight.landing_time,
        duration_minutes=flight.duration_minutes,

        # --- crew ---
        pic_membership_number=flight.pic_membership_number,
        pic_name=flight.pic_name,
        p2_membership_number=flight.p2_membership_number,
        p2_name=flight.p2_name,
        paying_pilot_membership_number=flight.paying_pilot_membership_number,


        # --- misc ---
        airfield_takeoff=flight.departure_airfield,
        airfield_landing=flight.arrival_airfield,
        remarks=flight.notes,
        category=flight.category,
    )

    if tow_flight is not None:
        record.tow_uuid = tow_flight.uuid
        record.tow_registration = tow_flight.registration
        record.tow_callsign = tow_flight.callsign
        record.tow_aircraft_type = tow_flight.aircraft_type
        record.tow_pilot_account = tow_flight.pic_membership_number
        record.tow_pilot_name = tow_flight.pic_name
        record.tow_takeoff_time = tow_flight.takeoff_time
        record.tow_landing_time = tow_flight.landing_time
        record.tow_duration_minutes = tow_flight.duration_minutes
        record.tow_release_height_ft = _round_height_ft(tow_flight.launch_height_ft)

    return record


def _is_tow_plane_flight(flight: GlidingAppFlight) -> bool:
    """
    Decide whether this row is itself the tug/SEP/TMG record.

    In Gliding.App, a glider aerotow is normally launch_method == "aerotow"
    and has tow_flight_uuid populated.

    The tug/SEP/TMG row is supporting data and should not become its own
    CombinationFlight output record.
    """
    return flight.launch_method in {
        "tmg-aerotow",
        "sep-aerotow",
        "sep",
    }

def map_glidingapp_flights_to_combination_flights(
    flights: Iterable[GlidingAppFlight],
) -> list[CombinationFlight]:
    return combine_glidingapp_flights(flights)