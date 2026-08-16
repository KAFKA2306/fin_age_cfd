from collect_nhtsa_sgo import DOWNLOADS, csv_inventory


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
