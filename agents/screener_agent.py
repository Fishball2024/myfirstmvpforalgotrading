import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor

class StockScreener:
    def __init__(self, limit=None):
        self.limit = limit

    def get_sp500_tickers(self):
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        df = pd.read_html(url)[0]
        return df['Symbol'].str.replace('.', '-', regex=False).tolist()

    def check_single_stock(self, ticker):
        """執行您的篩選條件"""
        try:
            stock = yf.Ticker(ticker)
            # 1. 市值過濾 (> 2 Billion)
            market_cap = stock.info.get('marketCap', 0)
            if market_cap < 2000000000: return None

            # 2. 抓取數據計算技術指標
            df = stock.history(period="1y")
            if len(df) < 200: return None

            close = df['Close']
            ma50 = close.rolling(50).mean().iloc[-1]
            ma100 = close.rolling(100).mean().iloc[-1]
            ma200 = close.rolling(200).mean().iloc[-1]
            vol_avg = df['Volume'].rolling(20).mean().iloc[-1]

            # 3. 條件判斷: MA排列 (50 > 200 > 100) & 成交量 > 2M
            if (ma50 > ma200 > ma100) and (vol_avg > 2000000):
                # 這裡可以再加入 RSI 邏輯
                return {
                    "Symbol": ticker,
                    "Price": round(close.iloc[-1], 2),
                    "MarketCap": f"{market_cap/1e9:.1f}B",
                    "Volume": f"{vol_avg/1e6:.1f}M"
                }
        except:
            return None

    def run(self):
        tickers = self.get_sp500_tickers()[:self.limit]
        print(f"🔎 開始篩選 {len(tickers)} 隻股票...")
        
        # 使用多線程加快掃描速度
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(self.check_single_stock, tickers))
        
        return [r for r in results if r is not None]
