import fitparse
import pandas as pd
from dotenv import load_dotenv

# 強制載入環境變數
load_dotenv(override=True)

def format_pace(speed_mps):
    """Convert speed (m/s) to pace (min/km) string."""
    if pd.isna(speed_mps) or speed_mps <= 0:
        return "0:00/km"
    
    # 公式：seconds_per_km = 1000 / speed_mps
    pace_seconds_per_km = 1000 / speed_mps
    
    # 轉換為 MM:SS
    minutes = int(pace_seconds_per_km // 60)
    seconds = int(pace_seconds_per_km % 60)
    return f"{minutes}:{seconds:02d}/km"

def process_fit_file(file_bytes):
    """解析 FIT 檔案並萃取核心跑步數據，包含資料清洗與單位轉換"""
    fitfile = fitparse.FitFile(file_bytes)
    
    records = []
    
    for record in fitfile.get_messages('record'):
        data = {}
        for data_record in record:
            data[data_record.name] = data_record.value
        records.append(data)
        
    if not records:
        return {}

    df = pd.DataFrame(records)
    
    # 建立一個安全的取值函數
    def get_series(column_names):
        for col in column_names:
            if col in df.columns:
                return df[col]
        return pd.Series([None] * len(df))
    
    # 取出需要的欄位
    distance_series = get_series(['distance'])
    speed_series = get_series(['enhanced_speed', 'speed'])
    heart_rate_series = get_series(['heart_rate'])
    cadence_series = get_series(['cadence', 'fractional_cadence'])
    step_length_series = get_series(['step_length'])
    vertical_oscillation_series = get_series(['vertical_oscillation'])
    stance_time_series = get_series(['stance_time'])
    
    # 將需要過濾和計算的欄位整理成新的 DataFrame
    # 針對步頻：如果是單腳紀錄，直接在此乘以 2 修正為正常步頻 (約 160-180 spm)
    process_df = pd.DataFrame({
        'speed': pd.to_numeric(speed_series, errors='coerce'),
        'cadence': pd.to_numeric(cadence_series, errors='coerce') * 2,
        'heart_rate': pd.to_numeric(heart_rate_series, errors='coerce'),
        'step_length': pd.to_numeric(step_length_series, errors='coerce'),
        'vertical_oscillation': pd.to_numeric(vertical_oscillation_series, errors='coerce'),
        'stance_time': pd.to_numeric(stance_time_series, errors='coerce')
    })
    
    # 1. 資料清洗：過濾掉靜止或步行的無效數據
    # 條件：speed >= 1.5 m/s 且 cadence >= 100
    valid_df = process_df[(process_df['speed'] >= 1.5) & (process_df['cadence'] >= 100)]
    
    # 如果過濾後沒有資料，可能代表門檻太高或是這不是跑步活動，退回使用原始資料(去除NaN)計算
    if valid_df.empty:
        valid_df = process_df.dropna(subset=['speed', 'cadence'])
        if valid_df.empty:
             valid_df = process_df

    # 2. 計算平均值與精準的單位轉換
    avg_speed_mps = valid_df['speed'].mean()
    pace_str = format_pace(avg_speed_mps)
    
    avg_cadence = valid_df['cadence'].mean()
    avg_heart_rate = valid_df['heart_rate'].mean()
    
    # step_length (mm) 轉換為 (m)
    avg_step_length_m = valid_df['step_length'].mean() / 1000.0 if not valid_df['step_length'].isna().all() else 0
    
    # vertical_oscillation (mm) 轉換為 (cm)
    avg_vertical_oscillation_cm = valid_df['vertical_oscillation'].mean() / 10.0 if not valid_df['vertical_oscillation'].isna().all() else 0
    
    # stance_time 通常為 ms，保留
    avg_stance_time_ms = valid_df['stance_time'].mean() if not valid_df['stance_time'].isna().all() else 0
    
    # 總距離取最大值 (公尺)
    max_distance_m = distance_series.max() if not distance_series.isna().all() else 0
    
    summary_data = {
        'distance_m': max_distance_m,
        'avg_speed_mps': avg_speed_mps,
        'pace_str': pace_str,
        'avg_heart_rate': avg_heart_rate,
        'avg_cadence': avg_cadence,
        'avg_step_length_m': avg_step_length_m,
        'avg_vertical_oscillation_cm': avg_vertical_oscillation_cm,
        'avg_stance_time_ms': avg_stance_time_ms,
    }
    
    # 將 nan 轉為 0，避免 json 序列化錯誤
    for k, v in summary_data.items():
        if isinstance(v, (int, float)) and pd.isna(v):
            summary_data[k] = 0
            
    return summary_data
