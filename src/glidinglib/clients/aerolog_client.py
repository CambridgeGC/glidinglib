from datetime import date
from typing import Any

import requests

from glidinglib.mappers.aerolog_tech_qualification_mapper import (
    map_aerolog_tech_qualification,
)


class AerologClient:
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

    def _get_with_retry(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"

        resp = self.session.get(
            url,
            params=params or {},
            headers=self._auth_headers(),
            timeout=self.timeout,
        )

        if resp.status_code == 401:
            self.login()
            resp = self.session.get(
                url,
                params=params or {},
                headers=self._auth_headers(),
                timeout=self.timeout,
            )

        resp.raise_for_status()
        return resp.json()

    def _put_with_retry(
        self,
        path: str,
        json_payload: Any,
    ) -> Any:
        url = f"{self.base_url}{path}"

        resp = self.session.put(
            url,
            json=json_payload,
            headers=self._auth_headers(),
            timeout=self.timeout,
        )

        if resp.status_code == 401:
            self.login()
            resp = self.session.put(
                url,
                json=json_payload,
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
        payload = self._get_with_retry(
            "/api/Services/GetFlightLogOnPeriod",
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
        return self._put_with_retry(
            "/api/importFlightLogsFrom3ps",
            records,
        )

    def get_members_tech_qualif(
        self,
        start_account: int | str,
        end_account: int | str | None = None,
    ):
        if end_account is None:
            end_account = start_account

        payload = self._get_with_retry(
            "/api/Services/GetMembersTechQualif",
            {
                "StartAccount": start_account,
                "EndAccount": end_account,
            },
        )

        rows = self._extract_tech_qualif_rows(payload)

        return [
            map_aerolog_tech_qualification(row)
            for row in rows
        ]

    def _extract_tech_qualif_rows(
        self,
        payload: Any,
    ) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []

        def walk(value: Any) -> None:
            if isinstance(value, list):
                for item in value:
                    walk(item)
                return

            if not isinstance(value, dict):
                return

            if "technicalQualifications" in value:
                account = value.get("account")

                name = (
                    value.get("name")
                    or f"{value.get('firstName', '')} {value.get('surname', '')}".strip()
                )

                for qual in value["technicalQualifications"]:
                    qual = dict(qual)
                    qual["_account"] = account
                    qual["_name"] = name
                    result.append(qual)

                return

            if "code" in value:
                result.append(value)
                return

            for key in (
                "technicalQualifications",
                "qualifications",
                "membersTechQualif",
                "data",
                "members",
                "member",
                "results",
            ):
                if key in value:
                    walk(value[key])

        walk(payload)
        return result