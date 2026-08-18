import csv
import io

from update_av_evidence import dmv_company_view, latest_nhtsa_reports, month_period


def csv_bytes(headers: list[str], rows: list[list[object]]) -> bytes:
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    return out.getvalue().encode()


def test_dmv_ratio_requires_matching_same_source_counts():
    event_headers = [
        "Manufacturer",
        "Permit Number",
        "DATE",
        "VEHICLE IS CAPABLE OF OPERATING WITHOUT A DRIVER\n(Yes or No)",
        "DRIVER PRESENT\n(Yes or No)",
        "DISENGAGEMENT INITIATED BY\n"
        "(AV System, Test Driver, Remote Operator, or Passenger)",
        "DISENGAGEMENT\nLOCATION\n"
        "(Interstate, Freeway, Highway, Rural Road, Street, or Parking Facility)",
        "DESCRIPTION OF FACTS CAUSING DISENGAGEMENT",
    ]
    events = csv_bytes(
        event_headers,
        [
            ["Example", "AVT001", "01/01/2024", "No", "Yes", "Test Driver", "Street", "a"],
            ["Example", "AVT001", "01/02/2024", "No", "Yes", "AV System", "Street", "b"],
        ],
    )
    mileage = csv_bytes(
        [
            "Manufacturer",
            "Permit Number",
            "VIN NUMBER",
            "Annual Total of Disengagements",
            "ANNUAL TOTAL",
        ],
        [["Example", "AVT001", "VIN1", "2", "1,000"]],
    )
    view = dmv_company_view(2024, events, mileage)
    company = view["companies"][0]
    assert company["source_count_match"] is True
    assert company["testing_miles_per_disengagement"] == 500.0
    assert "not a safety rate" in view["metric_warning"]


def test_dmv_ratio_is_null_when_event_and_mileage_counts_disagree():
    event_headers = [
        "Manufacturer",
        "Permit Number",
        "DATE",
        "VEHICLE IS CAPABLE OF OPERATING WITHOUT A DRIVER\n(Yes or No)",
        "DRIVER PRESENT\n(Yes or No)",
        "DISENGAGEMENT INITIATED BY\n"
        "(AV System, Test Driver, Remote Operator, or Passenger)",
        "DISENGAGEMENT\nLOCATION\n"
        "(Interstate, Freeway, Highway, Rural Road, Street, or Parking Facility)",
        "DESCRIPTION OF FACTS CAUSING DISENGAGEMENT",
    ]
    events = csv_bytes(
        event_headers,
        [["Example", "AVT001", "01/01/2024", "No", "Yes", "Test Driver", "Street", "a"]],
    )
    mileage = csv_bytes(
        [
            "Manufacturer",
            "Permit Number",
            "VIN NUMBER",
            "Annual Total of Disengagements",
            "ANNUAL TOTAL",
        ],
        [["Example", "AVT001", "VIN1", "2", "1,000"]],
    )
    company = dmv_company_view(2024, events, mileage)["companies"][0]
    assert company["source_count_match"] is False
    assert company["testing_miles_per_disengagement"] is None


def test_nhtsa_keeps_ads_and_level2_callers_separate_and_latest_version_only():
    raw = csv_bytes(
        [
            "Report ID",
            "Report Version",
            "Reporting Entity",
            "Incident Date",
            "Automation System Engaged?",
            "Engagement Status",
            "Same Incident ID",
            "State",
        ],
        [
            ["R1", "1", "Example", "JAN-2024", "ADS", "Verified Engaged", "I1", "CA"],
            ["R1", "2", "Example", "FEB-2024", "ADS", "Verified Engaged", "I1", "CA"],
        ],
    )
    records = latest_nhtsa_reports("ads", raw, "a" * 64)
    assert len(records) == 1
    assert records[0]["category"] == "ads"
    assert records[0]["report_version"] == 2
    assert records[0]["incident_month"] == "2024-02"


def test_nhtsa_month_parser_does_not_invent_unknown_dates():
    assert month_period("JUN-2026") == "2026-06"
    assert month_period("") is None
    assert month_period("[REDACTED]") is None
