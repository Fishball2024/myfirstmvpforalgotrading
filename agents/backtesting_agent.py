from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
# 導入你剛才寫好的 DataAgent
from agents.data_agent import DataAgent
from config import INITIAL_CASH

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
        # 這裡我們簡化為：當 50 向上穿透 150 且目前價格在 200 之上時進場
        if crossover(self.ma50, self.ma150) and self.ma150 > self.ma200:
            self.buy()
        
        # 賣出邏輯：例如當 50 跌破 150 時出場
        elif crossover(self.ma150, self.ma50):
            self.position.close()

# 2. 回測執行器 (Backtest Agent 的核心)
def run_backtest_on_all():
    data_agent = DataAgent()
    full_data = data_agent.get_local_data()
    
    # 因為我們有 23 隻標的，我們需要循環跑回測
    for ticker in data_agent.tickers:
        # 提取單一股票的數據並格式化（backtesting.py 需要特定的列名）
        ticker_data = full_data[ticker].copy()
        ticker_data.columns = ['Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume']
        
        bt = Backtest(ticker_data, TripleMAStrategy, cash=INITIAL_CASH, commission=.002)
        stats = bt.run()
        
        print(f"\n===== {ticker} 回測結果 =====")
        print(f"總報酬率: {stats['Return [%]']:.2f}%")
        print(f"買入持有報酬率: {stats['Buy & Hold Return [%]']:.2f}%")
        print(f"最大回撤 (MDD): {stats['Max. Drawdown [%]']:.2f}%")
        # bt.plot() # 如果想看圖表可以取消註釋

if __name__ == "__main__":
    run_backtest_on_all()
