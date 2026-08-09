"""Inspect generated parquet files without notebook-only dependencies."""

from __future__ import annotations

import pandas as pd

import config


def display_parquet_files() -> None:
    found = False
    for data_type in config.DATA_TYPES:
        data_type_dir = config.OUTPUT_DIR / data_type
        for file_path in sorted(data_type_dir.glob("*.parquet")):
            found = True
            print(f"ファイル: {file_path}")
            try:
                frame = pd.read_parquet(file_path)
                print(frame.to_string())
            except (OSError, ValueError) as exc:
                print(f"エラー: {file_path} の読み込みに失敗しました: {exc}")

    if not found:
        print("parquetファイルが見つかりませんでした。")


if __name__ == "__main__":
    display_parquet_files()
