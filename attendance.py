import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from io import BytesIO
import pytz
import os
import uuid
import zipfile

# --- Constants and Configuration ---
DB_PATH = "attendance.db"
TABLE_NAME = "attendance"
UPLOAD_FOLDER = "uploaded_photos"

# --- App Constants ---
ATTENDANCE_STATUSES = ["Present", "On Leave", "Absent"]
PHOTO_STATUSES = ["Photo Uploaded", "No Photo", "Photo Upload Failed"]
ROLES = ["CRP", "FA", "Unknown"]

# --- Helper Functions for Data ---

def get_all_field_workers():
    """Returns the list of all field workers."""
    return [
        # CRP Names - Maharashtra
        {"name": "Dhananjay Dewar", "role": "CRP", "state": "Maharashtra"},
        {"name": "Mahendra Tayde", "role": "CRP", "state": "Maharashtra"},
        {"name": "Shrihari Sontakke", "role": "CRP", "state": "Maharashtra"},
        {"name": "Roshan Ingle", "role": "CRP", "state": "Maharashtra"},
        {"name": "Nikhil Dhenge", "role": "CRP", "state": "Maharashtra"},
        {"name": "Pradip Gawande", "role": "CRP", "state": "Maharashtra"},
        {"name": "Manoj Thakre", "role": "CRP", "state": "Maharashtra"},
        {"name": "Amol Bute", "role": "CRP", "state": "Maharashtra"},
        {"name": "Dhananjay Gawande", "role": "CRP", "state": "Maharashtra"},
        {"name": "Pawan Ingle", "role": "CRP", "state": "Maharashtra"},
        {"name": "Amardip Bunde", "role": "CRP", "state": "Maharashtra"},
        {"name": "Gopal Tarale", "role": "CRP", "state": "Maharashtra"},
        {"name": "Shital Jalmakar", "role": "CRP", "state": "Maharashtra"},
        {"name": "Prabhakar Wankhade", "role": "CRP", "state": "Maharashtra"},
        {"name": "Bhagyashri Ghawat", "role": "CRP", "state": "Maharashtra"},
        # CRP Names - Gujarat
        {"name": "Rangpara Shailesh", "role": "CRP", "state": "Gujarat"},
        {"name": "Olakiya Ramesh", "role": "CRP", "state": "Gujarat"},
        {"name": "Paraliya Akash", "role": "CRP", "state": "Gujarat"},
        {"name": "Chauhan Ajay", "role": "CRP", "state": "Gujarat"},
        {"name": "Bavliya Umesh", "role": "CRP", "state": "Gujarat"},
        {"name": "Parmar Asmita", "role": "CRP", "state": "Gujarat"},
        {"name": "Malkiya Amit", "role": "CRP", "state": "Gujarat"},
        {"name": "Malkiya Pravin", "role": "CRP", "state": "Gujarat"},
        {"name": "Rathod Rohit", "role": "CRP", "state": "Gujarat"},
        {"name": "Chauhan Vijay", "role": "CRP", "state": "Gujarat"},
        {"name": "Malkiya Yash", "role": "CRP", "state": "Gujarat"},
        {"name": "Khetariya Ravat", "role": "CRP", "state": "Gujarat"},
        {"name": "Olakiya Vaishali", "role": "CRP", "state": "Gujarat"},
        {"name": "Vaghela Hasubhai", "role": "CRP", "state": "Gujarat"},
        {"name": "Vaghela Bavnaben", "role": "CRP", "state": "Gujarat"},
        {"name": "Sarvaiya Kinjalben", "role": "CRP", "state": "Gujarat"},
        {"name": "Dumadiya Vipul", "role": "CRP", "state": "Gujarat"},
        {"name": "Jograjiya Chatur", "role": "CRP", "state": "Gujarat"},
        {"name": "Luni Hiruben", "role": "CRP", "state": "Gujarat"},
        {"name": "Kalotara Hirabhai", "role": "CRP", "state": "Gujarat"},
        {"name": "Malkiya Hitesh", "role": "CRP", "state": "Gujarat"},
        {"name": "Zampadiya Vijay", "role": "CRP", "state": "Gujarat"},
        {"name": "Rangapara Arvindbhai", "role": "CRP", "state": "Gujarat"},
        {"name": "Mkavana Sanjay", "role": "CRP", "state": "Gujarat"},
        {"name": "Degama Vishal", "role": "CRP", "state": "Gujarat"},
        {"name": "Mer Parth", "role": "CRP", "state": "Gujarat"},
        {"name": "Shiyaliya Vijay", "role": "CRP", "state": "Gujarat"},
        {"name": "Meniya Mahesh", "role": "CRP", "state": "Gujarat"},
        {"name": "Dholakiya Manji", "role": "CRP", "state": "Gujarat"},
        {"name": "Kahmani Navghan", "role": "CRP", "state": "Gujarat"},
        {"name": "Dhoriya Rahul", "role": "CRP", "state": "Gujarat"},
        {"name": "Dabhi Vasharam", "role": "CRP", "state": "Gujarat"},
        {"name": "Dharajiya Mukesh", "role": "CRP", "state": "Gujarat"},
        {"name": "Dharajiya Mehul", "role": "CRP", "state": "Gujarat"},
        {"name": "Dabhi Ashok", "role": "CRP", "state": "Gujarat"},
        {"name": "Bhusadiya Ajay", "role": "CRP", "state": "Gujarat"},
        {"name": "Goriya Chhagan", "role": "CRP", "state": "Gujarat"},
        {"name": "Dhoriya Kartik", "role": "CRP", "state": "Gujarat"},
        {"name": "Rathod Dinesh", "role": "CRP", "state": "Gujarat"},
        {"name": "Sitapara Sanjay", "role": "CRP", "state": "Gujarat"},
        {"name": "Vaghela Shailesh", "role": "CRP", "state": "Gujarat"},
        {"name": "Hadani Vishal", "role": "CRP", "state": "Gujarat"},
        {"name": "Rajapara Bhavesh", "role": "CRP", "state": "Gujarat"},
        {"name": "Chavda Jayesh", "role": "CRP", "state": "Gujarat"},
        {"name": "Lalabhai Sambad", "role": "CRP", "state": "Gujarat"},
        {"name": "Paramar Abhijit", "role": "CRP", "state": "Gujarat"},
        {"name": "Makvana Vijay", "role": "CRP", "state": "Gujarat"},
        {"name": "Sambad Sanjay", "role": "CRP", "state": "Gujarat"},
        {"name": "Malakiya Akshay", "role": "CRP", "state": "Gujarat"},
        {"name": "Sakariya Gopal", "role": "CRP", "state": "Gujarat"},
        {"name": "Jograjiya Haresh", "role": "CRP", "state": "Gujarat"},
        {"name": "Kansagara Lalji", "role": "CRP", "state": "Gujarat"},
        {"name": "Rathod Hirabhai", "role": "CRP", "state": "Gujarat"},
        {"name": "Rathod Vishal", "role": "CRP", "state": "Gujarat"},
        {"name": "Sambad Jethabhai", "role": "CRP", "state": "Gujarat"},
        {"name": "Borasaniya Jayraj", "role": "CRP", "state": "Gujarat"},
        {"name": "Aal Rohit", "role": "CRP", "state": "Gujarat"},
        {"name": "Zapadiya Hareshbhai", "role": "CRP", "state": "Gujarat"},
        {"name": "Khatana Gelabhai", "role": "CRP", "state": "Gujarat"},
        {"name": "Rabari Ramabhai", "role": "CRP", "state": "Gujarat"},
        {"name": "Meghwal Jyotshanaben", "role": "CRP", "state": "Gujarat"},
        {"name": "Vidiya Aratiben", "role": "CRP", "state": "Gujarat"},
        {"name": "Chavan Jaypal", "role": "CRP", "state": "Gujarat"},
        {"name": "Chavda Valabhai", "role": "CRP", "state": "Gujarat"},
        {"name": "Makwana Ramesh", "role": "CRP", "state": "Gujarat"},
        {"name": "Parmar Rajesh", "role": "CRP", "state": "Gujarat"},
        # FA Names
        {"name": "Rajan Patel", "role": "FA", "state": "Gujarat"},
        {"name": "Pedhadiya Dharmesh", "role": "FA", "state": "Gujarat"},
        {"name": "Maradiya Bhavna", "role": "FA", "state": "Gujarat"},
        {"name": "Khokhar Kishan", "role": "FA", "state": "Gujarat"},
        {"name": "Olakiya Kinjal", "role": "FA", "state": "Gujarat"},
        {"name": "Dabhi Divya", "role": "FA", "state": "Gujarat"},
        {"name": "Solanki Dharmedrabhai", "role": "FA", "state": "Gujarat"},
        {"name": "Dabhi Hemangi", "role": "FA", "state": "Gujarat"},
        {"name": "Simral Kilnake", "role": "FA", "state": "Maharashtra"},
        {"name": "Shrikant Bajare", "role": "FA", "state": "Maharashtra"},
    ]

