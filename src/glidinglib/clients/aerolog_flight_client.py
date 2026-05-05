from datetime import date
from typing import Any

import requests


class AerologFlightClient:
    def __init__(
        self,
        base_url: str,
        email: str,
        password: str,
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.password = password
        self.timeout = timeout
        self.session = requests.Session()
        self.token: str | None = None

    def login(self) -> None:
        resp = self.session.post(
            f"{self.base_url}/api/Login",
            json={
                "email": self.email,
                "password": self.password,
            },
            timeout=self.timeout,
        )
        resp.raise_for_status()

        data = resp.json()
        if not data.get("authenticated"):
            raise RuntimeError(data.get("message", "Aerolog login failed"))

        self.token = data["token"]

    def _auth_headers(self) -> dict[str, str]:
        if not self.token:
            self.login()

        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

    def _get_with_retry(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        resp = self.session.get(
            url,
            params=params,
            headers=self._auth_headers(),
            timeout=self.timeout,
        )

        # Retry once if token expired
        if resp.status_code == 401:
            self.login()
            resp = self.session.get(
                url,
                params=params,
                headers=self._auth_headers(),
                timeout=self.timeout,
            )

        resp.raise_for_status()
        return resp.json()

    def get_flight_log_on_period(
        self,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        url = f"{self.base_url}/api/Services/GetFlightLogOnPeriod"

        payload = self._get_with_retry(
            url,
            {
                "StartDate": start_date.isoformat(),
                "EndDate": end_date.isoformat(),
            },
        )

        if isinstance(payload, dict):
            return payload.get("data") or []

        if isinstance(payload, list):
            return payload

        return []

    def send_flight_log_to_aerolog(
        self,
        records: list[dict[str, Any]],
    ) -> dict[str, Any]:
        url = f"{self.base_url}/api/importFlightLogsFrom3ps"

        resp = self.session.put(
            url,
            json=records,
            headers=self._auth_headers(),
            timeout=self.timeout,
        )

        # Retry once if token expired
        if resp.status_code == 401:
            self.login()
            resp = self.session.put(
                url,
                json=records,
                headers=self._auth_headers(),
                timeout=self.timeout,
            )

        resp.raise_for_status()
        return resp.json()