from typing import Any, Mapping, Optional

from glidinglib.models.glidingapp_account_model import GlidingAppAccount
from glidinglib.services.glidingapp_account_service import DataSource, GlidingAppAccountService
from glidinglib.auth.user_context import UserContext


class GlidingAppAuthService:
    """
    Authorization and user context service evaluating GlidingApp accounts against
    group-based permissions configured in config.json.
    """

    def __init__(
        self,
        config: dict,
        account_service: Optional[GlidingAppAccountService] = None,
    ):
        self.config = config
        self.account_service = account_service or GlidingAppAccountService(config)

    @property
    def permissions_config(self) -> dict[str, Any]:
        return self.config.get("permissions", {})

    @property
    def pages_config(self) -> dict[str, Any]:
        return self.permissions_config.get("pages", {})

    @property
    def capabilities_config(self) -> dict[str, Any]:
        return self.permissions_config.get("capabilities", {})

    @property
    def roles_config(self) -> dict[str, Any]:
        """Optional role alias bundles, e.g. 'duty_officer': ['instructor', 'launch director', 'admin']"""
        return self.permissions_config.get("roles", {})

    def _expand_groups(self, groups_list: list[Any], visited: Optional[set[str]] = None) -> set[str]:
        """Recursively expands role aliases from permissions.roles into individual groups."""
        if visited is None:
            visited = set()

        expanded: set[str] = set()
        roles = self.roles_config

        for item in groups_list:
            clean = str(item).strip().lower()
            if not clean:
                continue

            expanded.add(clean)

            if clean in roles and clean not in visited:
                visited.add(clean)
                alias_targets = roles[clean]
                if isinstance(alias_targets, (list, tuple, set)):
                    expanded.update(self._expand_groups(list(alias_targets), visited=visited))

        return expanded

    def evaluate_permissions(
        self,
        user_groups: list[str],
        raw_user_groups: Optional[list[str]] = None,
        is_authenticated: bool = False,
    ) -> tuple[dict[str, bool], list[str]]:
        """
        Evaluates capabilities and allowed pages for a given set of groups based on config.json.
        """
        if not is_authenticated:
            return {}, []

        all_user_groups = {g.strip().lower() for g in (user_groups + (raw_user_groups or []))}

        # 1. Evaluate capabilities
        capabilities_result: dict[str, bool] = {}
        for cap_name, allowed_groups in self.capabilities_config.items():
            if not isinstance(allowed_groups, (list, tuple, set)):
                allowed_groups = [str(allowed_groups)]
            expanded_allowed = self._expand_groups(list(allowed_groups))
            if "*" in expanded_allowed or any(g in all_user_groups for g in expanded_allowed):
                capabilities_result[cap_name] = True
            else:
                capabilities_result[cap_name] = False

        # 2. Evaluate allowed pages
        allowed_pages: list[str] = []
        for page_name, allowed_groups in self.pages_config.items():
            if not isinstance(allowed_groups, (list, tuple, set)):
                allowed_groups = [str(allowed_groups)]
            expanded_allowed = self._expand_groups(list(allowed_groups))
            if "*" in expanded_allowed or any(g in all_user_groups for g in expanded_allowed):
                allowed_pages.append(page_name)

        return capabilities_result, allowed_pages

    def get_user_context(
        self,
        email: Optional[str],
        data_source: DataSource | None = None,
        force_refresh: bool = False,
    ) -> UserContext:
        """
        Looks up a club member by email and computes their UserContext and permissions.
        """
        if not email or not email.strip():
            return UserContext(
                email="",
                is_authenticated=False,
                is_active=False,
            )

        account = self.account_service.get_account_by_email(
            email.strip(),
            data_source=data_source,
            force_refresh=force_refresh,
        )

        if not account or not account.is_active:
            return UserContext(
                email=email.strip().lower(),
                is_authenticated=bool(account),
                is_active=bool(account and account.is_active),
                account=account,
            )

        capabilities, allowed_pages = self.evaluate_permissions(
            user_groups=account.groups,
            raw_user_groups=getattr(account, "raw_groups", []),
            is_authenticated=True,
        )

        return UserContext(
            email=account.email.strip().lower(),
            name=account.name or f"{account.first_name} {account.last_name}".strip(),
            is_authenticated=True,
            is_active=account.is_active,
            membership_number=account.membership_number,
            membership_type=account.membership_type,
            groups=account.groups,
            raw_groups=getattr(account, "raw_groups", []),
            account=account,
            capabilities=capabilities,
            allowed_pages=allowed_pages,
        )

    def extract_email_from_headers(self, headers: Mapping[str, str]) -> str:
        """
        Extracts user email from HTTP headers (supports Cloudflare Access, reverse proxies, etc.).
        """
        candidates = [
            "Cf-Access-Authenticated-User-Email",
            "cf-access-authenticated-user-email",
            "X-User-Email",
            "x-user-email",
            "X-Forwarded-Email",
            "x-forwarded-email",
        ]
        for key in candidates:
            val = headers.get(key)
            if val and val.strip():
                return val.strip().lower()
        return ""