# Pre-compute maps for efficient lookups
ALL_FIELD_WORKERS = get_all_field_workers()
NAME_TO_ROLE_MAP = {worker["name"]: worker["role"] for worker in ALL_FIELD_WORKERS}
NAME_TO_STATE_MAP = {worker["name"]: worker["state"] for worker in ALL_FIELD_WORKERS}

@st.cache_data
def create_zip_of_photos(photo_paths):
    """Creates a ZIP file in memory containing the specified photo files."""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, False) as zip_file:
        for photo_path in photo_paths:
            if os.path.exists(photo_path):
                zip_file.write(photo_path, os.path.basename(photo_path))
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

# --- Database Management ---

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initializes the database table and photo upload directory."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Timestamp TEXT,
                Date TEXT,
                Person TEXT,
                Type TEXT,
                Status TEXT,
                Photo_Uploaded TEXT,
                Photo_Path TEXT,
                Latitude REAL,
                Longitude REAL,
                State TEXT,
                UNIQUE (Person, Date)
            )
        ''')

        existing_columns = [col[1] for col in cursor.execute(f"PRAGMA table_info({TABLE_NAME})").fetchall()]
        
        if 'Date' not in existing_columns:
            cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN Date TEXT")
            conn.commit()
        if 'Photo_Path' not in existing_columns:
            cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN Photo_Path TEXT")
            conn.commit()
        if 'Latitude' not in existing_columns:
            cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN Latitude REAL")
            conn.commit()
        if 'Longitude' not in existing_columns:
            cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN Longitude REAL")
            conn.commit()
        if 'State' not in existing_columns:
            cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN State TEXT DEFAULT 'Unknown'")
            conn.commit()
        
        conn.commit()

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    st.session_state.db_initialized = True

def load_attendance_data_from_db():
    """Loads all attendance data from the database into a Pandas DataFrame."""
    with get_db_connection() as conn:
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        if 'State' not in df.columns:
            df['State'] = 'Unknown'
        df['State'] = df['State'].fillna('Unknown')
        return df

def mark_attendance(person, person_type, status, photo_uploaded_indicator, photo_file_path, lat, lon, state):
    """Marks attendance. Relies on DB constraint for uniqueness."""
    india_timezone = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(india_timezone)
    timestamp_str = current_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')
    date_str = current_time.strftime('%Y-%m-%d')

    with get_db_connection() as conn:
        try:
            conn.execute(f'''
                INSERT INTO {TABLE_NAME} (Timestamp, Date, Person, Type, Status, Photo_Uploaded, Photo_Path, Latitude, Longitude, State)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp_str, date_str, person, person_type, status,
                photo_uploaded_indicator, photo_file_path, lat, lon, state
            ))
            conn.commit()
            st.success(f"Attendance marked for **{person}** as **{status}**.")
            return True
        except sqlite3.IntegrityError:
            st.warning(f"Attendance already marked today for **{person}**.")
            return False
        except Exception as e:
            st.error(f"Error marking attendance: {e}")
            return False

