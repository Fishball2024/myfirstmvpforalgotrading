import os
from datetime import datetime, timedelta

# --- 1. 交易標的設定 (Tickers) ---
# 包含：科技巨頭、零售消費、生物醫療、能源板塊
TICKERS = [
    # 科技與互聯網
    "GOOG", "AMZN", "AAPL", "META", "NVDA", "TSLA", "SHOP", "VEEV",
    # 零售與民生用品
    "COST", "PG", "TGT", "WMT",
    # 醫療與生物科技
    "LLY", "TEM", "BIIB", "BMY", "NVO", "REGN",
    # 能源
    "EOG", "XOM", "EQT", "CVX", "COP"
]

# --- 2. 回測時間範圍 (10年) ---
# 自動抓取從今天起往回推 10 年的數據
# 2026 年運行的話，會自動抓取 2016 至今的數據
_end_dt = datetime.now()
_start_dt = _end_dt - timedelta(days=10*365)

END_DATE = _end_dt.strftime('%Y-%m-%d')
START_DATE = _start_dt.strftime('%Y-%m-%d')

# --- 3. 策略與數據參數 ---
DATA_INTERVAL = "1d"      # 日線數據
INITIAL_CASH = 10000      # 初始資金 (美元)
COMMISSION = 0.002        # 交易佣金設定 (0.2%)

# --- 4. 均線策略參數 ---
SMA_FAST = 50
SMA_MEDIUM = 150
SMA_SLOW = 200

# --- 5. 系統與路徑設定 ---
DATA_FILE = "market_data.csv"
# 預留給未來 AI Agent 使用的 API KEY 區塊
# 部署在 Zeabur 時，建議從環境變數讀取
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_placeholder_key")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "your_placeholder_key")
