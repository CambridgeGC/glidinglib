from dataclasses import dataclass, field
from datetime import date
from typing import Any, Optional


@dataclass
class LaunchMethodSummary:
    launch_method: str = ""
    raw_launch_method: str = ""
    starts: int = 0


@dataclass
class GlidingAppRecencyDetail:
    # Status / flags
    fis_status: str = ""
    is_instructor: bool = False
    is_fes: bool = False
    tmg_exemption: str = ""

    # Launch totals
    starts: int = 0
    winch_starts: int = 0
    aerotow_starts: int = 0
    self_launch_starts: int = 0
    tmg_starts: int = 0
    fis_starts: int = 0
    checks_count: int = 0
    tmg_checks_count: int = 0

    # Flight times (in minutes)
    flight_time_minutes: int = 0
    fis_flight_time_minutes: int = 0
    tmg_flight_time_minutes: int = 0

    # 6-month launch breakdown
    six_month_methods: list[LaunchMethodSummary] = field(default_factory=list)

    # Dates
    last_cross_country_date: Optional[date] = None
    fes_refresher_date: Optional[date] = None
    fis_exam_date: Optional[date] = None
    fis_training_flight_date: Optional[date] = None
    fis_refresher_course_date: Optional[date] = None

    # Validity Expiries
    winch_valid_to: Optional[date] = None
    aerotow_valid_to: Optional[date] = None
    self_launch_valid_to: Optional[date] = None
    starts_valid_to: Optional[date] = None
    checks_valid_to: Optional[date] = None
    flight_time_valid_to: Optional[date] = None
    tmg_starts_valid_to: Optional[date] = None
    tmg_flight_time_valid_to: Optional[date] = None
    tmg_check_valid_to: Optional[date] = None
    fis_starts_valid_to: Optional[date] = None
    fis_flight_time_valid_to: Optional[date] = None
    fes_refresher_valid_to: Optional[date] = None
    fis_training_flight_valid_to: Optional[date] = None
    fis_refresher_course_valid_to: Optional[date] = None

    # Raw payload data
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class GlidingAppUserRecency:
    user_id: int = 0
    currency: str = ""
    currency_status: str = ""
    starts: int = 0
    hours: int = 0
    student: int = 0
    student_hours: int = 0
    pic_hours: int = 0
    fis_total_hours: int = 0
    recency: GlidingAppRecencyDetail = field(default_factory=GlidingAppRecencyDetail)
    raw: dict[str, Any] = field(default_factory=dict)
