# autonomous-vehicles

[![Quality](https://github.com/KAFKA2306/autonomous-vehicles/actions/workflows/quality.yml/badge.svg)](https://github.com/KAFKA2306/autonomous-vehicles/actions/workflows/quality.yml)
[![Government source check](https://github.com/KAFKA2306/autonomous-vehicles/actions/workflows/source-check.yml/badge.svg)](https://github.com/KAFKA2306/autonomous-vehicles/actions/workflows/source-check.yml)

Autonomous Vehicles の実運用拡大と事故・testing evidenceを、政府一次情報から再現可能に追跡します。

## 正準view

- Index: [`api/v1/autonomous-vehicles/index.json`](api/v1/autonomous-vehicles/index.json)
- NHTSA SGO: [`api/v1/autonomous-vehicles/nhtsa-sgo.json`](api/v1/autonomous-vehicles/nhtsa-sgo.json)
- California DMV: [`api/v1/autonomous-vehicles/california-dmv.json`](api/v1/autonomous-vehicles/california-dmv.json)

NHTSA viewはADS / Level 2 ADAS / Otherを分離し、Report IDごとに最新Report Versionだけをderived viewへ採用します。raw CSV revisionは別に保存するため、訂正履歴を失いません。Californiaのcrash時系列はNHTSA SGOの`state=CA`を別viewとして保持します。

California DMV viewはannual public-road testing miles、disengagement event、permit snapshotを保持します。company-levelの`testing_miles_per_disengagement`は、同じreport year・同じPermit Numberでmileage CSVのdisengagement数とevent CSVの行数が一致し、分母が0でない場合だけ生成します。これはtesting activityの運用指標であり、安全率・安全順位ではありません。

## Evidence

- NHTSA raw revisions: `data/nhtsa/sgo/revisions/<revision_id>/`
- California DMV raw revisions: `data/california/dmv/revisions/<revision_id>/`
- California statewide testing observations: [`data/california-dmv-testing.json`](data/california-dmv-testing.json)
- California permit snapshot: [`data/california-dmv-permits-2026-05-08.json`](data/california-dmv-permits-2026-05-08.json)

source bytesのSHA-256からrevision identityを作り、取得時刻だけが変わった場合は新しいraw revisionを作りません。

## 更新

```bash
python src/update_av_evidence.py
```

この1コマンドでNHTSA SGO、California DMVの取得可能なannual disengagement/mileage CSVを実取得し、raw revisionと正準viewを更新します。`Government source check` はPRでlive sourceを検証し、main push・週次実行ではsource bytesが変わった場合だけevidence/viewをcommitします。

## 一次情報

- NHTSA Standing General Order on Crash Reporting: https://www.nhtsa.gov/laws-regulations/standing-general-order-crash-reporting
- California DMV Autonomous Vehicles: https://www.dmv.ca.gov/portal/vehicle-industry-services/autonomous-vehicles/
- California DMV Permit Resources: https://www.dmv.ca.gov/portal/vehicle-industry-services/autonomous-vehicles/autonomous-vehicles-program-permit-resources/

2026年のCalifornia DMV reporting surfaceではVMT、dynamic-driving-task performance relevant system failures、vehicle immobilizations、braking events、collisions、noncompliance等が別templateとして定義されています。旧disengagement seriesと新制度metricsを同じ意味の系列として連結しません。

## データ上の制約

- NHTSA SGOのreport countは走行距離などのexposureで正規化されていません。分母なしのcompany safety rateを作りません。
- ADSとLevel 2 ADASを同じcategoryとして扱いません。
- NHTSAの`Same Incident ID`を保持し、report数とincident identityを区別します。
- California DMVのtestingとdeploymentを混同しません。旧annual disengagement reportingはtesting scopeです。
- 2025旧形式CSVのように公式URLで取得できないものを推測生成しません。
- sourceにない値・期間・単位を補間しません。
