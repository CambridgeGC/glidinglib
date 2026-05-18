from pathlib import Path
import os


def get_app_data_dir(app_name: str) -> Path:
    local_app_data = os.getenv("LOCALAPPDATA")

    if local_app_data:
        path = Path(local_app_data) / app_name
    else:
        path = Path.home() / f".{app_name.lower()}"

    path.mkdir(parents=True, exist_ok=True)

    return path