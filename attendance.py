# --- sqlite_attendance_app.py ---

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from io import BytesIO

DB_PATH = "attendance.db"
TABLE_NAME = "attendance"

# --- Initialize DB Table ---
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Timestamp TEXT,
                Person TEXT,
                Type TEXT,
                Status TEXT,
                Photo_Uploaded TEXT,
                Latitude REAL,
                Longitude REAL
            )
        ''')

@st.cache_data(ttl=60)
def load_attendance_data():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        return df

def mark_attendance(person, person_type, status, photo="No Photo", lat=None, lon=None):
    st.cache_data.clear()
    df = load_attendance_data()
    today = datetime.now().strftime('%Y-%m-%d')

    if not df[(df['Timestamp'].dt.strftime('%Y-%m-%d') == today) & (df['Person'] == person)].empty:
        st.warning(f"Attendance already marked today for {person}.")
        return False

    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute(f'''
                INSERT INTO {TABLE_NAME} (Timestamp, Person, Type, Status, Photo_Uploaded, Latitude, Longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                person,
                person_type,
                status,
                photo,
                lat,
                lon
            ))
            conn.commit()
            st.success(f"Attendance marked for {person} as {status}.")
            st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"Insert error: {e}")
            return False

def update_record(record_id, fields: dict):
    try:
        set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(f"UPDATE {TABLE_NAME} SET {set_clause} WHERE id = ?", list(fields.values()) + [record_id])
            conn.commit()
            st.success(f"Record {record_id} updated.")
            st.cache_data.clear()
            return True
    except Exception as e:
        st.error(f"Update error: {e}")
        return False

def delete_record(record_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (record_id,))
            conn.commit()
            st.success(f"Record {record_id} deleted.")
            st.cache_data.clear()
            return True
    except Exception as e:
        st.error(f"Delete error: {e}")
        return False

@st.cache_data
def convert_df_to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- Run DB init on load ---
init_db()
