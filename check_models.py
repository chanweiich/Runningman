import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    print("正在抓取可用模型清單...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"可用模型: {m.name}")
except Exception as e:
    print(f"連線失敗: {e}")