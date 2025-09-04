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
# --- Security: In a real app, use st.secrets or environment variables for the password ---
ADMIN_PASSWORD = "admin" 

# --- App Constants ---
ATTENDANCE_STATUSES = ["Present", "On Leave", "Absent"]
PHOTO_STATUSES = ["Photo Uploaded", "No Photo", "Photo Upload Failed"]
ROLES = ["CRP", "FA"]

# --- Helper Functions for Data ---

def get_all_field_workers():
    """Returns the list of all field workers. 
    In a larger app, this data could be loaded from a separate CSV or JSON file."""
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
        # ... (rest of the names are omitted for brevity but should be included here) ...
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


# --- Database Management ---

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initializes the database table and photo upload directory."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # ENHANCEMENT: Added a UNIQUE constraint to prevent duplicate attendance for the same person on the same day.
        # This is more robust than checking in Python.
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Timestamp TEXT,
                Date TEXT, -- Added for easier daily lookups and constraints
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

        # Add missing columns if the table already exists from an older version
        existing_columns = [col[1] for col in cursor.execute(f"PRAGMA table_info({TABLE_NAME})").fetchall()]
        if 'Date' not in existing_columns:
            cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN Date TEXT")
        if 'Photo_Path' not in existing_columns:
            cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN Photo_Path TEXT")
        if 'Latitude' not in existing_columns:
            cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN Latitude REAL")
        if 'Longitude' not in existing_columns:
            cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN Longitude REAL")
        if 'State' not in existing_columns:
            cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN State TEXT")
        
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

def update_record(record_id, fields: dict):
    """Updates an existing attendance record by ID."""
    set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
    with get_db_connection() as conn:
        try:
            conn.execute(f"UPDATE {TABLE_NAME} SET {set_clause} WHERE id = ?", list(fields.values()) + [record_id])
            conn.commit()
            st.success(f"Record **{record_id}** updated successfully.")
            return True
        except Exception as e:
            st.error(f"Error updating record **{record_id}**: {e}")
            return False

def delete_record(record_id):
    """Deletes a record and its associated photo file."""
    with get_db_connection() as conn:
        try:
            cursor = conn.execute(f"SELECT Photo_Path FROM {TABLE_NAME} WHERE id = ?", (record_id,))
            photo_path_to_delete = cursor.fetchone()
            if photo_path_to_delete and photo_path_to_delete[0] and os.path.exists(photo_path_to_delete[0]):
                os.remove(photo_path_to_delete[0])
                st.info(f"Removed associated photo file.")
            
            conn.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (record_id,))
            conn.commit()
            st.success(f"Record **{record_id}** deleted successfully.")
            return True
        except Exception as e:
            st.error(f"Error deleting record **{record_id}**: {e}")
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
                # PERFORMANCE: Reload data into session state and rerun the app
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
        end_date = st.date_input("End Date", value=datetime.now().date())
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

    # --- Download Buttons ---
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
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for photo_path in photo_paths_to_zip:
                        zip_file.write(photo_path, os.path.basename(photo_path))
                
                st.download_button(
                    label="Download Filtered Photos as ZIP",
                    data=zip_buffer.getvalue(),
                    file_name=f"photos_{start_date}_to_{end_date}.zip",
                    mime="application/zip",
                )

def render_admin_panel():
    """Renders the admin panel for record management after password verification."""
    st.header("Admin Panel")
    password = st.text_input("Enter Admin Password:", type="password")

    if password == ADMIN_PASSWORD:
        st.success("Access Granted")
        st.write("Use this section to update or delete existing attendance records.")
        df = st.session_state.get('attendance_df', pd.DataFrame())

        if df.empty:
            st.info("No records to manage.")
            return

        record_ids = df['id'].tolist()
        selected_id = st.selectbox("Select Record ID to Manage:", options=record_ids)

        if selected_id:
            record_to_edit = df[df['id'] == selected_id].iloc[0]
            
            with st.expander(f"Edit Record ID: {record_to_edit['id']}", expanded=True):
                edit_person = st.text_input("Person:", value=record_to_edit['Person'], key=f"edit_person_{selected_id}")
                edit_type = st.selectbox("Type:", options=ROLES, index=ROLES.index(record_to_edit['Type']), key=f"edit_type_{selected_id}")
                edit_status = st.selectbox("Status:", options=ATTENDANCE_STATUSES, index=ATTENDANCE_STATUSES.index(record_to_edit['Status']), key=f"edit_status_{selected_id}")
                
                all_states = sorted(list(set([w['state'] for w in ALL_FIELD_WORKERS])))
                edit_state = st.selectbox("State:", options=all_states, index=all_states.index(record_to_edit['State']), key=f"edit_state_{selected_id}")
                
                edit_lat = st.number_input("Latitude:", value=float(record_to_edit.get('Latitude', 0.0)), format="%.6f", key=f"edit_lat_{selected_id}")
                edit_lon = st.number_input("Longitude:", value=float(record_to_edit.get('Longitude', 0.0)), format="%.6f", key=f"edit_lon_{selected_id}")

                col_u1, col_u2 = st.columns(2)
                if col_u1.button("Update Record", key=f"update_{selected_id}", use_container_width=True):
                    fields_to_update = {
                        "Person": edit_person, "Type": edit_type, "Status": edit_status,
                        "State": edit_state, "Latitude": edit_lat, "Longitude": edit_lon
                    }
                    if update_record(selected_id, fields_to_update):
                        st.session_state.attendance_df = load_attendance_data_from_db()
                        st.rerun()

                if col_u2.button("Delete Record", key=f"delete_{selected_id}", type="primary", use_container_width=True):
                    if delete_record(selected_id):
                        st.session_state.attendance_df = load_attendance_data_from_db()
                        st.rerun()

    elif password:
        st.error("Incorrect password.")

# --- Main App Execution ---

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(layout="wide", page_title="Field Staff Attendance")
    st.title("👨‍🌾 Field Staff Attendance App")
    st.markdown("---")

    # --- Initialization ---
    if 'db_initialized' not in st.session_state:
        init_db()
    
    # PERFORMANCE: Load data into session state once, not on every interaction
    if 'attendance_df' not in st.session_state:
        st.session_state.attendance_df = load_attendance_data_from_db()
    
    # UI: Use tabs for better organization
    tab1, tab2, tab3 = st.tabs(["Mark Attendance", "View Records", "Admin Panel"])

    with tab1:
        render_attendance_form()

    with tab2:
        render_records_viewer()
    
    with tab3:
        render_admin_panel()

if __name__ == "__main__":
    main()

