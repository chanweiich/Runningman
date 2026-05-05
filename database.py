import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = "running_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS running_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upload_date TEXT,
            filename TEXT,
            distance_m REAL,
            pace_str TEXT,
            heart_rate REAL,
            cadence REAL,
            step_length_m REAL,
            vertical_oscillation_cm REAL,
            stance_time_ms REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_record(filename, summary_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO running_data (
            upload_date, filename, distance_m, pace_str, 
            heart_rate, cadence, step_length_m, 
            vertical_oscillation_cm, stance_time_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        now,
        filename,
        summary_data.get('distance_m', 0),
        summary_data.get('pace_str', "0:00/km"),
        summary_data.get('avg_heart_rate', 0),
        summary_data.get('avg_cadence', 0),
        summary_data.get('avg_step_length_m', 0),
        summary_data.get('avg_vertical_oscillation_cm', 0),
        summary_data.get('avg_stance_time_ms', 0)
    ))
    
    conn.commit()
    conn.close()

def get_history():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM running_data ORDER BY upload_date ASC", conn)
    conn.close()
    return df
