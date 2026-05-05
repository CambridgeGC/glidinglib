from datetime import date
from typing import Any

from glidinglib.clients.ktrax_flight_client import KtraxFlightClient
from glidinglib.mappers.ktrax_flight_mapper import map_ktrax_flight
from glidinglib.models.ktrax_flight_model import KtraxFlight


class KtraxFlightService:
    def __init__(self, client: KtraxFlightClient):
        self.client = client

    def get_flights_for_date(self, flight_date: date) -> list[KtraxFlight]:
        raw_rows = self.client.fetch_flights(flight_date)

        seq_index: dict[Any, dict[str, Any]] = {
            row.get("seq"): row
            for row in raw_rows
            if row.get("seq") is not None
        }

        return [
            map_ktrax_flight(
                api_row=row,
                sequence_number=index,
                seq_index=seq_index,
            )
            for index, row in enumerate(raw_rows, start=1)
        ]