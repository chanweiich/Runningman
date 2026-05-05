import os
import json
import traceback
import google.generativeai as genai
from dotenv import load_dotenv

# 強制載入 .env 檔案
load_dotenv(override=True)

antigravity_system_prompt = """
你是一位 Antigravity 反重力跑步教練。請根據跑者的步頻、步幅、垂直振幅與觸地時間，分析是否有『嚴重跨步煞車效應』或『過度對抗重力（上下彈跳）』的問題。
同時，請分析「心率與配速的關係」。例如：在高配速下心率是否過高（代表有氧基礎待加強），或在相同心率下配速是否有進步。
必須給出 1 個動作意象與 1 個具體輔助訓練，嚴禁只給出『請提高步頻』等無效建議。
"""

def get_coach_advice(summary_data):
    # 取得 API Key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_api_key_here":
        return "⚠️ 請先在 .env 檔案中設定您的 GEMINI_API_KEY"

    try:
        # 初始化 API 金鑰
        genai.configure(api_key=GEMINI_API_KEY)
        
        # 根據環境可用模型，精確指定模型名稱為 models/gemini-2.5-flash
        model = genai.GenerativeModel(
            model_name="models/gemini-2.5-flash",
            system_instruction=antigravity_system_prompt
        )
        
        # 準備給模型的資料
        prompt_data = {
            "配速": summary_data.get('pace_str', '未知'),
            "平均心率 (bpm)": round(summary_data.get('avg_heart_rate', 0), 1),
            "步頻 (spm)": round(summary_data.get('avg_cadence', 0), 1),
            "步幅 (m)": round(summary_data.get('avg_step_length_m', 0), 2),
            "垂直振幅 (cm)": round(summary_data.get('avg_vertical_oscillation_cm', 0), 2),
            "觸地時間 (ms)": round(summary_data.get('avg_stance_time_ms', 0), 1)
        }
        
        user_prompt = f"這是這位跑者本次的平均跑步動態數據：\n{json.dumps(prompt_data, ensure_ascii=False, indent=2)}\n請針對這些數據給我教練建議。"
        
        response = model.generate_content(user_prompt)
        return response.text
        
    except Exception as e:
        error_msg = f"API 呼叫發生錯誤：{type(e).__name__}\n錯誤訊息：{str(e)}\n\n詳細 Traceback:\n{traceback.format_exc()}"
        print("=== Gemini API Error ===")
        print(error_msg)
        print("========================")
        return f"⚠️ 抱歉，AI 教練連線發生問題。以下是詳細的錯誤資訊供排解：\n\n```text\n{error_msg}\n```"
