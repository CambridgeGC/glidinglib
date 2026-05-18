from glidinglib.clients.ogn_ddb_client import OgnDdbClient


def main() -> None:
    client = OgnDdbClient(
        app_name="FlightUpdater",
        timeout=10,
    )

    print("Loading OGN DDB...")
    records = client.load(force_refresh=True)

    print(f"Records loaded: {len(records)}")
    print(f"Cache file: {client.cache_path}")
    print(f"Cache exists: {client.cache_path.exists()}")

    if records:
        print("\nFirst record:")
        for key, value in records[0].items():
            print(f"  {key}: {value}")

    print("\nLookup by registration: G-CLON")

    record = client.find_by_registration("G-CLON")

    if record:
        for key, value in record.items():
            print(f"  {key}: {value}")
    else:
        print("  Not found")

    print("\nLookup by CN: 28")

    records_28 = client.find_by_cn("28")

    print(f"Matches: {len(records_28)}")

    for i, record in enumerate(records_28[:10], start=1):
        registration = record.get("registration", "")
        model = record.get("aircraft_model", "")
        device_id = record.get("device_id", "")

        print(
            f"  {i}: "
            f"{registration} | "
            f"{model} | "
            f"{device_id}"
        )

    print("\nTesting cache fallback...")

    offline_client = OgnDdbClient(
        app_name="FlightUpdater",
        url="http://127.0.0.1:9/not-available",
        timeout=2,
    )

    cached_records = offline_client.load(force_refresh=True)

    print(f"Cached records loaded: {len(cached_records)}")
    print(f"Cache file used: {offline_client.cache_path}")

    if len(cached_records) == len(records):
        print("Cache fallback OK")
    else:
        print("Cache fallback returned different record count")


if __name__ == "__main__":
    main()