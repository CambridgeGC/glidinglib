import unittest
from datetime import date
from unittest.mock import MagicMock

from glidinglib.models.glidingapp_recency_model import (
    GlidingAppUserRecency,
    GlidingAppRecencyDetail,
    LaunchMethodSummary,
)
from glidinglib.mappers.glidingapp_recency_mapper import (
    map_glidingapp_recency,
    map_glidingapp_recency_detail,
)
from glidinglib.services.glidingapp_account_service import GlidingAppAccountService


SAMPLE_RECENCY_JSON = {
    "user_id": 71,
    "currency": "groen",
    "starts": 50,
    "hours": 129,
    "student": 0,
    "student_hours": 0,
    "pic_hours": 691,
    "fis_total_hours": 468,
    "recency": {
        "fis": "valid",
        "lier": 30,
        "sleep": 114,
        "checks": 5,
        "is_fes": True,
        "starts": 144,
        "last_xc": "2026-08-23",
        "fis_uren": 6111,
        "tmg_uren": 1283,
        "tmg_check": 1,
        "vliegduur": 17647,
        "zelfstart": 45,
        "6m_methods": [
            {
                "starts": 37,
                "start_methode": "sleep"
            },
            {
                "starts": 13,
                "start_methode": "lier"
            }
        ],
        "fis_starts": 194,
        "tmg_starts": 45,
        "fes_refresher": "2023-01-31",
        "fis_date_exam": "",
        "is_instructor": True,
        "lier_valid_to": "2028-03-17",
        "sleep_valid_to": "2028-08-06",
        "checks_valid_to": "2028-06-30",
        "starts_valid_to": "2028-07-16",
        "fis_uren_valid_to": "2028-05-31",
        "tmg_uren_valid_to": "2027-11-18",
        "tmg_check_valid_to": "2026-12-31",
        "vliegduur_valid_to": "2028-08-09",
        "zelfstart_valid_to": "2027-12-20",
        "fis_starts_valid_to": "2028-08-18",
        "tmg_starts_valid_to": "2027-11-18",
        "fis_date_training_flight": "2022-06-08",
        "fis_date_refresher_course": "2026-03-07",
        "fes_date_refresher_valid_to": "2028-01-31",
        "fis_date_training_flight_valid_to": "2031-06-08",
        "fis_date_refresher_course_valid_to": "2029-03-07"
    }
}


class TestGlidingAppRecency(unittest.TestCase):
    def test_map_recency_sample(self):
        user_rec = map_glidingapp_recency(SAMPLE_RECENCY_JSON)

        self.assertEqual(user_rec.user_id, 71)
        self.assertEqual(user_rec.currency, "groen")
        self.assertEqual(user_rec.currency_status, "green")
        self.assertEqual(user_rec.starts, 50)
        self.assertEqual(user_rec.hours, 129)
        self.assertEqual(user_rec.student, 0)
        self.assertEqual(user_rec.student_hours, 0)
        self.assertEqual(user_rec.pic_hours, 691)
        self.assertEqual(user_rec.fis_total_hours, 468)

        rec = user_rec.recency
        self.assertEqual(rec.fis_status, "valid")
        self.assertTrue(rec.is_instructor)
        self.assertTrue(rec.is_fes)

        self.assertEqual(rec.starts, 144)
        self.assertEqual(rec.winch_starts, 30)
        self.assertEqual(rec.aerotow_starts, 114)
        self.assertEqual(rec.self_launch_starts, 45)
        self.assertEqual(rec.tmg_starts, 45)
        self.assertEqual(rec.fis_starts, 194)
        self.assertEqual(rec.checks_count, 5)
        self.assertEqual(rec.tmg_checks_count, 1)

        self.assertEqual(rec.flight_time_minutes, 17647)
        self.assertEqual(rec.fis_flight_time_minutes, 6111)
        self.assertEqual(rec.tmg_flight_time_minutes, 1283)

        self.assertEqual(len(rec.six_month_methods), 2)
        self.assertEqual(rec.six_month_methods[0].launch_method, "aerotow")
        self.assertEqual(rec.six_month_methods[0].raw_launch_method, "sleep")
        self.assertEqual(rec.six_month_methods[0].starts, 37)
        self.assertEqual(rec.six_month_methods[1].launch_method, "winch")
        self.assertEqual(rec.six_month_methods[1].raw_launch_method, "lier")
        self.assertEqual(rec.six_month_methods[1].starts, 13)

        self.assertEqual(rec.last_cross_country_date, date(2026, 8, 23))
        self.assertEqual(rec.fes_refresher_date, date(2023, 1, 31))
        self.assertIsNone(rec.fis_exam_date)
        self.assertEqual(rec.fis_training_flight_date, date(2022, 6, 8))
        self.assertEqual(rec.fis_refresher_course_date, date(2026, 3, 7))

        self.assertEqual(rec.winch_valid_to, date(2028, 3, 17))
        self.assertEqual(rec.aerotow_valid_to, date(2028, 8, 6))
        self.assertEqual(rec.self_launch_valid_to, date(2027, 12, 20))
        self.assertEqual(rec.starts_valid_to, date(2028, 7, 16))
        self.assertEqual(rec.checks_valid_to, date(2028, 6, 30))
        self.assertEqual(rec.flight_time_valid_to, date(2028, 8, 9))
        self.assertEqual(rec.tmg_starts_valid_to, date(2027, 11, 18))
        self.assertEqual(rec.tmg_flight_time_valid_to, date(2027, 11, 18))
        self.assertEqual(rec.tmg_check_valid_to, date(2026, 12, 31))
        self.assertEqual(rec.fis_starts_valid_to, date(2028, 8, 18))
        self.assertEqual(rec.fis_flight_time_valid_to, date(2028, 5, 31))
        self.assertEqual(rec.fes_refresher_valid_to, date(2028, 1, 31))
        self.assertEqual(rec.fis_training_flight_valid_to, date(2031, 6, 8))
        self.assertEqual(rec.fis_refresher_course_valid_to, date(2029, 3, 7))

    def test_map_recency_empty_payload(self):
        empty_rec = map_glidingapp_recency({})
        self.assertEqual(empty_rec.user_id, 0)
        self.assertEqual(empty_rec.currency, "")
        self.assertEqual(empty_rec.currency_status, "")
        self.assertEqual(empty_rec.recency.starts, 0)
        self.assertEqual(empty_rec.recency.six_month_methods, [])
        self.assertIsNone(empty_rec.recency.last_cross_country_date)

    def test_account_service_get_user_recency(self):
        mock_config = {
            "glidingapp": {
                "server": "https://fake.url",
                "api_key": "fake_key",
                "data_source": "live"
            }
        }
        service = GlidingAppAccountService(mock_config)
        service._client_for = MagicMock()
        mock_client = MagicMock()
        mock_client.fetch_user_recency.return_value = SAMPLE_RECENCY_JSON
        service._client_for.return_value = mock_client

        recency = service.get_user_recency(71)
        mock_client.fetch_user_recency.assert_called_once_with(71)
        self.assertEqual(recency.user_id, 71)
        self.assertEqual(recency.currency_status, "green")
        self.assertEqual(recency.recency.aerotow_starts, 114)


if __name__ == "__main__":
    unittest.main()
