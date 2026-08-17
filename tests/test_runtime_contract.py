from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest


def reload_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("FINAGE_OUTPUT_DIR", str(tmp_path / "output"))
    monkeypatch.setenv("FINAGE_LOG_DIR", str(tmp_path / "logs"))
    import config

    return importlib.reload(config)


def test_paths_are_environment_driven(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config = reload_config(monkeypatch, tmp_path)
    config.create_directories()

    assert config.OUTPUT_DIR == (tmp_path / "output").resolve()
    assert config.LOG_DIR == (tmp_path / "logs").resolve()
    assert (config.OUTPUT_DIR / "stock").is_dir()
    assert not str(config.OUTPUT_DIR).startswith(("D:\\", "M:\\"))


def test_missing_api_key_fails_closed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("FINAGE_API_KEY", raising=False)
    config = reload_config(monkeypatch, tmp_path)

    with pytest.raises(RuntimeError, match="FINAGE_API_KEY is not set"):
        config.require_api_key()


def test_supported_endpoint_is_url_encoded(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    reload_config(monkeypatch, tmp_path)
    import main

    assert main.FinageEndpoints.last_price("index", "^GSPC").endswith("/%5EGSPC")


def test_unknown_asset_type_is_rejected(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    reload_config(monkeypatch, tmp_path)
    import main

    with pytest.raises(ValueError, match="Unsupported asset type"):
        main.FinageEndpoints.last_price("commodity", "XAUUSD")


def test_california_dmv_permit_snapshot() -> None:
    data_path = Path("data/california-dmv-permits-2026-05-08.json")
    payload = json.loads(data_path.read_text(encoding="utf-8"))

    assert payload["publisher"] == "California Department of Motor Vehicles"
    assert payload["source_url"].startswith("https://www.dmv.ca.gov/")

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
    assert deployment["holders"] == [
        "Mercedes-Benz Research & Development North America",
        "Nuro Inc.",
        "Waymo LLC",
    ]
