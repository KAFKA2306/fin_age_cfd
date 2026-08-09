"""Portable runtime configuration for the Finage data client."""

from __future__ import annotations

import os
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(
    os.getenv("FINAGE_OUTPUT_DIR", REPOSITORY_ROOT / "output")
).expanduser().resolve()
LOG_DIR = Path(
    os.getenv("FINAGE_LOG_DIR", REPOSITORY_ROOT / ".runtime" / "logs")
).expanduser().resolve()
BASE_URL = os.getenv("FINAGE_BASE_URL", "https://api.finage.co.uk").rstrip("/")
API_KEY = os.getenv("FINAGE_API_KEY")

DATA_TYPES = ("stock", "forex", "crypto", "index", "combined_data")
TARGET_ASSETS = (
    {"type": "stock", "symbol": "AAPL"},
    {"type": "forex", "symbol": "GBPUSD"},
    {"type": "crypto", "symbol": "BTCUSD"},
    {"type": "index", "symbol": "^GSPC"},
)


def create_directories() -> None:
    """Create runtime output and log directories without relying on host-specific paths."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    for data_type in DATA_TYPES:
        if data_type != "combined_data":
            (OUTPUT_DIR / data_type).mkdir(parents=True, exist_ok=True)


def require_api_key() -> str:
    """Return the API key or fail closed with a remediation message."""
    if not API_KEY:
        raise RuntimeError(
            "FINAGE_API_KEY is not set. Set it only for the current shell "
            "or use a local secret manager."
        )
    return API_KEY
