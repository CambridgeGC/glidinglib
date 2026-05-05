from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Optional


@dataclass
class GlidingAppAccount:
    id: Optional[int] = None
    uuid: str = ""

    is_active: bool = False
    email: str = ""
    name: str = ""
    first_name: str = ""
    last_name: str = ""

    date_updated: Optional[datetime] = None

    membership_type: str = ""
    membership_number: str = ""

    phone: str = ""
    groups: list[str] = field(default_factory=list)

    home_club: Any = None
    extra: dict[str, Any] = field(default_factory=dict)
    association: dict[str, Any] = field(default_factory=dict)

    address1: str = ""
    address2: str = ""
    postcode: str = ""
    city: str = ""
    country: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    date_of_birth: Optional[date] = None

    license_number: str = ""
    license_issue_date: Optional[date] = None
    aml_number: str = ""

    emergency_contact: str = ""
    emergency_contact_relation: str = ""
    emergency_contact_phone: str = ""

    bis_exam_date: Optional[date] = None
    bis_ati: Any = None

    fis_exam_date: Optional[date] = None
    fis_refresher_course_date: Optional[date] = None
    fis_refresher_course_newest_date: Optional[date] = None
    fis_training_flight_date: Optional[date] = None

    fes_refresher_date: Optional[date] = None

    medical_valid_from: Optional[date] = None
    medical_valid_to: Optional[date] = None
    medical_checked_at: Optional[datetime] = None
    medical_checked_by: str = ""
    medical_history: list[Any] = field(default_factory=list)

    unsubscribe_to_all_mail: bool = False
    deactivate_by_date: Optional[date] = None
    delete_by_date: Optional[date] = None
    charge_to_id: Optional[int] = None