from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
# 導入你剛才寫好的 DataAgent
from agents.data_agent import DataAgent
from config import INITIAL_CASH, TICKERS

# 1. 定義策略類別
class TripleMAStrategy(Strategy):
    n1 = 50
    n2 = 150
    n3 = 200

    def init(self):
        # 計算三條均線
        self.ma50 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), self.data.Close)
        self.ma150 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), self.data.Close)
        self.ma200 = self.I(lambda x: pd.Series(x).rolling(self.n3).mean(), self.data.Close)

    def next(self):
        # 策略邏輯：當 50 > 150 且 150 > 200 時買入
        if crossover(self.ma50, self.ma150) and self.ma150 > self.ma200:
            self.buy()
        
        # 賣出邏輯：當 50 跌破 150 時出場
        elif crossover(self.ma150, self.ma50):
            self.position.close()

# 2. 回測執行器
def run_backtest_on_all():
    data_agent = DataAgent()
    full_data = data_agent.get_local_data()
    
    if full_data is None:
        print("❌ 無法獲取回測數據")
        return []

    results = [] # 用於存儲所有股票的結果，供 main.py 排行榜使用
    
    # 循環跑回測
    for ticker in TICKERS:
        try:
            # 💡 修正點：從 MultiIndex 中提取單一股票數據並去掉缺失值
            if ticker not in full_data.columns.levels[0]:
                continue
                
            ticker_data = full_data[ticker].dropna().copy()
            
            # 💡 修正點：確保列名符合 Backtesting.py 的要求 (首字母大寫)
            # yfinance auto_adjust=True 會回傳 Open, High, Low, Close, Volume
            # 這裡做一個保險的列名轉換
            ticker_data = ticker_data[['Open', 'High', 'Low', 'Close', 'Volume']]

            # 執行回測
            bt = Backtest(ticker_data, TripleMAStrategy, cash=INITIAL_CASH, commission=.002)
            stats = bt.run()
            
            # 打印單一標的結果
            print(f"📊 {ticker}: Return {stats['Return [%]']:.2f}% | MDD {stats['Max. Drawdown [%]']:.2f}%")
            
            # 💡 修正點：將關鍵指標存入字典，以便 main.py 生成排行榜
            results.append({
                "Ticker": ticker,
                "Return [%]": stats['Return [%]'],
                "Max. Drawdown [%]": stats['Max. Drawdown [%]'],
                "Win Rate [%]": stats['Win Rate [%]'],
                "Total Trades": stats['# Trades']
            })

        except Exception as e:
            print(f"❌ {ticker} 回測出錯: {e}")
            continue

    return results # 回傳完整結果清單

if __name__ == "__main__":
    res = run_backtest_on_all()
    # 簡單打印測試
    if res:
        print("\n--- 測試排行榜 ---")
        print(pd.DataFrame(res).sort_values(by="Return [%]", ascending=False).head())
