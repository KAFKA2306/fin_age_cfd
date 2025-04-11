import os

BASE_DIR = fr"M:\ML\Finance\fin_age_cfd"
SRC_DIR = os.path.join(BASE_DIR, "src")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

API_KEY = os.getenv("FINAGE_API_KEY")

if not API_KEY:
    print("警告: 環境変数 'FINAGE_API_KEY' が設定されていません。")

DATA_TYPES = ["stock", "forex", "crypto", "index", "combined_data"]
def create_directories():
    directories = [
        OUTPUT_DIR,
        os.path.join(OUTPUT_DIR, "stock"),
        os.path.join(OUTPUT_DIR, "forex"),
        os.path.join(OUTPUT_DIR, "crypto"),
        os.path.join(OUTPUT_DIR, "index")
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            if directory != OUTPUT_DIR:
                print(f"Subdirectory checked/created: {directory}")

TARGET_ASSETS = [
    {"type": "stock", "symbol": "AAPL"},
    {"type": "forex", "symbol": "GBPUSD"},
    {"type": "crypto", "symbol": "BTCUSD"},
    {"type": "index", "symbol": "^GSPC"}
]
