#!/usr/bin/env python3
"""Snapshot NHTSA Standing General Order incident CSVs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE_PAGE = "https://www.nhtsa.gov/es/node/103486"
DOWNLOADS = {
    "ads": "https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/SGO-2021-01_Incident_Reports_ADS.csv",
    "level_2_adas": "https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/SGO-2021-01_Incident_Reports_ADAS.csv",
    "other": "https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/SGO-2021-01_Incident_Reports_OTHER.csv",
}


def fetch(url: str) -> bytes:
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 autonomous-vehicles/1.0",
            "Accept": "text/csv,*/*;q=0.8",
        },
    )
    with urlopen(req, timeout=60) as response:
        return response.read()


def csv_inventory(raw: bytes) -> dict[str, object]:
    text = raw.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    columns = [str(name or "").strip() for name in (reader.fieldnames or [])]
    rows = sum(1 for _ in reader)
    if not columns or rows == 0:
        raise ValueError("downloaded NHTSA CSV is empty")
    return {
        "columns": columns,
        "rows": rows,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def collect() -> dict[str, object]:
    datasets = []
    for category, url in DOWNLOADS.items():
        raw = fetch(url)
        datasets.append({"category": category, "url": url, **csv_inventory(raw)})
    return {
        "schema_version": 1,
        "publisher": "National Highway Traffic Safety Administration",
        "dataset": "Standing General Order incident reports",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source_page": SOURCE_PAGE,
        "datasets": datasets,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/nhtsa/sgo-manifest.json"))
    args = parser.parse_args()
    result = collect()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"indexed {len(result['datasets'])} NHTSA SGO datasets -> {args.output}")


if __name__ == "__main__":
    main()
