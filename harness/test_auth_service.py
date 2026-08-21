import sys
from pathlib import Path

# Add src to sys.path for testing
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if SRC_DIR.exists() and str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import unittest
from unittest.mock import MagicMock

from glidinglib.auth.user_context import UserContext
from glidinglib.auth.auth_service import GlidingAppAuthService
from glidinglib.models.glidingapp_account_model import GlidingAppAccount


class TestGlidingAppAuthService(unittest.TestCase):
    def setUp(self):
        self.sample_config = {
            "permissions": {
                "roles": {
                    "admin": ["admin", "committee", "bestuur"],
                    "duty_officer": ["instructor", "launch director", "admin"]
                },
                "pages": {
                    "dashboard": ["*"],
                    "flight_editor": ["duty_officer"],
                    "ktrax_radar": ["*"],
                    "aerolog_upload": ["instructor", "admin"],
                    "admin_settings": ["admin"]
                },
                "capabilities": {
                    "can_view_logs": ["*"],
                    "can_edit_flights": ["duty_officer"],
                    "can_upload_aerolog": ["instructor", "admin"],
                    "can_modify_club_settings": ["admin"]
                }
            }
        }

    def test_unauthenticated_user(self):
        auth_service = GlidingAppAuthService(self.sample_config)
        ctx = auth_service.get_user_context(None)

        self.assertFalse(ctx.is_authenticated)
        self.assertFalse(ctx.is_active)
        self.assertFalse(ctx.has_group("admin"))
        self.assertFalse(ctx.can("can_view_logs"))
        self.assertFalse(ctx.can_access_page("dashboard"))
        self.assertEqual(ctx.allowed_pages, [])

    def test_glider_pilot_permissions(self):
        mock_account = GlidingAppAccount(
            id=101,
            email="pilot@cgc.org.uk",
            name="Peter Pilot",
            is_active=True,
            groups=["glider pilot"],
            raw_groups=["zweefvlieger"]
        )
        mock_account_service = MagicMock()
        mock_account_service.get_account_by_email.return_value = mock_account

        auth_service = GlidingAppAuthService(self.sample_config, account_service=mock_account_service)
        ctx = auth_service.get_user_context("pilot@cgc.org.uk")

        self.assertTrue(ctx.is_authenticated)
        self.assertTrue(ctx.is_active)
        self.assertTrue(ctx.has_group("glider pilot"))
        self.assertTrue(ctx.has_group("zweefvlieger"))
        self.assertFalse(ctx.has_group("instructor"))

        # Capabilities
        self.assertTrue(ctx.can("can_view_logs"))
        self.assertFalse(ctx.can("can_edit_flights"))
        self.assertFalse(ctx.can("can_upload_aerolog"))

        # Pages
        self.assertTrue(ctx.can_access_page("dashboard"))
        self.assertTrue(ctx.can_access_page("ktrax_radar"))
        self.assertFalse(ctx.can_access_page("flight_editor"))
        self.assertFalse(ctx.can_access_page("aerolog_upload"))

    def test_duty_officer_role_alias_permissions(self):
        # A launch director should gain 'duty_officer' access via role alias
        mock_account = GlidingAppAccount(
            id=102,
            email="director@cgc.org.uk",
            name="David Director",
            is_active=True,
            groups=["launch director"],
            raw_groups=["startleider"]
        )
        mock_account_service = MagicMock()
        mock_account_service.get_account_by_email.return_value = mock_account

        auth_service = GlidingAppAuthService(self.sample_config, account_service=mock_account_service)
        ctx = auth_service.get_user_context("director@cgc.org.uk")

        self.assertTrue(ctx.is_authenticated)
        self.assertTrue(ctx.can("can_edit_flights"))
        self.assertTrue(ctx.can_access_page("flight_editor"))
        self.assertFalse(ctx.can("can_upload_aerolog"))
        self.assertFalse(ctx.can_access_page("admin_settings"))

    def test_admin_permissions(self):
        mock_account = GlidingAppAccount(
            id=103,
            email="admin@cgc.org.uk",
            name="Alice Admin",
            is_active=True,
            groups=["admin"],
            raw_groups=["admin"]
        )
        mock_account_service = MagicMock()
        mock_account_service.get_account_by_email.return_value = mock_account

        auth_service = GlidingAppAuthService(self.sample_config, account_service=mock_account_service)
        ctx = auth_service.get_user_context("admin@cgc.org.uk")

        self.assertTrue(ctx.is_authenticated)
        self.assertTrue(ctx.can("can_edit_flights"))
        self.assertTrue(ctx.can("can_upload_aerolog"))
        self.assertTrue(ctx.can("can_modify_club_settings"))
        self.assertTrue(ctx.can_access_page("admin_settings"))

    def test_inactive_member_denied(self):
        mock_account = GlidingAppAccount(
            id=104,
            email="expired@cgc.org.uk",
            name="Inactive Member",
            is_active=False,
            groups=["admin"]
        )
        mock_account_service = MagicMock()
        mock_account_service.get_account_by_email.return_value = mock_account

        auth_service = GlidingAppAuthService(self.sample_config, account_service=mock_account_service)
        ctx = auth_service.get_user_context("expired@cgc.org.uk")

        self.assertFalse(ctx.is_active)
        self.assertFalse(ctx.can("can_view_logs"))
        self.assertFalse(ctx.can_access_page("dashboard"))

    def test_header_extraction(self):
        auth_service = GlidingAppAuthService(self.sample_config)
        headers = {
            "Host": "flightupdater.cgc.ruskin.me.uk",
            "Cf-Access-Authenticated-User-Email": "test@cgc.org.uk",
            "X-Origin-Secret": "secret"
        }
        email = auth_service.extract_email_from_headers(headers)
        self.assertEqual(email, "test@cgc.org.uk")


if __name__ == "__main__":
    unittest.main()
