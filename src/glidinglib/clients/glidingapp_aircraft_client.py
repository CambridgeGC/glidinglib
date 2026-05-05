from typing import Any
import requests


class GlidingAppAircraftClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "X-API-KEY": self.api_key,
            "Accept": "application/json",
        }

    def fetch_aircraft(self) -> list[dict[str, Any]]:
        url = f"{self.base_url}/api/aircraft.json"

        response = requests.get(
            url,
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        return data if isinstance(data, list) else []