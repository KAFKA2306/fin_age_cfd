## Windows 10 環境変数設定

**一時的な設定:**

```cmd
set FINAGE_API_KEY=YOUR_API_KEY
```

**恒久的な設定:**

```cmd
setx FINAGE_API_KEY "YOUR_API_KEY" /M
```

## プロジェクト構造と実装

**1. プロジェクトディレクトリ構造:**

```
E:/e/d/
├── src/
│   ├── config.py
│   ├── utils.py
│   ├── data_saver.py
│   └── main.py
└── output/
    ├── etf/
    ├── index/
    └── commodity/
```

**2. `src/config.py`:**

```python
import os

BASE_DIR = r"E:/e/d"
SRC_DIR = os.path.join(BASE_DIR, "src")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

API_KEY = os.getenv("FINAGE_API_KEY")

if not API_KEY:
    print("警告: 環境変数 'FINAGE_API_KEY' が設定されていません。")

DATA_TYPES = ["etf", "index", "commodity"]
```

**3. `src/utils.py`:**

```python
import os
from . import config

def create_directories():
    os.makedirs(config.SRC_DIR, exist_ok=True)
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    print(f"Base directories checked/created:\nSRC_DIR: {config.SRC_DIR}\nOUTPUT_DIR: {config.OUTPUT_DIR}")

    for data_type in config.DATA_TYPES:
        subdir_path = os.path.join(config.OUTPUT_DIR, data_type)
        os.makedirs(subdir_path, exist_ok=True)
        print(f"Subdirectory checked/created: {subdir_path}")

def get_output_path(data_type, filename):
    if data_type not in config.DATA_TYPES:
        raise ValueError(f"未定義のデータタイプです: {data_type}")
    subdir_path = os.path.join(config.OUTPUT_DIR, data_type)
    return os.path.join(subdir_path, filename)
```

**4. `src/data_saver.py`:**

```python
import os
import pandas as pd
import json
from . import utils

def save_data_to_csv(data, data_type, filename):
    try:
        output_path = utils.get_output_path(data_type, filename)

        if isinstance(data, pd.DataFrame):
            data.to_csv(output_path, index=False)
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
            df.to_csv(output_path, index=False)
        else:
             with open(output_path, 'w', encoding='utf-8') as f:
                f.write(str(data))

        print(f"データが正常に保存されました: {output_path}")

    except ValueError as ve:
        print(f"エラー: {ve}")
    except Exception as e:
        print(f"CSVデータ保存中にエラーが発生しました ({filename}): {e}")

def save_data_to_json(data, data_type, filename):
    try:
        output_path = utils.get_output_path(data_type, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"データが正常にJSON形式で保存されました: {output_path}")
    except ValueError as ve:
        print(f"エラー: {ve}")
    except Exception as e:
        print(f"JSONデータ保存中にエラーが発生しました ({filename}): {e}")
```

**5. `src/main.py`:**

```python
import os
import pandas as pd
from datetime import datetime
from . import config
from . import utils
from . import data_saver
# from .finage_client import get_historical_data, get_last_price # 実際のAPIクライアントをインポート

def run_data_pipeline():
    print("データパイプラインを開始します...")

    if not config.API_KEY:
        print("エラー: APIキーが設定されていません。環境変数 'FINAGE_API_KEY' を確認してください。")
        return

    utils.create_directories()

    print("\nデータの取得を開始します...")
    # --- 実際のデータ取得ロジックをここに実装 ---
    # 例: etf_data_hist = get_historical_data("etf", "QQQ", config.API_KEY, "start_date", "end_date")
    #     etf_data_last = get_last_price("etf", "QQQ", config.API_KEY)

    # ダミーデータ例
    etf_symbol = "QQQ"
    etf_data_hist = [
        {'date': '2024-01-01', 'o': 400, 'h': 405, 'l': 399, 'c': 404, 'v': 100000},
        {'date': '2024-01-02', 'o': 404, 'h': 408, 'l': 403, 'c': 407, 'v': 120000}
    ]
    etf_data_last = {'symbol': etf_symbol, 'price': 407.5, 'timestamp': datetime.now().isoformat()}

    index_symbol = "SPX"
    index_data_hist = [
        {'date': '2024-01-01', 'o': 4800, 'h': 4820, 'l': 4790, 'c': 4815},
        {'date': '2024-01-02', 'o': 4815, 'h': 4830, 'l': 4810, 'c': 4825}
    ]
    index_data_last = {'symbol': index_symbol, 'price': 4825.1, 'timestamp': datetime.now().isoformat()}

    commodity_symbol = "XAUUSD"
    commodity_data_hist = [
        {'date': '2024-01-01', 'o': 2050, 'h': 2060, 'l': 2045, 'c': 2058},
        {'date': '2024-01-02', 'o': 2058, 'h': 2065, 'l': 2055, 'c': 2062}
    ]
    commodity_data_last = {'symbol': commodity_symbol, 'price': 2062.5, 'timestamp': datetime.now().isoformat()}
    # --- ここまでダミーデータ ---

    print("データの取得が完了しました。")

    print("\nデータの保存を開始します...")
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    if etf_data_hist:
        data_saver.save_data_to_csv(etf_data_hist, "etf", f"{etf_symbol}_hist_{now_str}.csv")
    if etf_data_last:
        data_saver.save_data_to_json(etf_data_last, "etf", f"{etf_symbol}_last_{now_str}.json")

    if index_data_hist:
        data_saver.save_data_to_csv(index_data_hist, "index", f"{index_symbol}_hist_{now_str}.csv")
    if index_data_last:
        data_saver.save_data_to_json(index_data_last, "index", f"{index_symbol}_last_{now_str}.json")

    if commodity_data_hist:
        data_saver.save_data_to_csv(commodity_data_hist, "commodity", f"{commodity_symbol}_hist_{now_str}.csv")
    if commodity_data_last:
        data_saver.save_data_to_json(commodity_data_last, "commodity", f"{commodity_symbol}_last_{now_str}.json")

    print("\nデータの保存が完了しました。")
    print("データパイプラインが正常に終了しました。")

if __name__ == "__main__":
    run_data_pipeline()
```

