import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from glidinglib.services.glidingapp_account_service import GlidingAppAccountService


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[1] / "config.json"

    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def json_default(value: Any):
    if isinstance(value, (date, datetime)):
        return value.isoformat()

    if is_dataclass(value):
        return asdict(value)

    return str(value)


def dump(title: str, data: Any) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps(data, default=json_default, indent=2, ensure_ascii=False))


def main() -> None:
    config = load_config()

    service = GlidingAppAccountService(config)

    accounts = service.get_accounts()
    active_accounts = service.get_active_accounts()
    instructors = service.get_accounts_in_group("instructor")
    tow_pilots = service.get_accounts_in_group("tow pilot")

    print(f"Total accounts: {len(accounts)}")
    print(f"Active accounts: {len(active_accounts)}")
    print(f"Instructors: {len(instructors)}")
    print(f"Tow pilots: {len(tow_pilots)}")

    dump("First 5 accounts", accounts[:5])
    dump("Tow pilots", tow_pilots)


if __name__ == "__main__":
    main()