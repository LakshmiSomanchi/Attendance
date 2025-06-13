# --- sqlite_attendance_app.py ---

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from io import BytesIO
import pytz # For accurate timezones

# --- Database Configuration ---
DB_PATH = "attendance.db"
TABLE_NAME = "attendance"

# --- Field Worker Data ---
# Customize this list with your actual FA and CRP names.
# This list will be used to populate the dropdown for selecting a person.
ALL_FIELD_WORKERS = [
    {"name": "Anil Kumar", "role": "FA"},
    {"name": "Bina Devi", "role": "FA"},
    {"name": "Chandan Singh", "role": "CRP"},
    {"name": "Deepa Sharma", "role": "FA"},
    {"name": "Esha Gupta", "role": "CRP"},
    {"name": "Faisal Khan", "role": "FA"},
    {"name": "Gita Rani", "role": "CRP"},
    {"name": "Harish Verma", "role": "FA"},
    {"name": "Indira Prasad", "role": "CRP"},
    {"name": "Jatin Kumar", "role": "FA"},
    {"name": "Kavita Mishra", "role": "CRP"},
    {"name": "Lalit Sharma", "role": "FA"},
    {"name": "Mona Patel", "role": "CRP"},
    {"name": "Naveen Reddy", "role": "FA"},
    {"name": "Om Prakash", "role": "CRP"},
    {"name": "Pooja Devi", "role": "FA"},
    {"name": "Qasim Ahmed", "role": "CRP"},
    {"name": "Ramesh Singh", "role": "FA"},
    {"name": "Seema Yadav", "role": "CRP"},
    {"name": "Tarun Joshi", "role": "FA"},
    {"name": "Urmila Devi", "role": "CRP"},
    {"name": "Vivek Mehta", "role": "FA"},
    {"name": "Arti Rao", "role": "CRP"},
    {"name": "Bhavesh Desai", "role": "FA"},
    {"name": "Chetna Sharma", "role": "CRP"},
]

# Create a mapping from name to role for easy lookup
NAME_TO_ROLE_MAP = {worker["name"]: worker["role"] for worker in ALL_FIELD_WORKERS}


# --- Database Functions ---
def init_db():
    """Initializes the SQLite database table if it doesn't exist."""
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
    st.session_state.db_initialized = True # Use session state to prevent re-initializing on every rerun


@st.cache_data(ttl=60) # Cache data for 60 seconds to improve performance
def load_attendance_data():
    """Loads all attendance data from the database into a Pandas DataFrame."""
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
        # Convert Timestamp column to datetime objects for easier manipulation
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        return df

