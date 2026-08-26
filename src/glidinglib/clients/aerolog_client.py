import json
import logging
from datetime import date
from typing import Any

import requests

from glidinglib.mappers.aerolog_tech_qualification_mapper import (
    map_aerolog_tech_qualification,
)

logger = logging.getLogger(__name__)


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

    def _post_with_retry(
        self,
        path: str,
        json_payload: Any,
    ) -> Any:
        url = f"{self.base_url}{path}"

        resp = self.session.post(
            url,
            json=json_payload,
            headers=self._auth_headers(),
            timeout=self.timeout,
        )

        if resp.status_code == 401:
            self.login()

            resp = self.session.post(
                url,
                json=json_payload,
                headers=self._auth_headers(),
                timeout=self.timeout,
            )

        if logger.isEnabledFor(logging.DEBUG):
            headers_repr = {
                k: ("Bearer [hidden]" if k.lower() == "authorization" else v)
                for k, v in resp.request.headers.items()
            }
            request_body = resp.request.body
            if isinstance(request_body, bytes):
                request_body = request_body.decode("utf-8")
            try:
                parsed_body = json.loads(request_body) if request_body else None
                body_repr = json.dumps(parsed_body, indent=2, ensure_ascii=False) if parsed_body else ""
            except (TypeError, json.JSONDecodeError):
                body_repr = str(request_body)

            logger.debug(
                "Aerolog HTTP request | Method: %s | URL: %s | Headers: %s | Body: %s",
                resp.request.method,
                resp.request.url,
                headers_repr,
                body_repr,
            )

        try:
            resp.raise_for_status()

        except requests.HTTPError as exc:
            raise RuntimeError(
                f"Aerolog POST failed\n"
                f"Status: {resp.status_code}\n"
                f"URL: {url}\n"
                f"Response:\n{resp.text}\n\n"
                f"Payload:\n{json_payload}"
            ) from exc

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
        return self._post_with_retry(
            "/api/Services/ImportFlightLogsFrom3ps",
            records,
        )

    def get_members_tech_qualif(
        self,
        start_account: int | str = 1,
        end_account: int | str | None = None,
    ):
        if end_account is None:
            end_account = start_account

        is_single_account = str(start_account).strip() == str(end_account).strip()

        # Aerolog SQL API performs string/lexicographical comparisons on Account numbers
        # (e.g. '1' to '100' excludes '15' because '15' > '100').
        # When querying ranges, fetch wide range ("0" to "999999") and filter numerically in Python.
        if is_single_account:
            api_start = str(start_account).strip()
            api_end = str(end_account).strip()
        else:
            api_start = "0"
            api_end = "999999"

        payload = self._get_with_retry(
            "/api/Services/GetMembersTechQualif",
            {
                "StartAccount": api_start,
                "EndAccount": api_end,
            },
        )

        rows = self._extract_tech_qualif_rows(payload)
        mapped_quals = [
            map_aerolog_tech_qualification(row)
            for row in rows
        ]

        if not is_single_account:
            try:
                s_int = int(start_account)
                e_int = int(end_account)
                mapped_quals = [
                    q for q in mapped_quals
                    if q.account and str(q.account).strip().isdigit() and s_int <= int(str(q.account).strip()) <= e_int
                ]
            except (ValueError, TypeError):
                pass

        return mapped_quals

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

    def get_memberships_on_period(
        self,
        start_date: date | str,
        end_date: date | str,
    ) -> list[dict[str, Any]]:
        sd_str = start_date.isoformat() if isinstance(start_date, date) else str(start_date)
        ed_str = end_date.isoformat() if isinstance(end_date, date) else str(end_date)
        payload = self._get_with_retry(
            "/api/Services/GetMembershipOnPeriod",
            {
                "StartDate": sd_str,
                "EndDate": ed_str,
            },
        )
        if isinstance(payload, dict):
            return payload.get("data") or []
        if isinstance(payload, list):
            return payload
        return []

    def get_members_contact_details(
        self,
        start_account: int | str = 1,
        end_account: int | str = 999999,
    ) -> list[dict[str, Any]]:
        is_single_account = str(start_account).strip() == str(end_account).strip()
        if is_single_account:
            api_start = str(start_account).strip()
            api_end = str(end_account).strip()
        else:
            api_start = "0"
            api_end = "999999"

        payload = self._get_with_retry(
            "/api/Services/GetMembersContactDetails",
            {
                "StartAccount": api_start,
                "EndAccount": api_end,
            },
        )
        items = payload.get("data") if isinstance(payload, dict) else payload
        if not isinstance(items, list):
            return []

        if not is_single_account:
            try:
                s_int = int(start_account)
                e_int = int(end_account)
                filtered = []
                for it in items:
                    acc_str = str(it.get("account") or it.get("Account") or "").strip()
                    if acc_str.isdigit() and s_int <= int(acc_str) <= e_int:
                        filtered.append(it)
                return filtered
            except (ValueError, TypeError):
                pass

        return items