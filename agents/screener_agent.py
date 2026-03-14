import pandas as pd
import yfinance as yf
import requests
from concurrent.futures import ThreadPoolExecutor

class StockScreener:
    def __init__(self, limit=None):
        self.limit = limit

    def get_sp500_tickers(self):
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers)
            df = pd.read_html(response.text)[0]
            return df['Symbol'].str.replace('.', '-', regex=False).tolist()
        except Exception as e:
            print(f"Fetch failed: {e}")
            return []

    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def check_single_stock(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="1y", interval="1d", actions=False)
            if len(df) < 200: return None

            close = df['Close']
            ma50 = close.rolling(50).mean().iloc[-1]
            ma100 = close.rolling(100).mean().iloc[-1]
            ma200 = close.rolling(200).mean().iloc[-1]
            vol_avg = df['Volume'].tail(20).mean()
            last_rsi = self.calculate_rsi(close).iloc[-1]

            if (ma50 > ma200 > ma100) and (last_rsi > 50) and (vol_avg > 2000000):
                market_cap = stock.info.get('marketCap', 0)
                if market_cap > 2000000000:
                    return {
                        "Symbol": ticker, "Price": round(close.iloc[-1], 2),
                        "MarketCap": f"{market_cap/1e9:.1f}B", "RSI": round(last_rsi, 2)
                    }
            return None
        except Exception:
            return None

    def run(self):
        all_tickers = self.get_sp500_tickers()
        tickers = all_tickers[:self.limit] if self.limit else all_tickers
        print(f"🔎 Screening {len(tickers)} stocks...")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(self.check_single_stock, tickers))
        
        final_list = [r for r in results if r is not None]
        print(f"✅ Found {len(final_list)} candidates.")
        return final_list
