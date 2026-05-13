import json
from pathlib import Path

from glidinglib.clients.aerolog_client import AerologClient


CONFIG_FILE = Path(__file__).parent.parent / "config.json"

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)


aerolog_config = config["aerolog"]

if aerolog_config["data_source"] == "test":
    base_url = aerolog_config["test_base_url"]
    email = aerolog_config["test_email"]
    password = aerolog_config["test_password"]
else:
    base_url = aerolog_config["base_url"]
    email = aerolog_config["email"]
    password = aerolog_config["password"]


client = AerologClient(
    base_url=base_url,
    email=email,
    password=password,
)

quals = client.get_members_tech_qualif(1184, 1184)

for q in quals:
    print(
        q.code,
        q.description,
        q.date_issued,
        q.date_expired,
    )