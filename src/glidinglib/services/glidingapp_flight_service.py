from datetime import date
from typing import Iterable, Literal

from glidinglib.clients.glidingapp_client import GlidingAppClient
from glidinglib.mappers.glidingapp_flight_mapper import map_glidingapp_flight
from glidinglib.models.glidingapp_flight_model import GlidingAppFlight


DataSource = Literal["live", "test", "config"]


class GlidingAppFlightService:
    def __init__(
        self,
        config: dict,
        default_data_source: DataSource = "config",
        timeout: int = 30,
    ):
        self.config = config
        self.default_data_source = default_data_source
        self.timeout = timeout

    def _resolve_data_source(self, data_source: DataSource | None = None) -> str:
        selected = data_source or self.default_data_source

        if selected == "config":
            selected = self.config["glidingapp"].get("data_source", "live")

        if selected not in ("live", "test"):
            raise ValueError(
                f"Invalid GlidingApp data source: {selected!r}. "
                "Expected 'live', 'test', or 'config'."
            )

        return selected

    def _client_for(self, data_source: DataSource | None = None) -> GlidingAppClient:
        ga_config = self.config["glidingapp"]
        selected = self._resolve_data_source(data_source)

        if selected == "live":
            base_url = ga_config["server"]
            api_key = ga_config["api_key"]
        else:
            base_url = ga_config["test_server"]
            api_key = ga_config["test_api_key"]

        return GlidingAppClient(
            base_url=base_url,
            api_key=api_key,
            timeout=self.timeout,
        )

    def get_flights(
        self,
        year: int | None = None,
        flight_date: date | None = None,
        date_updated: date | None = None,
        deleted: bool = False,
        data_source: DataSource | None = None,
    ) -> list[GlidingAppFlight]:
        client = self._client_for(data_source)

        raw_rows = client.fetch_flights(
            year=year,
            flight_date=flight_date,
            date_updated=date_updated,
            deleted=deleted,
        )

        return [map_glidingapp_flight(row) for row in raw_rows or []]

    def get_flights_for_date(
        self,
        flight_date: date,
        data_source: DataSource | None = None,
    ) -> list[GlidingAppFlight]:
        return self.get_flights(
            flight_date=flight_date,
            data_source=data_source,
        )

    def get_flights_for_year(
        self,
        year: int,
        data_source: DataSource | None = None,
    ) -> list[GlidingAppFlight]:
        return self.get_flights(
            year=year,
            data_source=data_source,
        )

    def get_updated_flights(
        self,
        updated_date: date,
        data_source: DataSource | None = None,
    ) -> list[GlidingAppFlight]:
        return self.get_flights(
            date_updated=updated_date,
            data_source=data_source,
        )

    def get_deleted_flights_for_date(
        self,
        flight_date: date,
        data_source: DataSource | None = None,
    ) -> list[GlidingAppFlight]:
        return self.get_flights(
            flight_date=flight_date,
            deleted=True,
            data_source=data_source,
        )

    def get_training_flights(
        self,
        flights: Iterable[GlidingAppFlight],
    ) -> list[GlidingAppFlight]:
        return [flight for flight in flights if flight.is_training]

    def get_cross_country_flights(
        self,
        flights: Iterable[GlidingAppFlight],
    ) -> list[GlidingAppFlight]:
        return [flight for flight in flights if flight.is_cross_country]