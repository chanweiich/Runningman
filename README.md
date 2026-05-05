# 🏃‍♂️ Runningman - Antigravity 跑步數據分析系統

這是一個結合 Garmin 原始數據與 Gemini AI 的專業跑步診斷工具。本專案能自動解析 `.fit` 檔案，並針對跑者的跑步動力學（Running Dynamics）提供精準的 AI 改善建議。

## 🌟 核心功能
*   **自動數據校正**：自動將 Garmin 紀錄的單腳步頻修正為標準步頻（spm）。
*   **關鍵力學監測**：追蹤觸地時間、垂直振幅及步幅，精準定位「跨步煞車」問題。
*   **心率與效率分析**：整合平均心率與配速數據，評估有氧基礎與跑步效率。
*   **AI 反重力教練**：串接 **Gemini 2.5/3.0 Flash** 模型，提供具備動作意象的專業訓練處方。

## 🛠️ 技術棧
*   **Frontend**: Streamlit
*   **Data Processing**: Pandas, Fitparse
*   **AI Engine**: Google Generative AI (Gemini API)
*   **Database**: SQLite (用於儲存歷史訓練紀錄)

## 🚀 如何開始
1. 複製本專案：`git clone https://github.com/chanweiich/Runningman.git`
2. 安裝依賴：`pip install -r requirements.txt`
3. 建立 `.env` 檔案並加入你的 `GEMINI_API_KEY`。
4. 啟動程式：`streamlit run app.py`

---
*Developed by Zhang Zhewei (張哲瑋), NCCU Political Science.*
*以 2026 國道馬拉松 1:51:19 PB 的實戰經驗為開發基礎。*