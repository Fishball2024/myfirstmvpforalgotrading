import pandas as pd
import os
import time
from agents.data_agent import DataAgent
from agents.backtesting_agent import run_backtest_on_all
# --- 新增的導入 ---
from agents.screener_agent import StockScreener
from utils.email_helper import send_stock_report

def main():
    print("=== 🚀 AI Algo Trading MVP 啟動 (Zeabur 環境) ===")
    
    # ---------------------------------------------------------
    # PART 1: 原有的回測流程 (10年數據)
    # ---------------------------------------------------------
    data_agent = DataAgent()
    
    if not os.path.exists(data_agent.output_file):
        print("📡 偵測到初次運行，正在從 Yahoo Finance 抓取 10 年數據...")
        data_agent.fetch_all_data()
    else:
        print("💾 偵測到本地緩存數據，跳過下載步驟。")

    print("\n📈 正在對 23 隻標的執行『三均線多頭策略』回測...")
    
    results = None
    try:
        results = run_backtest_on_all() 
    except Exception as e:
        print(f"❌ 回測過程發生嚴重錯誤: {e}")
    
    if results and len(results) > 0:
        df_results = pd.DataFrame(results)
        if "Return [%]" in df_results.columns:
            df_results = df_results.sort_values(by="Return [%]", ascending=False)
        
        target_cols = ['Ticker', 'Return [%]', 'Max. Drawdown [%]', 'Win Rate [%]']
        display_columns = [col for col in target_cols if col in df_results.columns]

        print("\n🏆 --- 10 年回測績效排行榜 (50/150/200 MA) ---")
        print(df_results[display_columns].to_string(index=False))
    else:
        print("⚠️ 無有效回測結果可供顯示。")

    # ---------------------------------------------------------
    # PART 2: 新增的 S&P 500 強勢股篩選 + Email 流程
    # ---------------------------------------------------------
    print("\n🔍 啟動自動化『S&P 500 強勢股篩選器』...")
    
    # 初始化篩選器 (測試時建議 limit 設小一點，例如 50；正式跑設 500)
    screener = StockScreener(limit=50) 
    candidates = screener.run()
    
    if candidates:
        print(f"🎯 篩選完成，發現 {len(candidates)} 隻符合條件的股票！正在準備郵件...")
        
        # 1. 構建 HTML 郵件內容
        html_body = f"""
        <html>
            <body>
                <h2 style="color: #2E86C1;">📊 今日 S&P 500 強勢股篩選報告</h2>
                <p>篩選條件：市值 > 2B, MA 多頭排列, 成交量 > 2M</p>
                <table border="1" style="border-collapse: collapse; width: 100%; text-align: left;">
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 8px;">代碼</th>
                        <th style="padding: 8px;">現價</th>
                        <th style="padding: 8px;">市值</th>
                        <th style="padding: 8px;">平均成交量</th>
                    </tr>
        """
        for s in candidates:
            html_body += f"""
                <tr>
                    <td style="padding: 8px;"><b>{s['Symbol']}</b></td>
                    <td style="padding: 8px;">${s['Price']}</td>
                    <td style="padding: 8px;">{s['MarketCap']}</td>
                    <td style="padding: 8px;">{s['Volume']}</td>
                </tr>
            """
        html_body += """
                </table>
                <br>
                <p style="color: #7F8C8D;">-- 來自您的 AI 交易管家 (Zeabur 自動化任務)</p>
            </body>
        </html>
        """
        
        # 2. 寄信 (請將以下 email 改為您要收信的地址)
        receiver = "tsekachun1992@yahoo.com.hk" 
        send_stock_report(receiver, "🎯 今日 S&P 500 強勢股篩選報告", html_body)
    else:
        print("💡 今日掃描完成，沒有符合所有條件的股票。")

    print("\n==============================================")
    print("✅ 所有任務已完成！")

    # --- 防止 Zeabur 重啟的休眠機制 ---
    print("\n☕ 任務已結束，程式進入休眠模式以便查看日誌 (預計休眠 24 小時)...")
    time.sleep(86400) 

if __name__ == "__main__":
    main()
