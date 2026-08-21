import time
from typing import Iterable, Literal, Optional

from glidinglib.clients.glidingapp_client import GlidingAppClient
from glidinglib.mappers.glidingapp_account_mapper import map_glidingapp_account
from glidinglib.models.glidingapp_account_model import GlidingAppAccount


DataSource = Literal["live", "test", "config"]


class GlidingAppAccountService:
    def __init__(
        self,
        config: dict,
        default_data_source: DataSource = "config",
        timeout: int = 30,
        cache_ttl_seconds: int = 300,
    ):
        self.config = config
        self.default_data_source = default_data_source
        self.timeout = timeout
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: dict[str, tuple[float, list[GlidingAppAccount]]] = {}

    def _resolve_data_source(self, data_source: DataSource | None = None) -> str:
        selected = data_source or self.default_data_source

        if selected == "config":
            selected = self.config.get("glidingapp", {}).get("data_source", "live")

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
        ga_config = self.config.get("glidingapp", {})
        selected = self._resolve_data_source(data_source)

        if selected == "live":
            base_url = ga_config.get("server", "")
            api_key = ga_config.get("api_key", "")
        else:
            base_url = ga_config.get("test_server", "")
            api_key = ga_config.get("test_api_key", "")

        return GlidingAppClient(
            base_url=base_url,
            api_key=api_key,
            timeout=self.timeout,
        )

    def clear_cache(self, data_source: DataSource | None = None) -> None:
        if data_source:
            ds = self._resolve_data_source(data_source)
            self._cache.pop(ds, None)
        else:
            self._cache.clear()

    def get_accounts(
        self,
        data_source: DataSource | None = None,
        force_refresh: bool = False,
    ) -> list[GlidingAppAccount]:
        ds = self._resolve_data_source(data_source)
        now = time.time()

        if not force_refresh and ds in self._cache:
            cached_time, cached_accounts = self._cache[ds]
            if (now - cached_time) < self.cache_ttl_seconds:
                return cached_accounts

        client = self._client_for(ds)
        raw_rows = client.fetch_accounts()

        accounts = [
            map_glidingapp_account(row)
            for row in raw_rows or []
        ]
        self._cache[ds] = (now, accounts)
        return accounts

    def get_active_accounts(
        self,
        data_source: DataSource | None = None,
        force_refresh: bool = False,
    ) -> list[GlidingAppAccount]:
        return [
            account
            for account in self.get_accounts(data_source, force_refresh=force_refresh)
            if account.is_active
        ]

    def get_accounts_in_group(
        self,
        group: str,
        data_source: DataSource | None = None,
        force_refresh: bool = False,
    ) -> list[GlidingAppAccount]:
        group_key = group.strip().lower()

        return [
            account
            for account in self.get_accounts(data_source, force_refresh=force_refresh)
            if group_key in {g.lower() for g in account.groups}
            or group_key in {g.lower() for g in getattr(account, "raw_groups", [])}
        ]

    def get_account_by_email(
        self,
        email: str,
        data_source: DataSource | None = None,
        force_refresh: bool = False,
    ) -> Optional[GlidingAppAccount]:
        if not email or not email.strip():
            return None

        clean_email = email.strip().lower()
        for account in self.get_active_accounts(data_source, force_refresh=force_refresh):
            if account.email and account.email.strip().lower() == clean_email:
                return account
        return None