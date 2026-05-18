from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

from glidinglib.utils.app_paths import get_app_data_dir


class OgnDdbClient:
    DEFAULT_URL = "http://ddb.glidernet.org/download/?j=1"
    DEFAULT_CACHE_FILE = "ogn_ddb.json"

    def __init__(
        self,
        app_name: str = "GlidingLib",
        cache_dir: str | Path | None = None,
        cache_file: str = DEFAULT_CACHE_FILE,
        url: str = DEFAULT_URL,
        timeout: int = 30,
    ):
        self.cache_dir = Path(cache_dir) if cache_dir else get_app_data_dir(app_name)
        self.cache_file = cache_file
        self.url = url
        self.timeout = timeout

        self._records: list[dict[str, Any]] | None = None

        self._by_device_id: dict[str, dict[str, Any]] = {}
        self._by_registration: dict[str, dict[str, Any]] = {}
        self._by_cn: dict[str, list[dict[str, Any]]] = {}
        self._by_aircraft_model: dict[str, list[dict[str, Any]]] = {}        

    @property
    def cache_path(self) -> Path:
        return self.cache_dir / self.cache_file

    def load(
        self,
        force_refresh: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Load OGN DDB records.

        Behaviour:
        - If force_refresh=True:
            Always try to download fresh data.
            If download fails, fall back to cache.

        - If force_refresh=False:
            If cache exists:
                Try download first.
                If download fails, use cache.
            If cache does not exist:
                Download or raise error.

        After loading, indexes are rebuilt.
        """

        if force_refresh:
            records = self.download_or_cache()

        elif self.cache_path.exists():
            try:
                records = self.download()
            except requests.RequestException:
                records = self.load_from_cache()

        else:
            records = self.download_or_cache()

        self._records = records
        self._build_indexes(records)

        return records

    def download_or_cache(self) -> list[dict[str, Any]]:
        try:
            return self.download()
        except requests.RequestException as exc:
            if self.cache_path.exists():
                return self.load_from_cache()

            raise RuntimeError(
                f"Could not download OGN DDB and no cache exists at {self.cache_path}"
            ) from exc

    def download(self) -> list[dict[str, Any]]:
        response = requests.get(
            self.url,
            timeout=self.timeout,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()

        data = response.json()
        records = self._extract_records(data)

        self.save_to_cache(records)
        return records

    def save_to_cache(self, records: list[dict[str, Any]]) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        with self.cache_path.open("w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

    def load_from_cache(self) -> list[dict[str, Any]]:
        with self.cache_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return self._extract_records(data)

    def _extract_records(self, data: Any) -> list[dict[str, Any]]:
        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            for key in ("devices", "data", "records"):
                value = data.get(key)
                if isinstance(value, list):
                    return value

        return []
    
    def _build_indexes(
        self,
        records: list[dict[str, Any]],
    ) -> None:
        self._by_device_id.clear()
        self._by_registration.clear()
        self._by_cn.clear()
        self._by_aircraft_model.clear()

        for record in records:
            device_id = str(record.get("device_id", "")).upper().strip()
            registration = self._normalize_registration(record.get("registration", ""))
            if registration:
                self._by_registration[registration] = record

            cn = str(record.get("cn", "")).upper().strip()
            aircraft_model = str(record.get("aircraft_model", "")).upper().strip()

            if device_id:
                self._by_device_id[device_id] = record

            if registration:
                self._by_registration[registration] = record

            if cn:
                self._by_cn.setdefault(cn, []).append(record)

            if aircraft_model:
                self._by_aircraft_model.setdefault(
                    aircraft_model,
                    []
                ).append(record)

    def find_by_device_id(
        self,
        device_id: str,
    ) -> dict[str, Any] | None:
        self._ensure_loaded()

        return self._by_device_id.get(
            device_id.upper().strip()
        )


    def find_by_registration(
        self,
        registration: str,
    ) -> dict[str, Any] | None:
        self._ensure_loaded()

        return self._by_registration.get(
            self._normalize_registration(registration)
        )

    def find_by_cn(
        self,
        cn: str,
    ) -> list[dict[str, Any]]:
        self._ensure_loaded()

        return self._by_cn.get(
            cn.upper().strip(),
            [],
        )

    def find_by_aircraft_model(
        self,
        model: str,
    ) -> list[dict[str, Any]]:
        self._ensure_loaded()

        return self._by_aircraft_model.get(
            model.upper().strip(),
            [],
        )
    
    def _ensure_loaded(self) -> None:
        if self._records is None:
            self.load()

    def _normalize_registration(self, value: str) -> str:
        return (
            str(value or "")
            .upper()
            .replace("-", "")
            .replace(" ", "")
            .strip()
        )