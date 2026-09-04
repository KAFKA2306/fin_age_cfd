import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "build_av_summary.py"
SPEC = importlib.util.spec_from_file_location("build_av_summary_reporting", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReportingRegimeSummaryTest(unittest.TestCase):
    def test_projects_current_dmv_reporting_boundary_without_inventing_public_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "california-dmv-testing.json"
            path.write_text(
                json.dumps(
                    {
                        "reporting_regime_boundaries": [
                            {
                                "effective_date": "2026-04-28",
                                "reporting_operative_date": "2026-08-26",
                                "reporting_requirements": {
                                    "industry_memo": "AVIM 2026-001A",
                                    "industry_memo_url": "https://dmv.example/avim.pdf",
                                    "report_format": "csv",
                                    "monthly_reporting_start": "2026-08-26",
                                    "first_quarterly_report_due": "2026-09-30",
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            result = MODULE.current_reporting_regime(path)

        self.assertEqual(result["effective_date"], "2026-04-28")
        self.assertEqual(result["reporting_operative_date"], "2026-08-26")
        self.assertEqual(result["monthly_reporting_start"], "2026-08-26")
        self.assertEqual(result["first_quarterly_report_due"], "2026-09-30")
        self.assertEqual(result["industry_memo"], "AVIM 2026-001A")
        self.assertEqual(result["report_format"], "csv")
        self.assertIn("UNVERIFIED", result["availability_warning"])
        self.assertNotIn("value", result)

    def test_requires_reporting_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "california-dmv-testing.json"
            path.write_text(
                json.dumps({"reporting_regime_boundaries": []}), encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "no reporting regime boundary"):
                MODULE.current_reporting_regime(path)


if __name__ == "__main__":
    unittest.main()
