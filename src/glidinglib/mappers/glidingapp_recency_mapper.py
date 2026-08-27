from datetime import date
from typing import Any, Optional

from glidinglib.models.glidingapp_recency_model import (
    GlidingAppRecencyDetail,
    GlidingAppUserRecency,
    LaunchMethodSummary,
)

CURRENCY_TRANSLATION_MAP = {
    "groen": "green",
    "oranje": "amber",
    "geel": "amber",
    "yellow": "amber",
    "rood": "red",
    "blauw": "blue",
    "grijs": "grey",
    "nvt": "n/k",
    "n.v.t.": "n/k",
}

LAUNCH_METHOD_MAP = {
    "lier": "winch",
    "sleep": "aerotow",
    "zelf": "self-launch",
    "zelfstart": "self-launch",
    "tmg": "tmg",
    "tmg-a": "tmg-aerotow",
    "sep": "sep",
    "sep-a": "sep-aerotow",
    "car": "car",
    "bungee": "bungee",
    "overig": "other",
}


def _parse_date(value: Any) -> Optional[date]:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except (ValueError, TypeError):
        return None


def _to_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def map_glidingapp_recency_detail(raw_rec: dict[str, Any]) -> GlidingAppRecencyDetail:
    if not isinstance(raw_rec, dict):
        return GlidingAppRecencyDetail()

    raw_methods = raw_rec.get("6m_methods") or []
    six_month_methods: list[LaunchMethodSummary] = []
    if isinstance(raw_methods, list):
        for item in raw_methods:
            if isinstance(item, dict):
                raw_m = str(item.get("start_methode") or "").strip().lower()
                six_month_methods.append(
                    LaunchMethodSummary(
                        raw_launch_method=raw_m,
                        launch_method=LAUNCH_METHOD_MAP.get(raw_m, raw_m),
                        starts=_to_int(item.get("starts")),
                    )
                )

    return GlidingAppRecencyDetail(
        fis_status=str(raw_rec.get("fis") or ""),
        is_instructor=bool(raw_rec.get("is_instructor", False)),
        is_fes=bool(raw_rec.get("is_fes", False)),
        tmg_exemption=str(raw_rec.get("tmg_excemption") or raw_rec.get("tmg_exemption") or "").strip().lower(),

        starts=_to_int(raw_rec.get("starts")),
        winch_starts=_to_int(raw_rec.get("lier")),
        aerotow_starts=_to_int(raw_rec.get("sleep")),
        self_launch_starts=_to_int(raw_rec.get("zelfstart")),
        tmg_starts=_to_int(raw_rec.get("tmg_starts")),
        fis_starts=_to_int(raw_rec.get("fis_starts")),
        checks_count=_to_int(raw_rec.get("checks")),
        tmg_checks_count=_to_int(raw_rec.get("tmg_check")),

        flight_time_minutes=_to_int(raw_rec.get("vliegduur")),
        fis_flight_time_minutes=_to_int(raw_rec.get("fis_uren")),
        tmg_flight_time_minutes=_to_int(raw_rec.get("tmg_uren")),

        six_month_methods=six_month_methods,

        last_cross_country_date=_parse_date(raw_rec.get("last_xc")),
        fes_refresher_date=_parse_date(raw_rec.get("fes_refresher")),
        fis_exam_date=_parse_date(raw_rec.get("fis_date_exam")),
        fis_training_flight_date=_parse_date(raw_rec.get("fis_date_training_flight")),
        fis_refresher_course_date=_parse_date(raw_rec.get("fis_date_refresher_course")),

        winch_valid_to=_parse_date(raw_rec.get("lier_valid_to")),
        aerotow_valid_to=_parse_date(raw_rec.get("sleep_valid_to")),
        self_launch_valid_to=_parse_date(raw_rec.get("zelfstart_valid_to")),
        starts_valid_to=_parse_date(raw_rec.get("starts_valid_to")),
        checks_valid_to=_parse_date(raw_rec.get("checks_valid_to")),
        flight_time_valid_to=_parse_date(raw_rec.get("vliegduur_valid_to")),
        tmg_starts_valid_to=_parse_date(raw_rec.get("tmg_starts_valid_to")),
        tmg_flight_time_valid_to=_parse_date(raw_rec.get("tmg_uren_valid_to")),
        tmg_check_valid_to=_parse_date(raw_rec.get("tmg_check_valid_to")),
        fis_starts_valid_to=_parse_date(raw_rec.get("fis_starts_valid_to")),
        fis_flight_time_valid_to=_parse_date(raw_rec.get("fis_uren_valid_to")),
        fes_refresher_valid_to=_parse_date(raw_rec.get("fes_date_refresher_valid_to")),
        fis_training_flight_valid_to=_parse_date(raw_rec.get("fis_date_training_flight_valid_to")),
        fis_refresher_course_valid_to=_parse_date(raw_rec.get("fis_date_refresher_course_valid_to")),
        raw=raw_rec,
    )


def map_glidingapp_recency(api_row: dict[str, Any]) -> GlidingAppUserRecency:
    if not isinstance(api_row, dict):
        return GlidingAppUserRecency()

    raw_currency = str(api_row.get("currency") or "").strip().lower()
    recency_detail = map_glidingapp_recency_detail(api_row.get("recency") or {})

    return GlidingAppUserRecency(
        user_id=_to_int(api_row.get("user_id")),
        currency=raw_currency,
        currency_status=CURRENCY_TRANSLATION_MAP.get(raw_currency, raw_currency),
        starts=_to_int(api_row.get("starts")),
        hours=_to_int(api_row.get("hours")),
        student=_to_int(api_row.get("student")),
        student_hours=_to_int(api_row.get("student_hours")),
        pic_hours=_to_int(api_row.get("pic_hours")),
        fis_total_hours=_to_int(api_row.get("fis_total_hours")),
        recency=recency_detail,
        raw=api_row,
    )
