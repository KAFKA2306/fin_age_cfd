import os
import requests
import pandas as pd
import urllib.parse
import logging
from datetime import datetime
import config as config

BASE_URL = config.BASE_URL
API_KEY = config.API_KEY
SRC_DIR = config.SRC_DIR
OUTPUT_DIR = config.OUTPUT_DIR

logging.basicConfig(
    filename=os.path.join(SRC_DIR, 'api_errors.log'),
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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

def get_auth_headers() -> dict:
    return {
        "Authorization": f"Bearer {os.getenv('FINAGE_API_KEY')}",
        "X-API-Version": "2025Q2"
    }

def normalize_symbol(symbol: str) -> str:
    encoded = urllib.parse.quote(symbol, safe='')
    return encoded.replace('^', '%5E')


def get_last_price(asset_type, symbol):
    endpoint_map = {
        "stock": f"/last/stock/{symbol}",
        "forex": f"/last/forex/{symbol}",
        "crypto": f"/last/crypto/{symbol}",
        "index": f"/last/stock-index/{urllib.parse.quote(symbol, safe='')}"
    }
    
    endpoint = endpoint_map.get(asset_type)
    if not endpoint:
        logging.error(f"無効な資産タイプ: {asset_type}")
        return {}
    
    url = f"{BASE_URL}{endpoint}"
    params = {"apikey": API_KEY}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"最新価格取得エラー: {e}")
        logging.error(f"最新価格取得エラー: {e} -  ")
        return {}


def save_data_to_parquet(df, asset_type, filename):
    output_path = os.path.join(OUTPUT_DIR, asset_type, filename)
    df.to_parquet(output_path)
    return output_path

def save_data_to_json(data, asset_type, filename):
    output_path = os.path.join(OUTPUT_DIR, asset_type, filename)
    with open(output_path, 'w') as f:
        pd.Series(data).to_json(f, orient='index')
    return output_path

def main():
    if not API_KEY:
        print("APIキーが設定されていません")
        return

    for asset in config.TARGET_ASSETS:
        last_price = get_last_price(asset['type'], asset['symbol'])
        print(f"{asset['type']} {asset['symbol']}: {last_price}")

if __name__ == "__main__":
    config.create_directories()
    main()

