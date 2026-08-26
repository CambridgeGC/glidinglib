import argparse
import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime, time
from pathlib import Path
from typing import Any

from glidinglib.services.glidingapp_account_service import GlidingAppAccountService


def load_config() -> dict:
    config_path = Path(__file__).resolve().parents[1] / "config.json"

    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def json_default(value: Any):
    if isinstance(value, (date, time, datetime)):
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
    parser = argparse.ArgumentParser(description="Fetch and display Gliding.App member recency")
    parser.add_argument(
        "user_id",
        nargs="?",
        type=int,
        default=71,
        help="Gliding.App user ID (default: 71)",
    )
    parser.add_argument(
        "--data-source",
        choices=["live", "test", "config"],
        default="config",
        help="Data source: live, test, or config",
    )

    args = parser.parse_args()
    config = load_config()

    service = GlidingAppAccountService(config)
    print(f"Fetching recency for user_id={args.user_id} (data_source={args.data_source})...")

    recency = service.get_user_recency(
        user_id=args.user_id,
        data_source=args.data_source,
    )

    dump(f"Gliding.App User Recency - User ID {args.user_id}", recency)


if __name__ == "__main__":
    main()
