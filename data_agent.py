import yfinance as yf
import pandas as pd
import os
from config import TICKERS, START_DATE, END_DATE, DATA_INTERVAL

class DataAgent:
    def __init__(self):
        self.tickers = TICKERS
        self.start = START_DATE
        self.end = END_DATE
        self.interval = DATA_INTERVAL
        self.output_file = "market_data.csv"

    def fetch_all_data(self):
        """
        抓取 config 中所有標的的歷史數據
        """
        print(f"🚀 Data Agent 開始工作...")
        print(f"📅 抓取區間: {self.start} 至 {self.end}")
        
        try:
            # 批次下載所有數據
            # group_by='column' 會讓數據以 Ticker 作為第一層級
            df = yf.download(
                self.tickers, 
                start=self.start, 
                end=self.end, 
                interval=self.interval,
                group_by='column'
            )
            
            if df.empty:
                print("❌ 沒抓到數據，請檢查網絡或 Ticker 代碼。")
                return None

            # 保存到本地，方便回測代理 (Backtest Agent) 直接讀取
            df.to_csv(self.output_file)
            print(f"✅ 成功抓取 {len(self.tickers)} 個標的數據，已存至 {self.output_file}")
            return df

        except Exception as e:
            print(f"🧨 發生錯誤: {e}")
            return None

    def get_local_data(self):
        """
        如果已經下載過，直接從本地讀取（節省時間）
        """
        if os.path.exists(self.output_file):
            return pd.read_csv(self.output_file, header=[0, 1], index_col=0)
        else:
            return self.fetch_all_data()

# 測試運行
if __name__ == "__main__":
    agent = DataAgent()
    data = agent.fetch_all_data()
    # 顯示前五行看看
    print("\n--- 數據摘要 ---")
    print(data.head())