# --- UI Rendering Functions ---

def render_attendance_form():
    """Renders the main form for marking attendance."""
    with st.form("attendance_form", clear_on_submit=True):
        st.header("Mark Your Attendance")
        
        states = sorted(list(set([worker["state"] for worker in ALL_FIELD_WORKERS])))
        selected_state = st.selectbox("Select your State:", options=states)

        filtered_persons = [worker for worker in ALL_FIELD_WORKERS if worker["state"] == selected_state]
        person_names = sorted([worker["name"] for worker in filtered_persons])
        selected_person = st.selectbox("Select your name:", options=person_names)
        
        person_type = NAME_TO_ROLE_MAP.get(selected_person, "Unknown")
        person_state = NAME_TO_STATE_MAP.get(selected_person, "Unknown")
        st.info(f"**Role:** {person_type} | **State:** {person_state}")

        attendance_status = st.radio("Select attendance status:", options=ATTENDANCE_STATUSES, horizontal=True)

        uploaded_photo = st.file_uploader(
            "Upload a photo (optional for verification):",
            type=["jpg", "jpeg", "png"]
        )
        
        submitted = st.form_submit_button("Submit Attendance", use_container_width=True)

    if submitted:
        photo_uploaded_indicator = "No Photo"
        photo_file_path = None
        if uploaded_photo is not None:
            unique_filename = f"{uuid.uuid4()}_{uploaded_photo.name}"
            photo_file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            try:
                with open(photo_file_path, "wb") as f:
                    f.write(uploaded_photo.getbuffer())
                photo_uploaded_indicator = "Photo Uploaded"
                st.image(uploaded_photo, caption="Uploaded Photo", width=150)
            except Exception as e:
                st.error(f"Error saving photo: {e}")
                photo_file_path = None
                photo_uploaded_indicator = "Photo Upload Failed"

        if selected_person:
            success = mark_attendance(
                selected_person, person_type, attendance_status,
                photo_uploaded_indicator, photo_file_path, None, None, person_state
            )
            if success:
                st.session_state.attendance_df = load_attendance_data_from_db()
                st.rerun()
        else:
            st.error("Please select your name to mark attendance.")

