from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AerologTechQualification:
    account: int | None = None
    name: str = ""
    code: str = ""
    description: str = ""
    date_issued: datetime | None = None
    date_expired: datetime | None = None