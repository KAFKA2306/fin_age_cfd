from __future__ import annotations

import importlib
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