def mark_attendance(person, person_type, status, photo_uploaded_indicator, lat=None, lon=None):
    """
    Marks attendance for a person, checking if they've already marked today.
    photo_uploaded_indicator will be a string 'Yes' or 'No'.
    """
    # Clear cache to ensure fresh data is loaded after marking attendance
    st.cache_data.clear()
    df = load_attendance_data()
    today_str = datetime.now().strftime('%Y-%m-%d')

    # Check if attendance is already marked for today for this person
    if not df[(df['Timestamp'].dt.strftime('%Y-%m-%d') == today_str) & (df['Person'] == person)].empty:
        st.warning(f"Attendance already marked today for {person}.")
        return False

    # Get current time in India timezone
    india_timezone = pytz.timezone('Asia/Kolkata')
    current_time_in_india = datetime.now(india_timezone)
    timestamp_str = current_time_in_india.strftime('%Y-%m-%d %H:%M:%S %Z%z')

    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute(f'''
                INSERT INTO {TABLE_NAME} (Timestamp, Person, Type, Status, Photo_Uploaded, Latitude, Longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp_str, # Use the timezone-aware timestamp
                person,
                person_type,
                status,
                photo_uploaded_indicator, # 'Yes' or 'No' based on photo input
                lat,
                lon
            ))
            conn.commit()
            st.success(f"Attendance marked for {person} as {status}.")
            st.cache_data.clear() # Clear cache again after successful insert
            return True
        except Exception as e:
            st.error(f"Error marking attendance: {e}")
            return False

def update_record(record_id, fields: dict):
    """Updates an existing attendance record by ID."""
    try:
        set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(f"UPDATE {TABLE_NAME} SET {set_clause} WHERE id = ?", list(fields.values()) + [record_id])
            conn.commit()
            st.success(f"Record {record_id} updated successfully.")
            st.cache_data.clear() # Clear cache after update
            return True
    except Exception as e:
        st.error(f"Error updating record {record_id}: {e}")
        return False

def delete_record(record_id):
    """Deletes an attendance record by ID."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (record_id,))
            conn.commit()
            st.success(f"Record {record_id} deleted successfully.")
            st.cache_data.clear() # Clear cache after delete
            return True
    except Exception as e:
        st.error(f"Error deleting record {record_id}: {e}")
        return False

@st.cache_data
def convert_df_to_excel_bytes(df):
    """Converts a Pandas DataFrame to an Excel byte stream for download."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()


# --- Streamlit App Layout ---
st.set_page_config(layout="centered", page_title="Field Worker Attendance")

# Initialize database only once
if 'db_initialized' not in st.session_state:
    init_db()

st.title("👨‍🌾 Field Worker Attendance Tracker")
st.markdown("---")

# --- Attendance Marking Section ---
st.header("Mark Your Attendance")

# Dropdown for names
person_names = sorted([worker["name"] for worker in ALL_FIELD_WORKERS])
selected_person = st.selectbox(
    "Select your name:",
    options=person_names,
    index=0 # Default to the first name
)

# Automatically display the role based on selected person
if selected_person:
    person_type = NAME_TO_ROLE_MAP.get(selected_person, "Unknown")
    st.info(f"**Role:** {person_type}")
else:
    person_type = "Unknown"

# Geolocation Input
# NOTE: For a real web app with automatic geolocation, you would need
# to use JavaScript on the frontend to capture GPS coordinates and send
# them to the Streamlit backend (e.g., via Streamlit Components or a custom solution).
# For this local setup, we use a manual input.
geolocation_input = st.text_input(
    "Enter your current geolocation (e.g., Latitude, Longitude or Address):",
    placeholder="e.g., 18.5204, 73.8567 (Pune, India)"
)
latitude = None
longitude = None
if geolocation_input:
    try:
        # Attempt to parse as Lat, Lon
        parts = geolocation_input.replace(" ", "").split(',')
        if len(parts) == 2:
            latitude = float(parts[0])
            longitude = float(parts[1])
    except ValueError:
        st.warning("Please enter geolocation as 'Latitude, Longitude' or descriptive text.")
        latitude = None
        longitude = None


# Photo Upload
# NOTE: The actual photo file is NOT stored in the SQLite database due to size limitations.
# For persistent storage of photos, you would typically save them to a designated
# folder on your server or to cloud storage (e.g., AWS S3, Google Cloud Storage)
# and store the file path/URL in the database.
uploaded_photo = st.file_uploader(
    "Upload a photo (optional for verification):",
    type=["jpg", "jpeg", "png"],
    help="Upload a selfie or a photo of your field activity."
)

photo_uploaded_indicator = "No Photo"
if uploaded_photo is not None:
    # For now, just indicate that a photo was uploaded.
    # In a real app, you'd save the uploaded_photo.read() bytes to a file.
    photo_uploaded_indicator = "Photo Uploaded"
    st.success("Photo uploaded successfully!")
    st.image(uploaded_photo, caption="Uploaded Photo", width=150)


# Attendance Status Radio Buttons
attendance_status = st.radio(
    "Select attendance status:",
    options=["Present", "On Leave", "Absent"],
    index=0 # Default to 'Present'
)

# Submit Button
if st.button("Submit Attendance"):
    if selected_person:
        mark_attendance(selected_person, person_type, attendance_status, photo_uploaded_indicator, latitude, longitude)
    else:
        st.error("Please select your name to mark attendance.")

st.markdown("---")

# --- View Attendance Records Section ---
st.header("View Attendance Records")

df_attendance = load_attendance_data()

if not df_attendance.empty:
    st.subheader("Filter Records")
    col1, col2, col3 = st.columns(3)

    # Filter by date
    with col1:
        start_date = st.date_input("Start Date", value=df_attendance['Timestamp'].min().date())
    with col2:
        end_date = st.date_input("End Date", value=df_attendance['Timestamp'].max().date())
    with col3:
        # Filter by person
        all_persons = sorted(df_attendance['Person'].unique())
        selected_persons_filter = st.multiselect("Filter by Person(s):", options=all_persons, default=all_persons)

    # Apply filters
    filtered_df = df_attendance[
        (df_attendance['Timestamp'].dt.date >= start_date) &
        (df_attendance['Timestamp'].dt.date <= end_date) &
        (df_attendance['Person'].isin(selected_persons_filter))
    ]

    st.dataframe(filtered_df.sort_values(by="Timestamp", ascending=False), use_container_width=True)

    # Download button for Excel
    excel_data = convert_df_to_excel_bytes(filtered_df)
    st.download_button(
        label="Download Attendance as Excel",
        data=excel_data,
        file_name="attendance_records.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.markdown("---")

    # --- Manage Records Section (Update/Delete) ---
    st.header("Manage Records (Admin Only)")
    st.write("Enter the ID of the record you wish to update or delete.")

    record_ids = df_attendance['id'].tolist()
    if record_ids:
        selected_record_id = st.selectbox("Select Record ID:", options=record_ids)

        if selected_record_id:
            record_to_edit = df_attendance[df_attendance['id'] == selected_record_id].iloc[0]
            st.write(f"**Editing Record ID:** {record_to_edit['id']}")

            # Display current values for editing
            edit_person = st.text_input("Person:", value=record_to_edit['Person'], key=f"edit_person_{selected_record_id}")
            edit_type = st.selectbox("Type:", options=["FA", "CRP", "Unknown"], index=["FA", "CRP", "Unknown"].index(record_to_edit['Type']) if record_to_edit['Type'] in ["FA", "CRP", "Unknown"] else 2, key=f"edit_type_{selected_record_id}")
            edit_status = st.selectbox("Status:", options=["Present", "On Leave", "Absent"], index=["Present", "On Leave", "Absent"].index(record_to_edit['Status']) if record_to_edit['Status'] in ["Present", "On Leave", "Absent"] else 0, key=f"edit_status_{selected_record_id}")
            edit_photo_uploaded = st.selectbox("Photo Uploaded:", options=["Yes", "No", "Photo Uploaded", "No Photo"], index=["Yes", "No", "Photo Uploaded", "No Photo"].index(record_to_edit['Photo_Uploaded']) if record_to_edit['Photo_Uploaded'] in ["Yes", "No", "Photo Uploaded", "No Photo"] else 1, key=f"edit_photo_{selected_record_id}")
            edit_lat = st.number_input("Latitude:", value=float(record_to_edit['Latitude']) if pd.notna(record_to_edit['Latitude']) else 0.0, format="%.6f", key=f"edit_lat_{selected_record_id}")
            edit_lon = st.number_input("Longitude:", value=float(record_to_edit['Longitude']) if pd.notna(record_to_edit['Longitude']) else 0.0, format="%.6f", key=f"edit_lon_{selected_record_id}")

            col_u1, col_u2 = st.columns(2)
            with col_u1:
                if st.button(f"Update Record {selected_record_id}"):
                    fields_to_update = {
                        "Person": edit_person,
                        "Type": edit_type,
                        "Status": edit_status,
                        "Photo_Uploaded": edit_photo_uploaded,
                        "Latitude": edit_lat,
                        "Longitude": edit_lon
                    }
                    update_record(selected_record_id, fields_to_update)
            with col_u2:
                if st.button(f"Delete Record {selected_record_id}"):
                    delete_record(selected_record_id)
    else:
        st.info("No records to manage yet.")

else:
    st.info("No attendance records found. Mark attendance to see them here.")
