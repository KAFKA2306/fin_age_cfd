import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "build_av_summary.py"
SPEC = importlib.util.spec_from_file_location("build_av_summary", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AvSummaryTest(unittest.TestCase):
    def test_summary_keeps_categories_and_same_period_dmv_totals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "nhtsa-sgo.json").write_text(
                json.dumps(
                    {
                        "publisher": "NHTSA",
                        "source_page": "https://www.nhtsa.gov/example",
                        "source_revision_id": "abc",
                        "comparison_warning": "not exposure normalized",
                        "categories": {
                            "ads": {
                                "latest_report_count": 100,
                                "monthly_report_counts_2024_plus": {
                                    "2024-01": 10,
                                    "2024-02": 20,
                                },
                                "reporting_entity_counts_2024_plus": {
                                    "A": 10,
                                    "B": 20,
                                },
                                "california_report_count_2024_plus": 12,
                                "california_distinct_same_incident_id_count_2024_plus": 11,
                                "records": [{"report_id": "x"}],
                            },
                            "level_2_adas": {
                                "latest_report_count": 200,
                                "monthly_report_counts_2024_plus": {"2024-01": 30},
                                "reporting_entity_counts_2024_plus": {"C": 30},
                                "california_report_count_2024_plus": 4,
                                "california_distinct_same_incident_id_count_2024_plus": 4,
                                "records": [{"report_id": "y"}],
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )
            (root / "california-dmv.json").write_text(
                json.dumps(
                    {
                        "publisher": "California DMV",
                        "source_revision_id": "def",
                        "company_testing_reports": {
                            "2024": {
                                "period": {
                                    "start": "2023-12-01",
                                    "end": "2024-11-30",
                                },
                                "metric_warning": "testing metric, not safety rate",
                                "sources": {
                                    "mileage": {"url": "https://dmv.example/miles.csv"},
                                    "vehicle-disengagement": {
                                        "url": "https://dmv.example/disengagements.csv"
                                    },
                                },
                                "companies": [
                                    {
                                        "autonomous_testing_miles": 100.5,
                                        "reported_disengagements": 2,
                                    },
                                    {
                                        "autonomous_testing_miles": 200,
                                        "reported_disengagements": 3,
                                    },
                                ],
                            }
                        },
                        "statewide_testing_observations": [],
                        "permit_snapshot": {},
                    }
                ),
                encoding="utf-8",
            )

            summary = MODULE.build(root)

        self.assertEqual(summary["nhtsa_sgo"]["ads"]["report_count_2024_plus"], 30)
        self.assertEqual(
            summary["nhtsa_sgo"]["level_2_adas"]["latest_report_count"], 200
        )
        self.assertEqual(summary["california_dmv"]["autonomous_testing_miles"], 300.5)
        self.assertEqual(summary["california_dmv"]["reported_disengagements"], 5)
        self.assertNotIn("records", summary["nhtsa_sgo"]["ads"])
        self.assertNotIn("companies", summary["california_dmv"])


if __name__ == "__main__":
    unittest.main()
