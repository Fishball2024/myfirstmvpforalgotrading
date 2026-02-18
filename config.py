from datetime import datetime, timedelta

# 2. 回測時間範圍 (改為過去 10 年)
# 今天是 2026-02-18，這將抓取自 2016-02-18 左右開始的數據
END_DATE = datetime.now().strftime('%Y-%m-%d')
START_DATE = (datetime.now() - timedelta(days=10*365)).strftime('%Y-%m-%d')