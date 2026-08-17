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


def test_california_dmv_testing_history() -> None:
    payload = load_json("data/california-dmv-testing.json")
    observations = payload["observations"]
    assert all(
        str(item["source_url"]).startswith("https://www.dmv.ca.gov/")
        for item in observations
    )

    totals = [item for item in observations if item["metric"] == "public_road_testing_miles"]
    assert [(item["period_start"], item["period_end"], item["value"]) for item in totals] == [
        ("2022-12-01", "2023-11-30", 9_068_861),
        ("2023-12-01", "2024-11-30", 4_498_066),
        ("2024-12-01", "2025-11-30", 9_000_000),
    ]

    latest = totals[-1]
    assert latest["qualifier"] == "greater_than"
    assert latest["unit"] == "miles"

    first_period = [item for item in observations if item["period_start"] == "2022-12-01"]
    metrics = {item["metric"]: item["value"] for item in first_period}
    assert metrics == {
        "public_road_testing_miles": 9_068_861,
        "safety_driver_testing_miles": 5_801_069,
        "driverless_testing_miles": 3_267_792,
    }
