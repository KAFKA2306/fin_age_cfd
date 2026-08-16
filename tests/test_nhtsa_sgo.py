from src.collect_nhtsa_sgo import discover_downloads


def test_discover_downloads_keeps_ads_and_level2_separate():
    html = b'''<html><body>
    <a href="/files/ads.csv">ADS Incident Report Data</a>
    <a href="/files/l2.csv">Level 2 ADAS Incident Report Data</a>
    <a href="/files/other.csv">Other Incident Report Data</a>
    </body></html>'''
    found = discover_downloads(html)
    assert set(found) == {"ads", "level_2_adas", "other"}
    assert found["ads"].endswith("/files/ads.csv")
    assert found["level_2_adas"].endswith("/files/l2.csv")
