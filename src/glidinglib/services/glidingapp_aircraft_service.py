from typing import Literal

from glidinglib.clients.glidingapp_client import GlidingAppClient
from glidinglib.mappers.glidingapp_aircraft_mapper import map_glidingapp_aircraft
from glidinglib.models.glidingapp_aircraft_model import GlidingAppAircraft


DataSource = Literal["live", "test", "config"]


class GlidingAppAircraftService:
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

    def _client_for(
        self,
        data_source: DataSource | None = None,
    ) -> GlidingAppClient:
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

    def get_aircraft(
        self,
        data_source: DataSource | None = None,
    ) -> list[GlidingAppAircraft]:
        client = self._client_for(data_source)
        raw_rows = client.fetch_aircraft()

        return [
            map_glidingapp_aircraft(row)
            for row in raw_rows or []
        ]

    def get_aircraft_by_registration(
        self,
        data_source: DataSource | None = None,
    ) -> dict[str, GlidingAppAircraft]:
        return {
            aircraft.registration.upper(): aircraft
            for aircraft in self.get_aircraft(data_source)
            if aircraft.registration
        }

    def get_aircraft_by_callsign(
        self,
        data_source: DataSource | None = None,
    ) -> dict[str, GlidingAppAircraft]:
        return {
            aircraft.callsign.upper(): aircraft
            for aircraft in self.get_aircraft(data_source)
            if aircraft.callsign
        }