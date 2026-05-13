from datetime import datetime
from typing import Any, Optional

from glidinglib.models.aerolog_tech_qualification import AerologTechQualification


def _parse_datetime(value: Any) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def map_aerolog_tech_qualification(row: dict) -> AerologTechQualification:
    return AerologTechQualification(
        account=row.get("_account"),
        name=row.get("_name", "") or "",
        code=row.get("code", "") or "",
        description=row.get("desc", "") or "",
        date_issued=_parse_datetime(row.get("dateIssued")),
        date_expired=_parse_datetime(row.get("dateExpired")),
    )