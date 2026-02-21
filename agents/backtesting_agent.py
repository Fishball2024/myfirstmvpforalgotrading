from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
# 導入 DataAgent
from agents.data_agent import DataAgent
from config import INITIAL_CASH, TICKERS

# 1. 定義策略類別
class TripleMAStrategy(Strategy):
    n1 = 50
    n2 = 150
    n3 = 200

    def init(self):
        # 使用 lambda 確保數據格式正確傳遞給 rolling
        self.ma50 = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), self.data.Close)
        self.ma150 = self.I(lambda x: pd.Series(x).rolling(self.n2).mean(), self.data.Close)
        self.ma200 = self.I(lambda x: pd.Series(x).rolling(self.n3).mean(), self.data.Close)

    def next(self):
        # 策略邏輯：當 50MA > 150MA 且 150MA > 200MA 時買入
        if crossover(self.ma50, self.ma150) and self.ma150 > self.ma200:
            self.buy()
        
        # 賣出邏輯：當 150MA 穿透回 50MA (50跌破150) 時出場
        elif crossover(self.ma150, self.ma50):
            self.position.close()

# 2. 回測執行器
def run_backtest_on_all():
    data_agent = DataAgent()
    full_data = data_agent.get_local_data()
    
    if full_data is None:
        print("❌ 無法獲取回測數據")
        return []

    results = [] # 用於存儲結果清單
    
    for ticker in TICKERS:
        try:
            # 檢查該股票是否在數據表中 (處理 MultiIndex)
            if ticker not in full_data.columns.levels[0]:
                continue
                
            # 提取數據並清理空值
            ticker_data = full_data[ticker].dropna().copy()
            
            # 確保欄位符合 Backtesting 規範
            available_cols = ticker_data.columns.tolist()
            # 根據 DataAgent 的 auto_adjust=True，欄位應為 Open, High, Low, Close, Volume
            needed_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            # 檢查欄位是否存在
            if not all(col in available_cols for col in needed_cols):
                print(f"⚠️ {ticker} 數據格式不符，跳過。")
                continue

            ticker_data = ticker_data[needed_cols]

            # 執行回測
            bt = Backtest(ticker_data, TripleMAStrategy, cash=INITIAL_CASH, commission=.002)
            stats = bt.run()
            
            # 實時打印進度
            print(f"📊 {ticker}: Return {stats['Return [%]']:.2f}% | MDD {stats['Max. Drawdown [%]']:.2f}%")
            
            # 存入結果清單
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

    return results

if __name__ == "__main__":
    res = run_backtest_on_all()
    if res:
        print("\n--- 測試排行榜 ---")
        print(pd.DataFrame(res).sort_values(by="Return [%]", ascending=False).head())
