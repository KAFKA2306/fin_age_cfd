#!/usr/bin/env python3
"""Discover and snapshot NHTSA Standing General Order incident CSVs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

PAGE = "https://www.nhtsa.gov/es/node/103486"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.href: str | None = None
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() == "a":
            self.href = dict(attrs).get("href")
            self.text = []

    def handle_data(self, data: str) -> None:
        if self.href is not None:
            self.text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self.href is not None:
            self.links.append((" ".join(" ".join(self.text).split()), self.href))
            self.href = None
            self.text = []


def fetch(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "autonomous-vehicles/1.0 github.com/KAFKA2306/autonomous-vehicles"})
    with urlopen(req, timeout=60) as response:
        return response.read()


def classify(label: str) -> str | None:
    lowered = label.lower()
    if "level 2 adas" in lowered:
        return "level_2_adas"
    if "ads incident" in lowered:
        return "ads"
    if "other incident" in lowered:
        return "other"
    return None


def discover_downloads(page_html: bytes) -> dict[str, str]:
    parser = LinkParser()
    parser.feed(page_html.decode("utf-8", errors="replace"))
    found: dict[str, str] = {}
    for label, href in parser.links:
        category = classify(label)
        if category and ("csv" in href.lower() or "download" in href.lower()):
            found[category] = urljoin(PAGE, href)
    missing = {"ads", "level_2_adas", "other"} - found.keys()
    if missing:
        raise ValueError(f"NHTSA SGO download links missing: {sorted(missing)}")
    return found


def csv_inventory(raw: bytes) -> dict[str, object]:
    text = raw.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    columns = [str(name or "").strip() for name in (reader.fieldnames or [])]
    rows = sum(1 for _ in reader)
    if not columns or rows == 0:
        raise ValueError("downloaded NHTSA CSV is empty")
    return {"columns": columns, "rows": rows, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def collect() -> dict[str, object]:
    page_raw = fetch(PAGE)
    downloads = discover_downloads(page_raw)
    datasets = []
    for category, url in sorted(downloads.items()):
        raw = fetch(url)
        datasets.append({"category": category, "url": url, **csv_inventory(raw)})
    return {
        "schema_version": 1,
        "publisher": "National Highway Traffic Safety Administration",
        "dataset": "Standing General Order incident reports",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source_page": PAGE,
        "source_page_sha256": hashlib.sha256(page_raw).hexdigest(),
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
