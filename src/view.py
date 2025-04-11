import os
import glob
import pandas as pd
import config
from IPython.display import display

def display_parquet_files():
    for data_type in config.DATA_TYPES:
        if data_type == "combined_data":
            data_type_dir = os.path.join(config.OUTPUT_DIR, data_type)
        else:
            data_type_dir = os.path.join(config.OUTPUT_DIR, data_type)
        parquet_files = glob.glob(os.path.join(data_type_dir, "*.parquet"))
        parquet_files.sort()  # ファイルを順番に表示するためにソート
    
    file_path = None  # file_pathを初期化
    if not parquet_files:
        print("parquetファイルが見つかりませんでした。")
    else:
        for file_path in parquet_files:
            print(f"ファイル: {file_path}")
            try:
                df = pd.read_parquet(file_path)
                display(df)
            except Exception as e:
                print(f"エラー: {file_path} の読み込みに失敗しました: {e}")

        pass

if __name__ == "__main__":
    display_parquet_files()