import json


DATA_PATH = "data/california-dmv-permits-2026-05-08.json"
SOURCE_URL = (
    "https://www.dmv.ca.gov/portal/vehicle-industry-services/autonomous-vehicles/"
    "autonomous-vehicle-testing-permit-holders/"
)


def test_california_dmv_permit_snapshot() -> None:
    with open(DATA_PATH, encoding="utf-8") as handle:
        payload = json.load(handle)

    assert payload["publisher"] == "California Department of Motor Vehicles"
    assert payload["source_url"] == SOURCE_URL

    categories = {item["permit_type"]: item for item in payload["permit_categories"]}
    assert set(categories) == {
        "testing_with_safety_driver",
        "driverless_testing",
        "deployment",
    }

    safety_driver = categories["testing_with_safety_driver"]
    assert safety_driver["effective_at"] == "2026-05-08"
    assert len(safety_driver["holders"]) == 27
    assert "TESLA ROBOTAXI LLC" in safety_driver["holders"]
    assert "WAYMO LLC" in safety_driver["holders"]

    driverless = categories["driverless_testing"]
    assert driverless["effective_at"] == "2026-04-03"
    assert len(driverless["holders"]) == 6
    assert "Waymo LLC" in driverless["holders"]
    assert "Zoox Inc." in driverless["holders"]

    deployment = categories["deployment"]
    assert deployment["effective_at"] == "2025-11-21"
    assert len(deployment["holders"]) == 3
    assert deployment["holders"] == [
        "Mercedes-Benz Research & Development North America",
        "Nuro Inc.",
        "Waymo LLC",
    ]
