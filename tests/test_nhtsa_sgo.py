import json
from pathlib import Path

from collect_nhtsa_sgo import DOWNLOADS, csv_inventory, revision_id, write_revision


def sample_raw(report_id: str) -> bytes:
    return f"Report ID,Report Version\n{report_id},1\n".encode()


def sample_manifest(raw_files: dict[str, bytes], retrieved_at: str) -> dict[str, object]:
    datasets = [
        {
            "category": category,
            "filename": f"{category}.csv",
            "url": DOWNLOADS[category],
            **csv_inventory(raw_files[category]),
        }
        for category in DOWNLOADS
    ]
    return {
        "schema_version": 2,
        "publisher": "National Highway Traffic Safety Administration",
        "dataset": "Standing General Order incident reports",
        "first_retrieved_at": retrieved_at,
        "source_page": "https://www.nhtsa.gov/es/node/103486",
        "datasets": datasets,
        "revision_id": revision_id(datasets),
    }


def test_download_registry_keeps_ads_and_level2_separate():
    assert set(DOWNLOADS) == {"ads", "level_2_adas", "other"}
    assert DOWNLOADS["ads"].endswith("_ADS.csv")
    assert DOWNLOADS["level_2_adas"].endswith("_ADAS.csv")
    assert DOWNLOADS["other"].endswith("_OTHER.csv")


def test_csv_inventory_requires_real_rows():
    result = csv_inventory(b"Report ID,Report Version\n1,2\n")
    assert result["rows"] == 1
    assert result["columns"] == ["Report ID", "Report Version"]
    assert len(result["sha256"]) == 64


def test_revision_id_depends_on_source_bytes_not_retrieval_time():
    raw_files = {category: sample_raw(category) for category in DOWNLOADS}
    first = sample_manifest(raw_files, "2026-08-18T00:00:00+00:00")
    second = sample_manifest(raw_files, "2026-08-19T00:00:00+00:00")
    assert first["revision_id"] == second["revision_id"]

    changed = dict(raw_files)
    changed["ads"] = sample_raw("changed")
    third = sample_manifest(changed, "2026-08-19T00:00:00+00:00")
    assert first["revision_id"] != third["revision_id"]


def test_write_revision_is_immutable_for_same_source_revision(tmp_path: Path):
    raw_files = {category: sample_raw(category) for category in DOWNLOADS}
    first = sample_manifest(raw_files, "2026-08-18T00:00:00+00:00")
    path = write_revision(first, raw_files, tmp_path)
    original = path.read_text(encoding="utf-8")

    second = sample_manifest(raw_files, "2026-08-19T00:00:00+00:00")
    same_path = write_revision(second, raw_files, tmp_path)

    assert same_path == path
    assert path.read_text(encoding="utf-8") == original
    stored = json.loads(original)
    assert stored["first_retrieved_at"] == "2026-08-18T00:00:00+00:00"
    for category in DOWNLOADS:
        assert (path.parent / f"{category}.csv").read_bytes() == raw_files[category]
