from typing import Iterable

from glidinglib.models.aerolog_flight_model import AerologFlight
from glidinglib.models.combination_flight_model import CombinationFlight


def map_aerolog_flights_to_combination_flights(
    flights: Iterable[AerologFlight],
) -> list[CombinationFlight]:
    return [
        map_aerolog_flight_to_combination_flight(flight)
        for flight in flights
    ]


def map_aerolog_flight_to_combination_flight(
    flight: AerologFlight,
) -> CombinationFlight:
    return CombinationFlight(
        source="AL",
        uuid=str(flight.sync_key or ""),
        sequence_number=flight.sequence_number,
        sync_key=flight.sync_key,

        flight_date=flight.flight_date,

        registration=flight.registration,
        callsign=flight.callsign,
        aircraft_type=flight.aircraft_type,

        launch_method=flight.launch_method,

        takeoff_time=flight.takeoff_time,
        landing_time=flight.landing_time,
        duration_minutes=flight.duration_minutes,

        pic_membership_number=flight.pic_membership_number,
        pic_name="",
        p2_membership_number=flight.p2_membership_number,
        p2_name="",
        paying_pilot_membership_number=flight.third_party_payer_account
        or flight.pic_membership_number,

        tow_registration=flight.tug_registration,
        tow_pilot_name=flight.tug_pilot,
        tow_landing_time=flight.tug_landing_time,
        tow_duration_minutes=flight.tug_time_minutes,
        tow_release_height_ft=flight.launch_height_ft,

        airfield_takeoff=flight.airfield_takeoff,
        airfield_landing=flight.airfield_landing,
        runway_takeoff=flight.runway_takeoff,
        runway_landing=flight.runway_landing,

        remarks=flight.remarks,
    )