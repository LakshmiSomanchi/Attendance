import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json
from airtable import Airtable

# --- Configuration ---
TABLE_NAME = "CRP/FA Attendance Table"  # Must match Airtable table name

# --- Person Lists ---
CRP_NAMES = [
    "Dhananjay Dewar", "Mahendra Tayde", "Shrihari Sontakke", "Roshan Ingle",
    "Nikhil Dhenge", "Pradip Gawande", "Manoj Thakre", "Amol Bute",
    "Dhananjay Gawande", "Pawan Ingle", "Amardip Bunde", "Gopal Tarale",
    "Shital Jalmakar", "Prabhakar Wankhade", "Bhagyashri Ghawat",
    "Rangpara Shailesh", "Olakiya Ramesh", "Paraliya Akash", "Chauhan Ajay",
    "Bavliya Umesh", "Parmar Asmita", "Malkiya Amit", "Malkiya Pravin",
    "Rathod Rohit", "Chauhan Vijay", "Malkiya Yash", "Khetariya Ravat",
    "Olakiya Vaishali", "Vaghela Hasubhai", "Vaghela Bavnaben",
    "Sarvaiya Kinjalben", "Dumadiya Vipul", "Jograjiya Chatur",
    "Luni Hiruben", "Kalotara Hirabhai", "Malkiya Hitesh",
    "Zampadiya Vijay", "Rangapara Arvindbhai", "Mkavana Sanjay",
    "Degama Vishal", "Mer Parth", "Shiyaliya Vijay", "Meniya Mahesh",
    "Dholakiya Manji", "Kahmani Navghan", "Dhoriya Rahul",
    "Dabhi Vasharam", "Dharajiya Mukesh", "Dharajiya Mehul",
    "Dabhi Ashok", "Bhusadiya Ajay", "Goriya Chhagan",
    "Dhoriya Kartik", "Rathod Dinesh", "Sitapara Sanjay",
    "Vaghela Shailesh", "Hadani Vishal", "Rajapara Bhavesh",
    "Chavda Jayesh", "Lalabhai Sambad", "Paramar Abhijit",
    "Makvana Vijay", "Sambad Sanjay", "Malakiya Akshay",
    "Sakariya Gopal", "Jograjiya Haresh", "Kansagara Lalji",
    "Rathod Hirabhai", "Rathod Vishal", "Sambad Jethabhai",
    "Borasaniya Jayraj", "Aal Rohit", "Zapadiya Hareshbhai",
    "Khatana Gelabhai", "Rabari Ramabhai", "Meghwal Jyotshanaben",
    "Vidiya Aratiben", "Chavan Jaypal", "Chavda Valabhai",
    "Makwana Ramesh", "Parmar Rajesh"
]

FA_NAMES = [
    "Rajan Patel", "Pedhadiya Dharmesh", "Maradiya Bhavna", "Khokhar Kishan",
    "Olakiya Kinjal", "Dabhi Divya", "Solanki Dharmedrabhai", "Dabhi Hemangi",
    "Simral Kilnake", "Shrikant Bajare"
]

ALL_PERSONS = sorted(CRP_NAMES + FA_NAMES)

# --- Airtable Connection ---
@st.cache_resource
def get_airtable_client():
    try:
        api_key = st.secrets["airtable"]["api_key"]
        base_id = st.secrets["airtable"]["base_id"]
        return Airtable(base_id, TABLE_NAME, api_key)
    except KeyError:
        st.error("Missing Airtable API Key or Base ID in Streamlit secrets.")
        st.stop()
    except Exception as e:
        st.error(f"Error connecting to Airtable: {e}")
        st.stop()

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

        if 'Timestamp' in df:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Failed to load data from Airtable: {e}")
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
        st.error(f"Error saving attendance: {e}")
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
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()
