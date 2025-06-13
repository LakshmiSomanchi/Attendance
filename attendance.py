# --- airtable_app.py ---

import streamlit as st
import pandas as pd
from datetime import datetime
from airtable import Airtable
from io import BytesIO
import subprocess
import sys

st.write("Python executable:", sys.executable)
st.write(subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True).stdout)


TABLE_NAME = "CRP/FA Attendance Table" 

@st.cache_resource
def get_airtable_client():
    try:
        api_key = st.secrets["airtable"]["api_key"]
        base_id = st.secrets["airtable"]["base_id"]
        return Airtable(base_id, TABLE_NAME, api_key)
    except KeyError as e:
        st.error("Missing Airtable API Key or Base ID in secrets.")
        raise e
    except Exception as e:
        st.error(f"Connection error: {e}")
        raise e

@st.cache_data(ttl=60)
def load_attendance_data_from_airtable():
    try:
        records = get_airtable_client().get_all()
        data = []
        for record in records:
            fields = record.get('fields', {})
            fields['record_id'] = record.get('id')
            data.append(fields)

        df = pd.DataFrame(data)
        expected = ['Timestamp', 'Person', 'Type', 'Status', 'Photo_Uploaded', 'Latitude', 'Longitude', 'record_id']
        for col in expected:
            if col not in df:
                df[col] = None

        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        return df

    except Exception as e:
        st.error(f"Failed to load Airtable data: {e}")
        return pd.DataFrame(columns=['Timestamp', 'Person', 'Type', 'Status', 'Photo_Uploaded', 'Latitude', 'Longitude', 'record_id'])

def mark_attendance(person, person_type, status, photo="No Photo", lat=None, lon=None):
    st.cache_data.clear()
    df = load_attendance_data_from_airtable()
    today = datetime.now().strftime('%Y-%m-%d')

    if not df[(df['Timestamp'].dt.strftime('%Y-%m-%d') == today) & (df['Person'] == person)].empty:
        st.warning(f"Attendance already marked today for {person}.")
        return False

    try:
        get_airtable_client().insert({
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Person': person,
            'Type': person_type,
            'Status': status,
            'Photo_Uploaded': photo,
            'Latitude': lat,
            'Longitude': lon
        })
        st.success(f"Attendance marked for {person} as {status}.")
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Insert error: {e}")
        return False

def update_record_in_airtable(record_id, fields):
    try:
        get_airtable_client().update(record_id, fields)
        st.success(f"Record {record_id} updated.")
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Update error: {e}")
        return False

def delete_record_from_airtable(record_id):
    try:
        get_airtable_client().delete(record_id)
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
