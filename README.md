# autonomous-vehicles

[![Quality](https://github.com/KAFKA2306/autonomous-vehicles/actions/workflows/quality.yml/badge.svg)](https://github.com/KAFKA2306/autonomous-vehicles/actions/workflows/quality.yml)
[![NHTSA source check](https://github.com/KAFKA2306/autonomous-vehicles/actions/workflows/source-check.yml/badge.svg)](https://github.com/KAFKA2306/autonomous-vehicles/actions/workflows/source-check.yml)

Autonomous Vehicles の実運用拡大と安全情報を、政府一次情報から再現可能に追跡するリポジトリです。

旧 `fin_age_cfd` のCFD価格取得実験は正準責務ではありません。現在は NHTSA と California DMV の公開情報だけを扱います。

## 一次情報

- NHTSA Standing General Order on Crash Reporting: https://www.nhtsa.gov/laws-regulations/standing-general-order-crash-reporting
- California DMV Autonomous Vehicles: https://www.dmv.ca.gov/portal/vehicle-industry-services/autonomous-vehicles/

## 現在のデータ

- `data/california-dmv-permits-2026-05-08.json`
  - safety-driver testing / driverless testing / deployment のpermit holder snapshot
- `data/california-dmv-testing.json`
  - California DMVが公表したpublic-road testing miles
  - `more than 9 million` のような公表上の不等号条件は `qualifier` として保持し、正確な値を推測しません
- NHTSA SGO revision snapshot
  - ADS / Level 2 ADAS / Other の公開CSVを取得
  - source SHA-256から決定的なrevision IDを生成
  - sourceが変化した場合だけ `data/nhtsa/sgo/revisions/<revision_id>/` にraw CSVとmanifestを追加

## NHTSA source snapshot

現在の公開CSVを検証するだけの場合:

```bash
python src/collect_nhtsa_sgo.py --output /tmp/sgo-manifest.json
```

raw CSVをrevision historyとして保存する場合:

```bash
python src/collect_nhtsa_sgo.py --revision-dir data/nhtsa/sgo/revisions
```

同じ3ファイルの内容が変わらなければ同じrevision IDになるため、取得時刻だけを理由に新しいsnapshotは作りません。

## 自動検証

- `Quality`
  - Ruff
  - pytest
  - tracked runtime artifact / unsafe host configuration の監査
- `NHTSA source check`
  - pull requestでは現在のNHTSA CSVを実取得して検証
  - 定期実行ではsource revisionが変化した場合だけraw CSVとmanifestをcommit

## データ上の制約

- NHTSAのincident countは走行距離などのexposureで正規化されていないため、分母がない状態で会社間の安全率を作りません。
- ADSとLevel 2 ADASを同じcategoryとして扱いません。
- testing milesとcommercial service milesを混同しません。
- sourceにない値や不明な期間・単位を補間しません。

## 未完了

Issue #5 の残件です。

- California DMV annual disengagement seriesの再構築
- company-level normalization
- 2024年以降の比較可能な時系列
- 分母が確認できる場合だけ行うsafety comparison

https://github.com/KAFKA2306/autonomous-vehicles/issues/5
