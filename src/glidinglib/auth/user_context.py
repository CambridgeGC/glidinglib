from dataclasses import dataclass, field
from typing import Any, Optional

from glidinglib.models.glidingapp_account_model import GlidingAppAccount


@dataclass
class UserContext:
    email: str = ""
    name: str = ""
    is_authenticated: bool = False
    is_active: bool = False
    membership_number: str = ""
    membership_type: str = ""
    groups: list[str] = field(default_factory=list)
    raw_groups: list[str] = field(default_factory=list)
    account: Optional[GlidingAppAccount] = None
    capabilities: dict[str, bool] = field(default_factory=dict)
    allowed_pages: list[str] = field(default_factory=list)

    def has_group(self, *groups: str) -> bool:
        """
        Check if user belongs to at least one of the specified groups.
        Matches against both translated English groups and raw GlidingApp groups.
        Supports '*' for all authenticated active members.
        """
        if not self.is_authenticated or not self.is_active:
            return False
        user_groups = {g.lower().strip() for g in (self.groups + self.raw_groups)}
        for g in groups:
            target = str(g).lower().strip()
            if target == "*" or target in user_groups:
                return True
        return False

    def has_all_groups(self, *groups: str) -> bool:
        """Check if user belongs to ALL of the specified groups."""
        if not self.is_authenticated or not self.is_active:
            return False
        user_groups = {g.lower().strip() for g in (self.groups + self.raw_groups)}
        for g in groups:
            target = str(g).lower().strip()
            if target != "*" and target not in user_groups:
                return False
        return True

    def can(self, capability: str) -> bool:
        """Check if user is granted a specific capability configured in config.json."""
        if not self.is_authenticated or not self.is_active:
            return False
        return bool(self.capabilities.get(capability, False))

    def can_access_page(self, page_name: str) -> bool:
        """Check if user is allowed to access a specific page configured in config.json."""
        if not self.is_authenticated or not self.is_active:
            return False
        return page_name in self.allowed_pages

    def to_dict(self) -> dict[str, Any]:
        """Convert to a JSON-serializable dictionary for /api/user or /api/auth/me endpoints."""
        return {
            "authenticated": self.is_authenticated,
            "active": self.is_active,
            "email": self.email,
            "name": self.name,
            "membership_number": self.membership_number,
            "membership_type": self.membership_type,
            "groups": self.groups,
            "capabilities": self.capabilities,
            "allowed_pages": self.allowed_pages,
        }
