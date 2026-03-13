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
            
            # 1. 抓取數據 (獲取 1 年日線數據以計算 MA)
            df = stock.history(period="1y", interval="1d", actions=False)
            if len(df) < 200: 
                return None

            # 2. 計算技術指標
            close = df['Close']
            ma50 = close.rolling(50).mean().iloc[-1]
            ma100 = close.rolling(100).mean().iloc[-1]
            ma200 = close.rolling(200).mean().iloc[-1]
            
            # 成交量 (最近 20 日平均成交量)
            vol_avg = df['Volume'].tail(20).mean()
            
            # RSI 計算
            rsi_values = self.calculate_rsi(close)
            last_rsi = rsi_values.iloc[-1]

            # 3. 條件篩選 (MA50 > MA200 > MA100 且 RSI > 50 且 成交量 > 2M)
            if (ma50 > ma200 > ma100) and (last_rsi > 50) and (vol_avg > 2000000):
                # 4. 市值過濾 (> 2B)
                market_cap = stock.info.get('marketCap', 0)
                if market_cap > 2000000000:
                    return {
                        "Symbol": ticker,
                        "Price": round(close.iloc[-1], 2),
                        "MarketCap": f"{market_cap/1e9:.1f}B",
                        "Volume": f"{vol_avg/1e6:.1f}M",
                        "RSI": round(last_rsi, 2)
                    }
            return None
        except Exception:
            # 這是第 56 行左右的關鍵點，確保這個 except 區塊存在
            return None

    def run(self):
        """啟動篩選流程"""
        all_tickers = self.get_sp500_tickers()
        if not all_tickers:
            return []
            
        tickers = all_tickers[:self.limit] if self.limit else all_tickers
        print(f"🔎 開始篩選 {len(tickers)} 隻股票 (S&P 500)...")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(self.check_single_stock, tickers))
        
        final_list = [r for r in results if r is not None]
        print(f"✅ 篩選完成！共找到 {len(final_list)} 隻符合條件。")
        return final_list
