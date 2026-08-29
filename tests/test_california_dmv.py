import json
from pathlib import Path


def load_json(path: str) -> dict[str, object]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_california_dmv_permit_snapshot() -> None:
    payload = load_json("data/california-dmv-permits.json")
    assert payload["publisher"] == "California Department of Motor Vehicles"
    assert str(payload["source_url"]).startswith("https://www.dmv.ca.gov/")

    categories = {item["permit_type"]: item for item in payload["permit_categories"]}
    assert set(categories) == {
        "testing_with_safety_driver",
        "driverless_testing",
        "deployment",
    }
    drivered = categories["testing_with_safety_driver"]
    assert drivered["effective_at"] == "2026-08-12"
    assert len(drivered["holders"]) == 28
    assert "KODIAK AI" in drivered["holders"]
    assert "WeRide AI" in drivered["holders"]
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

    boundaries = payload["reporting_regime_boundaries"]
    assert len(boundaries) == 1
    boundary = boundaries[0]
    assert boundary["effective_date"] == "2026-04-28"
    assert boundary["reporting_operative_delay_days"] == 120
    assert boundary["reporting_operative_date"] == "2026-08-26"
    assert "disengagement reporting removed" in boundary["change"]
    assert "dynamic driving task performance relevant system failures" in boundary["change"]
    assert "vehicle immobilizations" in boundary["change"]
    assert str(boundary["source_url"]).startswith("https://www.dmv.ca.gov/")
    assert str(boundary["adopted_regulatory_text_url"]).startswith(
        "https://www.dmv.ca.gov/"
    )
    assert str(boundary["final_statement_of_reasons_url"]).startswith(
        "https://www.dmv.ca.gov/"
    )
