from datetime import date
from typing import Any, Optional

import requests


class GlidingAppClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()

    def _headers(self) -> dict[str, str]:
        return {
            "X-API-KEY": self.api_key,
            "Accept": "application/json",
        }

    def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        response = self.session.get(
            f"{self.base_url}{path}",
            headers=self._headers(),
            params=params or {},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def _post(
        self,
        path: str,
        body: dict[str, Any],
    ) -> Any:
        response = self.session.post(
            f"{self.base_url}{path}",
            headers=self._headers(),
            json=body,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def _put(
        self,
        path: str,
        body: dict[str, Any],
    ) -> Any:
        response = self.session.put(
            f"{self.base_url}{path}",
            headers=self._headers(),
            json=body,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    # ---------------- Accounts ----------------

    def fetch_accounts(self) -> list[dict[str, Any]]:
        data = self._get("/api/accounts.json")
        return data if isinstance(data, list) else []

    def update_account(
        self,
        account_id: int | str,
        data_fields: dict[str, Any],
    ) -> Any:
        return self._put(
            "/api/accounts.json",
            {
                "id": account_id,
                "data": data_fields,
            },
        )

    # ---------------- Aircraft ----------------

    def fetch_aircraft(self) -> list[dict[str, Any]]:
        data = self._get("/api/aircraft.json")
        return data if isinstance(data, list) else []

    # ---------------- Flights ----------------

    def fetch_flights(
        self,
        year: Optional[int] = None,
        flight_date: Optional[date] = None,
        date_updated: Optional[date] = None,
        deleted: bool = False,
    ) -> list[dict[str, Any]]:
        params: dict[str, str | int] = {}

        if year is not None:
            params["year"] = year

        if flight_date is not None:
            params["date"] = flight_date.isoformat()

        if date_updated is not None:
            params["date_updated"] = date_updated.isoformat()

        if deleted:
            params["deleted"] = 1

        data = self._get("/api/flights.json", params=params)
        return data if isinstance(data, list) else []

    # ---------------- Competencies ----------------

    def fetch_competencies(self) -> list[dict[str, Any]]:
        data = self._get("/api/competencies.json")
        return data if isinstance(data, list) else []

    def fetch_user_competencies(
        self,
        user_id: int | str,
    ) -> list[dict[str, Any]]:
        data = self._get(
            "/api/competencies/user.json",
            params={"user_id": user_id},
        )
        return data if isinstance(data, list) else []

    def assign_competency(
        self,
        user_id: int | str,
        competency_id: int | str,
        date_assigned: str | None = None,
        date_valid_to: str | None = None,
    ) -> Any:
        body: dict[str, Any] = {
            "user_id": user_id,
            "id": competency_id,
            "score": "assigned",
        }

        if date_assigned:
            body["date_assigned"] = date_assigned

        if date_valid_to:
            body["date_valid_to"] = date_valid_to

        return self._post(
            "/api/competencies/assign.json",
            body,
        )

    def revoke_competency(
        self,
        user_id: int | str,
        competency_id: int | str,
    ) -> Any:
        return self._post(
            "/api/competencies/revoke.json",
            {
                "user_id": user_id,
                "id": competency_id,
            },
        )