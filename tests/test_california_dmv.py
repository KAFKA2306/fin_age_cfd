import json
from pathlib import Path


def load_json(path: str) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_california_dmv_permit_snapshot() -> None:
    payload = load_json("data/california-dmv-permits-2026-05-08.json")
    assert payload["publisher"] == "California Department of Motor Vehicles"
    assert str(payload["source_url"]).startswith("https://www.dmv.ca.gov/")

    categories = {item["permit_type"]: item for item in payload["permit_categories"]}
    assert set(categories) == {
        "testing_with_safety_driver",
        "driverless_testing",
        "deployment",
    }
    assert categories["testing_with_safety_driver"]["effective_at"] == "2026-05-08"
    assert len(categories["testing_with_safety_driver"]["holders"]) == 27
    assert categories["driverless_testing"]["effective_at"] == "2026-04-03"
    assert len(categories["driverless_testing"]["holders"]) == 6
    assert categories["deployment"]["effective_at"] == "2025-11-21"
    assert len(categories["deployment"]["holders"]) == 3


def test_california_dmv_testing_miles_preserve_qualifier() -> None:
    payload = load_json("data/california-dmv-testing.json")
    observations = payload["observations"]
    assert all(
        str(item["source_url"]).startswith("https://www.dmv.ca.gov/")
        for item in observations
    )

    latest = observations[-1]
    assert latest["period_start"] == "2024-12-01"
    assert latest["period_end"] == "2025-11-30"
    assert latest["metric"] == "public_road_testing_miles"
    assert latest["value"] == 9_000_000
    assert latest["qualifier"] == "greater_than"
    assert latest["unit"] == "miles"
