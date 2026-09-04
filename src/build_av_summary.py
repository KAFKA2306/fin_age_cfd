#!/usr/bin/env python3
"""Build a compact AV summary without copying incident or company ledgers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = ROOT / "api" / "v1" / "autonomous-vehicles"


def dump(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def category_summary(category: dict) -> dict:
    monthly = category.get("monthly_report_counts_2024_plus") or {}
    return {
        "latest_report_count": category["latest_report_count"],
        "report_count_2024_plus": sum(int(value) for value in monthly.values()),
        "reporting_entity_count_2024_plus": len(
            category.get("reporting_entity_counts_2024_plus") or {}
        ),
        "california_report_count_2024_plus": category[
            "california_report_count_2024_plus"
        ],
        "california_distinct_same_incident_id_count_2024_plus": category[
            "california_distinct_same_incident_id_count_2024_plus"
        ],
    }


def latest_statewide_testing_miles(dmv: dict) -> dict:
    observations = [
        item
        for item in dmv.get("statewide_testing_observations") or []
        if item.get("metric") == "public_road_testing_miles"
    ]
    if not observations:
        raise ValueError("California DMV output has no statewide public-road testing miles")
    latest = max(
        observations,
        key=lambda item: (str(item.get("period_end") or ""), str(item.get("period_start") or "")),
    )
    result = {
        "period": {
            "start": latest["period_start"],
            "end": latest["period_end"],
        },
        "value": latest["value"],
        "unit": latest["unit"],
        "scope": latest["scope"],
        "source_url": latest["source_url"],
    }
    if latest.get("qualifier"):
        result["qualifier"] = latest["qualifier"]
    return result


def current_permit_summary(dmv: dict) -> dict:
    snapshot = dmv.get("permit_snapshot") or {}
    categories = snapshot.get("permit_categories") or []
    if not categories:
        raise ValueError("California DMV output has no current permit snapshot")
    result: dict[str, dict] = {}
    for category in categories:
        permit_type = str(category.get("permit_type") or "")
        if not permit_type:
            raise ValueError("California DMV permit category has no permit_type")
        holders = category.get("holders")
        if not isinstance(holders, list):
            raise ValueError(f"California DMV permit category {permit_type} has no holders list")
        result[permit_type] = {
            "effective_at": category["effective_at"],
            "holder_count": len(holders),
        }
    return {
        "retrieved_at": snapshot["retrieved_at"],
        "source_url": snapshot["source_url"],
        "categories": result,
    }


def build(root: Path) -> dict:
    nhtsa = load(root / "nhtsa-sgo.json")
    dmv = load(root / "california-dmv.json")

    reports = dmv.get("company_testing_reports") or {}
    if not reports:
        raise ValueError("California DMV output has no company testing reports")
    latest_year = max(reports, key=int)
    latest = reports[latest_year]
    companies = latest.get("companies") or []
    if not companies:
        raise ValueError(f"California DMV {latest_year} report has no companies")

    miles = round(
        sum(float(company.get("autonomous_testing_miles") or 0) for company in companies),
        3,
    )
    disengagements = sum(
        int(company.get("reported_disengagements") or 0) for company in companies
    )

    return {
        "schema_version": 1,
        "nhtsa_sgo": {
            "publisher": nhtsa["publisher"],
            "source_page": nhtsa["source_page"],
            "source_revision_id": nhtsa["source_revision_id"],
            "ads": category_summary(nhtsa["categories"]["ads"]),
            "level_2_adas": category_summary(nhtsa["categories"]["level_2_adas"]),
            "comparison_warning": nhtsa["comparison_warning"],
        },
        "california_dmv": {
            "publisher": dmv["publisher"],
            "source_revision_id": dmv["source_revision_id"],
            "latest_report_year": int(latest_year),
            "period": latest["period"],
            "company_permit_group_count": len(companies),
            "autonomous_testing_miles": miles,
            "reported_disengagements": disengagements,
            "metric_warning": latest["metric_warning"],
            "source_urls": sorted(
                source["url"] for source in latest.get("sources", {}).values()
            ),
            "latest_statewide_public_road_testing_miles": latest_statewide_testing_miles(
                dmv
            ),
            "current_permit_snapshot": current_permit_summary(dmv),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    summary = build(args.root)
    output = args.root / "summary.json"
    output.write_bytes(dump(summary))
    print(
        json.dumps(
            {
                "ads_reports": summary["nhtsa_sgo"]["ads"]["latest_report_count"],
                "level_2_adas_reports": summary["nhtsa_sgo"]["level_2_adas"][
                    "latest_report_count"
                ],
                "dmv_report_year": summary["california_dmv"]["latest_report_year"],
                "dmv_testing_miles": summary["california_dmv"][
                    "autonomous_testing_miles"
                ],
                "dmv_latest_statewide_testing_miles": summary["california_dmv"][
                    "latest_statewide_public_road_testing_miles"
                ]["value"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
