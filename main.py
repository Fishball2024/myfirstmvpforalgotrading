import pandas as pd
from agents.data_agent import DataAgent
from agents.backtest_agent import run_backtest_on_all
import os

def main():
    print("=== 🚀 AI Algo Trading MVP 啟動 (Zeabur 環境) ===")
    
    # 1. 初始化數據代理
    data_agent = DataAgent()
    
    # 2. 檢查本地是否有數據，沒有則抓取 (10年數據)
    if not os.path.exists(data_agent.output_file):
        print("📡 偵測到初次運行，正在從 Yahoo Finance 抓取 10 年數據...")
        data_agent.fetch_all_data()
    else:
        print("💾 偵測到本地緩存數據，跳過下載步驟。")

    # 3. 執行回測並獲取排行榜
    print("\n📈 正在對 23 隻標的執行『三均線多頭策略』回測...")
    # 這裡我們稍微修改一下 backtest_agent 的回測函數，讓它回傳結果
    results = run_backtest_on_all() 
    
    # 4. 排序並輸出最專業的報告
    if results:
        df_results = pd.DataFrame(results).sort_values(by="Return [%]", ascending=False)
        print("\n🏆 --- 10 年回測績效排行榜 (50/150/200 MA) ---")
        print(df_results[['Ticker', 'Return [%]', 'Max. Drawdown [%]', 'Win Rate [%]']].to_string(index=False))
        print("\n==============================================")
        print("✅ 任務完成！")

if __name__ == "__main__":
    main()
