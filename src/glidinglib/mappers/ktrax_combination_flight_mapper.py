from typing import Iterable

from glidinglib.models.ktrax_flight_model import KtraxFlight
from glidinglib.models.combination_flight_model import CombinationFlight


def map_ktrax_flights_to_combination_flights(
    flights: Iterable[KtraxFlight],
) -> list[CombinationFlight]:
    flights = list(flights)

    flights_by_uuid = {
        flight.uuid: flight
        for flight in flights
        if flight.uuid
    }

    combination_flights: list[CombinationFlight] = []

    for flight in flights:
        # Skip tug rows, but keep the glider aerotow rows.
        if _is_tug_row(flight):
            continue

        tow_flight = None
        if flight.tow_flight_uuid:
            candidate = flights_by_uuid.get(flight.tow_flight_uuid)
            if candidate is not None and _is_tug_row(candidate):
                tow_flight = candidate

        combination_flights.append(
            map_ktrax_flight_to_combination_flight(
                flight,
                tow_flight=tow_flight,
            )
        )

    return combination_flights


def map_ktrax_flight_to_combination_flight(
    flight: KtraxFlight,
    tow_flight: KtraxFlight | None = None,
) -> CombinationFlight:
    return CombinationFlight(
        source="KT",
        uuid=str(flight.uuid or ""),
        sequence_number=flight.sequence_number,

        flight_date=flight.flight_date,

        registration=flight.registration,
        callsign=flight.callsign,
        aircraft_type=flight.aircraft_type,

        launch_method=flight.launch_method,

        takeoff_time=flight.takeoff_time,
        landing_time=flight.landing_time,
        duration_minutes=getattr(flight, "duration_minutes", 0) or 0,

        pic_membership_number=flight.pic_membership_number,
        pic_name=flight.pic_name,
        p2_membership_number=flight.p2_membership_number,
        p2_name=flight.p2_name,
        paying_pilot_membership_number=flight.pic_membership_number,

        tow_uuid=tow_flight.uuid if tow_flight else flight.tow_flight_uuid,
        tow_registration=tow_flight.registration if tow_flight else "",
        tow_callsign=tow_flight.callsign if tow_flight else flight.tow_callsign,
        tow_aircraft_type=tow_flight.aircraft_type if tow_flight else "",
        tow_pilot_account=tow_flight.pic_membership_number if tow_flight else "",
        tow_pilot_name=tow_flight.pic_name if tow_flight else "",
        tow_takeoff_time=tow_flight.takeoff_time if tow_flight else None,
        tow_landing_time=tow_flight.landing_time if tow_flight else None,
        tow_duration_minutes=getattr(tow_flight, "duration_minutes", 0) if tow_flight else 0,

        tow_release_height_ft=flight.launch_height_ft,

        remarks="",
    )


def _is_tug_row(flight: KtraxFlight) -> bool:
    callsign = (flight.callsign or "").strip().upper()
    registration = (flight.registration or "").strip().upper()
    aircraft_type = (flight.aircraft_type or "").strip().upper()

    return (
        callsign.startswith("TUG")
        or registration.startswith("TUG")
        or aircraft_type in {"TUG", "PA25", "PA-25"}
    )