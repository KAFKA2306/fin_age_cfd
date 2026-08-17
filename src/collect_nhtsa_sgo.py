#!/usr/bin/env python3
"""Snapshot NHTSA Standing General Order incident CSV revisions."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE_PAGE = "https://www.nhtsa.gov/es/node/103486"
DOWNLOADS = {
    "ads": "https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/SGO-2021-01_Incident_Reports_ADS.csv",
    "level_2_adas": (
        "https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/"
        "SGO-2021-01_Incident_Reports_ADAS.csv"
    ),
    "other": (
        "https://static.nhtsa.gov/odi/ffdd/sgo-2021-01/"
        "SGO-2021-01_Incident_Reports_OTHER.csv"
    ),
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


def revision_id(datasets: list[dict[str, object]]) -> str:
    identities = sorted(f"{item['category']}:{item['sha256']}" for item in datasets)
    return hashlib.sha256("\n".join(identities).encode()).hexdigest()


def collect_sources() -> tuple[dict[str, object], dict[str, bytes]]:
    raw_files: dict[str, bytes] = {}
    datasets: list[dict[str, object]] = []
    for category, url in DOWNLOADS.items():
        raw = fetch(url)
        raw_files[category] = raw
        datasets.append(
            {
                "category": category,
                "filename": f"{category}.csv",
                "url": url,
                **csv_inventory(raw),
            }
        )
    manifest: dict[str, object] = {
        "schema_version": 2,
        "publisher": "National Highway Traffic Safety Administration",
        "dataset": "Standing General Order incident reports",
        "first_retrieved_at": datetime.now(UTC).isoformat(),
        "source_page": SOURCE_PAGE,
        "datasets": datasets,
    }
    manifest["revision_id"] = revision_id(datasets)
    return manifest, raw_files


def collect() -> dict[str, object]:
    manifest, _ = collect_sources()
    return manifest


def write_manifest(manifest: dict[str, object], output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output


def write_revision(
    manifest: dict[str, object], raw_files: dict[str, bytes], revision_dir: Path
) -> Path:
    revision = str(manifest["revision_id"])
    target = revision_dir / revision
    manifest_path = target / "manifest.json"
    if manifest_path.exists():
        return manifest_path

    target.mkdir(parents=True, exist_ok=True)
    for category in DOWNLOADS:
        (target / f"{category}.csv").write_bytes(raw_files[category])
    write_manifest(manifest, manifest_path)
    return manifest_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--revision-dir", type=Path)
    args = parser.parse_args()

    manifest, raw_files = collect_sources()
    outputs: list[Path] = []
    if args.revision_dir:
        outputs.append(write_revision(manifest, raw_files, args.revision_dir))
    if args.output:
        outputs.append(write_manifest(manifest, args.output))
    if not outputs:
        outputs.append(write_manifest(manifest, Path("data/nhtsa/sgo-manifest.json")))

    print(f"indexed {len(manifest['datasets'])} NHTSA SGO datasets -> {', '.join(map(str, outputs))}")


if __name__ == "__main__":
    main()