**実行方法:**

1.  上記コードを各ファイルに保存します。
2.  環境変数 `FINAGE_API_KEY` を設定します。
3.  コマンドプロンプトで `E:/e/d` に移動し、以下を実行します。

    ```bash
    python -m src.main
    ```

---
Perplexity の Eliot より: pplx.ai/share





# Finage APIを用いた金融データ取得パイプラインの最適化とエラー解決策

## 要約
本報告書では、Finage APIを利用した金融データ取得パイプラインにおいて発生するHTTP 401/404エラーの根本原因と体系的解決策を分析する。APIエンドポイントの構造変化[1][2]、認証メカニズム[12]、時系列データ取得のベストプラクティス[14]に基づき、技術的課題を解決する実践的アプローチを提示する。

## 技術的課題の構造分析

### 認証関連エラー（401 Unauthorized）

2. **時刻同期問題**
   - サーバー時刻の最大許容誤差（±1分）超過[12]
   - JST→UTC変換の不備

```python
# 時刻同期検証コード例
from datetime import datetime, timezone
import ntplib

def validate_time_sync():
    try:
        ntp_time = ntplib.NTPClient().request('pool.ntp.org').tx_time
        local_time = datetime.now(timezone.utc).timestamp()
        return abs(ntp_time - local_time)  str:
    encoded = urllib.parse.quote(symbol, safe='')
    return encoded.replace('^', '%5E')
```

## システム最適化戦略

### エンドポイント管理モジュール
```python
class FinageEndpoints:
    BASE_URL = "https://api.finage.co.uk"
    
    @staticmethod
    def historical_data(asset_type: str) -> str:
        endpoints = {
            "stock": "/agg/stock/equity/",
            "forex": "/agg/forex/pair/",
            "crypto": "/agg/crypto/pair/",
            "index": "/agg/index/global/"
        }
        return f"{FinageEndpoints.BASE_URL}{endpoints[asset_type]}"
```

### 認証ヘッダー処理
```python
def get_auth_headers() -> dict:
    return {
        "Authorization": f"Bearer {os.getenv('FINAGE_API_KEY')}",
        "X-API-Version": "2025Q2"
    }
```

## データ取得プロセスの再設計

### 時系列データ取得フロー
1. シンボル正規化
2. タイムゾーン変換（JST → UTC）

```python
def fetch_historical_data(asset_type: str, symbol: str, days: int):
    endpoint = FinageEndpoints.historical_data(asset_type)
    params = {
        "from": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
        "to": datetime.now().strftime("%Y-%m-%d"),
        "adjustments": "split_dividends"
    }
    
    response = requests.get(
        f"{endpoint}{normalize_symbol(symbol)}/1/day",
        headers=get_auth_headers(),
        params=params
    )
    response.raise_for_status()
    return response.json()["results"]
```

### エラー分類マトリックス
| エラーコード | 原因分類 | 自動対応策 |
|-------------|----------|------------|
| 401         | 認証失敗 | APIキー再取得 |
| 404         | リソース不在 | エンドポイント検証 |
| 429         | レート制限 | 指数バックオフ |
| 500         | サーバーエラー | アラート通知 |