def render_records_viewer():
    """Renders the UI for viewing, filtering, and downloading records."""
    st.header("View Attendance Records")
    df = st.session_state.get('attendance_df', pd.DataFrame())

    if df.empty:
        st.info("No attendance records found yet.")
        return

    st.subheader("Filter Records")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        min_date_available = df['Timestamp'].dropna().min().date() if not df['Timestamp'].dropna().empty else datetime.now().date()
        default_start_date = max(min_date_available, (datetime.now().date() - timedelta(days=30)))
        start_date = st.date_input("Start Date", value=default_start_date)
    with col2:
        max_date_available = df['Timestamp'].dropna().max().date() if not df['Timestamp'].dropna().empty else datetime.now().date()
        end_date = st.date_input("End Date", value=max_date_available)
    with col3:
        all_persons_filter = sorted(df['Person'].unique())
        selected_persons_filter = st.multiselect("Filter by Person(s):", options=all_persons_filter, default=all_persons_filter)
    with col4:
        all_states_filter = sorted(df['State'].unique())
        selected_states_filter = st.multiselect("Filter by State(s):", options=all_states_filter, default=all_states_filter)

    filtered_df = df[
        (df['Timestamp'].dt.date >= start_date) &
        (df['Timestamp'].dt.date <= end_date) &
        (df['Person'].isin(selected_persons_filter)) &
        (df['State'].isin(selected_states_filter))
    ].copy()

    st.markdown("### Filtered Attendance Data")
    st.dataframe(filtered_df.sort_values(by="Timestamp", ascending=False), use_container_width=True)

    if not filtered_df.empty:
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv_data,
            file_name=f"attendance_{start_date}_to_{end_date}.csv",
            mime="text/csv"
        )

        records_with_photos = filtered_df[filtered_df['Photo_Path'].notna() & (filtered_df['Photo_Path'] != '')]
        if not records_with_photos.empty:
            photo_paths_to_zip = [path for path in records_with_photos['Photo_Path'].tolist() if os.path.exists(path)]
            if photo_paths_to_zip:
                zip_file_bytes = create_zip_of_photos(photo_paths_to_zip) 
                
                st.download_button(
                    label="Download Filtered Photos as ZIP",
                    data=zip_file_bytes,
                    file_name=f"photos_{start_date}_to_{end_date}.zip",
                    mime="application/zip",
                )

# --- Main App Execution ---

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(layout="wide", page_title="Field Staff Attendance")
    st.title("👨‍🌾 Field Staff Attendance App")
    st.markdown("---")

    if 'db_initialized' not in st.session_state:
        init_db()
    
    if 'attendance_df' not in st.session_state:
        st.session_state.attendance_df = load_attendance_data_from_db()
    
    tab1, tab2 = st.tabs(["Mark Attendance", "View Records"])

    with tab1:
        render_attendance_form()

    with tab2:
        render_records_viewer()

if __name__ == "__main__":
    main()
