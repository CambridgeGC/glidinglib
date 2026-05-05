from typing import Iterable, Literal

from glidinglib.clients.glidingapp_account_client import GlidingAppAccountClient
from glidinglib.mappers.glidingapp_account_mapper import map_glidingapp_account
from glidinglib.models.glidingapp_account_model import GlidingAppAccount


DataSource = Literal["live", "test", "config"]


class GlidingAppAccountService:
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
            selected = self.config["glidingapp"].get("data_source", "live")

        if selected not in ("live", "test"):
            raise ValueError(
                f"Invalid GlidingApp data source: {selected!r}. "
                "Expected 'live', 'test', or 'config'."
            )

        return selected

    def _client_for(
        self,
        data_source: DataSource | None = None,
    ) -> GlidingAppAccountClient:
        ga_config = self.config["glidingapp"]
        selected = self._resolve_data_source(data_source)

        if selected == "live":
            base_url = ga_config["server"]
            api_key = ga_config["api_key"]
        else:
            base_url = ga_config["test_server"]
            api_key = ga_config["test_api_key"]

        return GlidingAppAccountClient(
            base_url=base_url,
            api_key=api_key,
            timeout=self.timeout,
        )

    def get_accounts(
        self,
        data_source: DataSource | None = None,
    ) -> list[GlidingAppAccount]:
        client = self._client_for(data_source)
        raw_rows = client.fetch_accounts()

        return [
            map_glidingapp_account(row)
            for row in raw_rows or []
        ]

    def get_active_accounts(
        self,
        data_source: DataSource | None = None,
    ) -> list[GlidingAppAccount]:
        return [
            account
            for account in self.get_accounts(data_source)
            if account.is_active
        ]

    def get_accounts_in_group(
        self,
        group: str,
        data_source: DataSource | None = None,
    ) -> list[GlidingAppAccount]:
        group_key = group.strip().lower()

        return [
            account
            for account in self.get_accounts(data_source)
            if group_key in {g.lower() for g in account.groups}
        ]