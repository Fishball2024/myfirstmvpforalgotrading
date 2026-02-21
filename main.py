import pandas as pd
from agents.data_agent import DataAgent
from agents.backtesting_agent import run_backtest_on_all
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
    
    results = None
    try:
        # 執行所有標的回測
        results = run_backtest_on_all() 
    except Exception as e:
        print(f"❌ 回測過程發生嚴重錯誤: {e}")
    
    # 4. 排序並輸出最專業的報告
    if results and len(results) > 0:
        df_results = pd.DataFrame(results)
        
        # 確保排序欄位存在
        if "Return [%]" in df_results.columns:
            df_results = df_results.sort_values(by="Return [%]", ascending=False)
        
        # 定義要顯示的欄位，並過濾掉 DataFrame 中不存在的欄位避免 KeyError
        target_cols = ['Ticker', 'Return [%]', 'Max. Drawdown [%]', 'Win Rate [%]']
        display_columns = [col for col in target_cols if col in df_results.columns]

        print("\n🏆 --- 10 年回測績效排行榜 (50/150/200 MA) ---")
        print(df_results[display_columns].to_string(index=False))
        print("\n==============================================")
        print("✅ 任務完成！")
    else:
        print("⚠️ 無有效回測結果可供顯示。")

if __name__ == "__main__":
    main()


# ... 原有的排行榜輸出代碼 ...
    print("\n==============================================")
    print("✅ 任務完成！")

    # --- 新增：防止 Zeabur 重啟的休眠機制 ---
    import time
    print("\n☕ 任務已結束，程式進入休眠模式以便查看日誌 (預計休眠 24 小時)...")
    time.sleep(86400) # 讓它睡 24 小時，這樣就不會重啟了
