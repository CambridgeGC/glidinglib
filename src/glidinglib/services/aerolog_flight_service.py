from datetime import date
from typing import Literal
import json

from glidinglib.clients.aerolog_flight_client import AerologFlightClient
from glidinglib.mappers.aerolog_flight_mapper import (
    map_aerolog_flight,
    map_aerolog_flight_to_import_payload,
)
from glidinglib.models.aerolog_flight_model import AerologFlight


DataSource = Literal["live", "test", "config"]


class AerologFlightService:
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
            selected = self.config["aerolog"].get("data_source", "live")

        if selected not in ("live", "test"):
            raise ValueError(
                f"Invalid Aerolog data source: {selected!r}. "
                "Expected 'live', 'test', or 'config'."
            )

        return selected

    def _client_for(self, data_source: DataSource | None = None) -> AerologFlightClient:
        aerolog_config = self.config["aerolog"]
        selected = self._resolve_data_source(data_source)

        if selected == "live":
            base_url = aerolog_config["base_url"]
            email = aerolog_config["email"]
            password = aerolog_config["password"]
        else:
            base_url = aerolog_config["test_base_url"]
            email = aerolog_config["test_email"]
            password = aerolog_config.get("test_password", aerolog_config["password"])

        return AerologFlightClient(
            base_url=base_url,
            email=email,
            password=password,
            timeout=self.timeout,
        )

    def get_flight_log_on_period(
        self,
        start_date: date,
        end_date: date,
        data_source: DataSource | None = None,
    ) -> list[AerologFlight]:
        client = self._client_for(data_source)

        raw_rows = client.get_flight_log_on_period(
            start_date=start_date,
            end_date=end_date,
        )

        return [map_aerolog_flight(row) for row in raw_rows or []]

    def get_flights_for_date(
        self,
        flight_date: date,
        data_source: DataSource | None = None,
    ) -> list[AerologFlight]:
        return self.get_flight_log_on_period(
            start_date=flight_date,
            end_date=flight_date,
            data_source=data_source,
        )

    def send_flight_log_to_aerolog(
        self,
        flights: list[AerologFlight],
        data_source: DataSource | None = None,
        dry_run: bool = True,
    ) -> dict:
        selected = self._resolve_data_source(data_source)

        payload = [
            map_aerolog_flight_to_import_payload(flight)
            for flight in flights
        ]

        # Treat either test OR explicit dry_run as no-send with payload output for verification
        if selected == "test" or dry_run:
            print()
            print("Aerolog payload (dry run):")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            print()

            return {
                "status": "dry_run",
                "sent": False,
                "record_count": len(payload),
                "payload": payload,
                "data_source": selected,
            }

        client = self._client_for(data_source)

        response = client.send_flight_log_to_aerolog(payload)

        return {
            "status": "sent",
            "sent": True,
            "record_count": len(payload),
            "data_source": selected,
            "response": response,
        }