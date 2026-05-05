from datetime import date
from typing import Optional

import requests


class GlidingAppFlightClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "X-API-KEY": self.api_key,
            "Accept": "application/json",
        }

    def fetch_flights(
        self,
        year: Optional[int] = None,
        flight_date: Optional[date] = None,
        date_updated: Optional[date] = None,
        deleted: bool = False,
    ) -> list[dict]:
        """
        Fetch flights from GlidingApp.

        API:
            /api/flights.json

        Optional filters:
            year=YYYY
            date=YYYY-MM-DD
            date_updated=YYYY-MM-DD
            deleted=1
        """

        params: dict[str, str | int] = {}

        if year is not None:
            params["year"] = year

        if flight_date is not None:
            params["date"] = flight_date.isoformat()

        if date_updated is not None:
            params["date_updated"] = date_updated.isoformat()

        if deleted:
            params["deleted"] = 1

        url = f"{self.base_url}/api/flights.json"

        response = requests.get(
            url,
            headers=self._headers(),
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        # Defensive: API should return a list, but ensure we always return a list
        if isinstance(data, list):
            return data

        return []