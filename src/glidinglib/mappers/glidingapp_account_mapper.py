from datetime import date, datetime
from typing import Any, Optional

from glidinglib.models.glidingapp_account_model import GlidingAppAccount


GROUP_TRANSLATION_MAP = {
    # Flying roles
    "zweefvlieger": "glider pilot",
    "sleepvlieger": "tow pilot",
    "gastvlieger": "guest pilot",
    "instructeur": "instructor",

    # Ground / launch roles
    "trekker": "retrieve driver",
    "startleider": "launch director",
    "lierist": "winch driver",
    "startwagen": "launch vehicle",

    # Qualifications / status
    "brevet": "licensed pilot",

    # Duty / ops roles


    # Admin / organisational
    "admin": "admin",
    "instructie_coordinator": "instruction coordinator",
    "bestuur": "committee",
    "leden_admin": "membership admin",
    "projectmanager": "project manager",
    "rooster_maker": "roster maker",

    # Technical
    "technicus_vliegend": "aircraft technician",
    "technicus_rollend": "ground equipment technician",

    # Misc / leave as-is if unknown
    # (anything not in this map will pass through unchanged)
}


def _parse_datetime(value: Any) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _parse_date(value: Any) -> Optional[date]:
    if not value:
        return None
    return date.fromisoformat(str(value)[:10])


def _translate_group(group: str) -> str:
    return GROUP_TRANSLATION_MAP.get(group, group)


def map_glidingapp_account(api_row: dict[str, Any]) -> GlidingAppAccount:
    data = api_row.get("data") or {}

    groups = [
        _translate_group(str(group))
        for group in api_row.get("groups") or []
    ]

    return GlidingAppAccount(
        id=api_row.get("id"),
        uuid=str(api_row.get("uuid") or ""),

        is_active=bool(api_row.get("is_active", False)),
        email=str(api_row.get("email") or ""),
        name=str(api_row.get("name") or ""),
        first_name=str(api_row.get("first_name") or ""),
        last_name=str(api_row.get("last_name") or ""),

        date_updated=_parse_datetime(api_row.get("date_updated")),

        membership_type=str(api_row.get("lidmaatschap") or ""),
        membership_number=str(api_row.get("lid_nummer") or ""),

        phone=str(api_row.get("phone") or ""),
        groups=groups,

        home_club=api_row.get("home_club"),
        extra=api_row.get("extra") or {},
        association=api_row.get("association") or {},

        address1=str(data.get("address1") or ""),
        address2=str(data.get("address2") or ""),
        postcode=str(data.get("zipcode") or ""),
        city=str(data.get("city") or ""),
        country=str(data.get("country") or ""),
        latitude=data.get("lat"),
        longitude=data.get("lon"),

        date_of_birth=_parse_date(data.get("date_of_birth")),

        license_number=str(data.get("license_number") or ""),
        license_issue_date=_parse_date(data.get("license_issue_date")),
        aml_number=str(data.get("aml_nummer") or ""),

        emergency_contact=str(data.get("emergency_contact") or ""),
        emergency_contact_relation=str(data.get("emergency_contact_relation") or ""),
        emergency_contact_phone=str(data.get("emergency_contact_phone") or ""),

        bis_exam_date=_parse_date(data.get("bis_date_exam")),
        bis_ati=data.get("bis_ati"),

        fis_exam_date=_parse_date(data.get("fis_date_exam")),
        fis_refresher_course_date=_parse_date(data.get("fis_date_refresher_course")),
        fis_refresher_course_newest_date=_parse_date(
            data.get("fis_date_refresher_course_newest")
        ),
        fis_training_flight_date=_parse_date(data.get("fis_date_training_flight")),

        fes_refresher_date=_parse_date(data.get("fes_refresher")),

        medical_valid_from=_parse_date(data.get("medical_valid_from")),
        medical_valid_to=_parse_date(data.get("medical_valid_to")),
        medical_checked_at=_parse_datetime(data.get("medical_checked_at")),
        medical_checked_by=str(data.get("medical_checked_by") or ""),
        medical_history=data.get("medical_history") or [],

        unsubscribe_to_all_mail=bool(api_row.get("unsubscribe_to_all_mail", False)),
        deactivate_by_date=_parse_date(api_row.get("deactivate_by_date")),
        delete_by_date=_parse_date(api_row.get("delete_by_date")),
        charge_to_id=api_row.get("charge_to_id"),
    )