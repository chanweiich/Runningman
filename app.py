import streamlit as st
import pandas as pd
import plotly.express as px
from data_processor import process_fit_file
from ai_coach import get_coach_advice
from database import init_db, save_record, get_history

from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Antigravity 跑步數據分析", layout="wide", page_icon="🏃‍♂️")

def main():
    st.title("🏃‍♂️ Antigravity 跑步數據分析機器人")
    
    # 初始化資料庫
    init_db()
    
    # 側邊欄：檔案上傳
    with st.sidebar:
        st.header("上傳數據")
        uploaded_file = st.file_uploader("上傳 Garmin .fit 檔案", type=['fit'])
        st.info("提示：確保手錶有記錄進階跑步動態（如觸地時間、垂直振幅），分析結果會更精準。")
        
    # 處理上傳的檔案
    if uploaded_file is not None:
        with st.spinner('解析 FIT 檔案中... 執行資料清洗與單位轉換'):
            # 讀取檔案 bytes
            file_bytes = uploaded_file.read()
            filename = uploaded_file.name
            
            summary_data = process_fit_file(file_bytes)
            
            if not summary_data:
                st.error("無法解析此 FIT 檔案或找不到有效的跑步資料。")
                return
            
            st.subheader("📊 本次跑步數據摘要")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric("距離", f"{summary_data.get('distance_m', 0)/1000:.2f} km")
            col2.metric("配速", summary_data.get('pace_str', '0:00/km'))
            col3.metric("心率 (bpm)", f"{summary_data.get('avg_heart_rate', 0):.0f}")
            col4.metric("步頻 (spm)", f"{summary_data.get('avg_cadence', 0):.0f}")
            col5.metric("觸地時間 (ms)", f"{summary_data.get('avg_stance_time_ms', 0):.0f}")
            col6.metric("垂直振幅 (cm)", f"{summary_data.get('avg_vertical_oscillation_cm', 0):.1f}")
            
            # 儲存到資料庫
            save_record(filename, summary_data)
            
            # AI 教練分析
            st.subheader("🤖 AI 教練診斷")
            with st.spinner('教練思考中... 正在分析步頻、觸地時間與重力對抗情況'):
                advice = get_coach_advice(summary_data)
                st.write(advice)
                
    st.divider()
    
    # 歷史趨勢圖表
    st.subheader("📈 歷史進步軌跡")
    history_df = get_history()
    
    if not history_df.empty:
        # 將字串格式的 upload_date 轉為 datetime
        history_df['upload_date'] = pd.to_datetime(history_df['upload_date'])
        
        tab1, tab2, tab3 = st.tabs(["步頻趨勢", "觸地時間趨勢", "垂直振幅趨勢"])
        
        with tab1:
            fig_cadence = px.line(history_df, x='upload_date', y='cadence', 
                                  markers=True, title='平均步頻 (spm) 變化',
                                  hover_data=['filename', 'pace_str'])
            st.plotly_chart(fig_cadence, use_container_width=True)
            
        with tab2:
            fig_stance = px.line(history_df, x='upload_date', y='stance_time_ms', 
                                 markers=True, title='平均觸地時間 (ms) 變化',
                                 hover_data=['filename', 'pace_str'])
            st.plotly_chart(fig_stance, use_container_width=True)
            
        with tab3:
            fig_vo = px.line(history_df, x='upload_date', y='vertical_oscillation_cm', 
                             markers=True, title='平均垂直振幅 (cm) 變化',
                             hover_data=['filename', 'pace_str'])
            st.plotly_chart(fig_vo, use_container_width=True)
            
        # 顯示原始資料表
        with st.expander("查看所有歷史資料紀錄"):
            st.dataframe(history_df)
    else:
        st.info("目前還沒有歷史紀錄，請上傳您的第一個 FIT 檔案！")

if __name__ == "__main__":
    main()
