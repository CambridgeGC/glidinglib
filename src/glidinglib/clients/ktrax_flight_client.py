from datetime import date, datetime
from zoneinfo import ZoneInfo
from typing import Any

import requests




UK_TZ = ZoneInfo("Europe/London")


def _ktrax_tz_for_date(flight_date: date) -> str:
    """
    Return '1' for BST, '0' for GMT.
    """
    dt = datetime.combine(flight_date, datetime.min.time())
    offset = dt.replace(tzinfo=UK_TZ).utcoffset()

    return "1" if offset and offset.total_seconds() == 3600 else "0"

class KtraxFlightClient:
    def __init__(
        self,
        ktrax_id: str = "GRANSDEN LODGE",
        tz: str | None = None,
        timeout: int = 30,
    ):
        self.ktrax_id = ktrax_id
        self.tz = tz
        self.timeout = timeout
        self.base_url = "https://ktrax.kisstech.ch/backend/logbook"

    def fetch_flights(self, flight_date: date) -> list[dict[str, Any]]:
        date_str = flight_date.isoformat()

        tz = self.tz or _ktrax_tz_for_date(flight_date)

        params = {
            "query_type": "ap",
            "id": self.ktrax_id,
            "tz": tz,
            "dbeg": date_str,
            "dend": date_str,
        }

        response = requests.get(
            self.base_url,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        sorties = data.get("sorties", data)

        if isinstance(sorties, list):
            return sorties

        return []