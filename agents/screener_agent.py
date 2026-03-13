import pandas as pd
import yfinance as yf
import requests
from concurrent.futures import ThreadPoolExecutor

class StockScreener:
    def __init__(self, limit=None):
        self.limit = limit

    def get_sp500_tickers(self):
        """獲取 S&P 500 名單，加入 Headers 防止 403 錯誤"""
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers)
            df = pd.read_html(response.text)[0]
            # yfinance 格式：將 . 替換為 - (例如 BRK.B 轉為 BRK-B)
            return df['Symbol'].str.replace('.', '-', regex=False).tolist()
        except Exception as e:
            print(f"❌ 獲取名單失敗: {e}")
            return []

    def calculate_rsi(self, series, period=14):
        """計算 RSI 指標"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def check_single_stock(self, ticker):
        """執行詳細篩選條件"""
        try:
            stock = yf.Ticker(ticker)
            
            # 1. 抓取數據 (獲取 1 年日線數據以計算 MA200)
            # 使用 history 獲取價格，這比直接拿 info 快很多
            df = stock.history(period="1y", interval="1d", actions=False)
            if len(df) < 200: 
                return None

            # 2. 計算技術指標
            close = df['Close']
            ma50 = close.rolling(50).mean().iloc[-1]
            ma100 = close.rolling(100).mean().iloc[-1]
            ma200 = close.rolling(200).mean().iloc[-1]
            
            # 成交量 (取最近 20 日平均成交量)
            vol_avg = df['Volume'].tail(20).mean()
            
            # RSI 計算
            rsi_values = self.calculate_rsi(close)
            last_rsi = rsi_values.iloc[-1]

