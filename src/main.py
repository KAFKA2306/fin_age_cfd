"""Minimal Finage latest-price client."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any
from urllib.parse import quote

import pandas as pd
import requests

import config

LOGGER = logging.getLogger(__name__)


class FinageEndpoints:
    BASE_URL = config.BASE_URL

    @staticmethod
    def last_price(asset_type: str, symbol: str) -> str:
        endpoint_map = {
            "stock": f"/last/stock/{quote(symbol, safe='')}",
            "forex": f"/last/forex/{quote(symbol, safe='')}",
            "crypto": f"/last/crypto/{quote(symbol, safe='')}",
            "index": f"/last/stock-index/{quote(symbol, safe='')}",
        }
        try:
            endpoint = endpoint_map[asset_type]
        except KeyError as exc:
            raise ValueError(f"Unsupported asset type: {asset_type}") from exc
        return f"{FinageEndpoints.BASE_URL}{endpoint}"


def configure_logging() -> None:
    config.create_directories()
    logging.basicConfig(
        filename=config.LOG_DIR / "api_errors.log",
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def get_last_price(
    asset_type: str,
    symbol: str,
    *,
    timeout_seconds: float = 20.0,
) -> dict[str, Any]:
    api_key = config.require_api_key()
    url = FinageEndpoints.last_price(asset_type, symbol)
    try:
        response = requests.get(
            url,
            params={"apikey": api_key},
            headers={"X-API-Version": "2025Q2"},
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Finage response must be a JSON object")
        return payload
    except (requests.RequestException, ValueError) as exc:
        LOGGER.exception("Latest-price request failed for %s %s", asset_type, symbol)
        raise RuntimeError(f"Latest-price request failed for {asset_type} {symbol}") from exc


def save_data_to_parquet(df: pd.DataFrame, asset_type: str, filename: str) -> Path:
    output_path = config.OUTPUT_DIR / asset_type / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path)
    return output_path


def save_data_to_json(data: dict[str, Any], asset_type: str, filename: str) -> Path:
    output_path = config.OUTPUT_DIR / asset_type / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def main() -> int:
    configure_logging()
    for asset in config.TARGET_ASSETS:
        payload = get_last_price(asset["type"], asset["symbol"])
        print(f"{asset['type']} {asset['symbol']}: {json.dumps(payload, ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
