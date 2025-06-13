import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from io import BytesIO
import pytz # For accurate timezones
import os # For file system operations
import uuid # For generating unique filenames

# --- Database Configuration ---
DB_PATH = "attendance.db"
TABLE_NAME = "attendance"
UPLOAD_FOLDER = "uploaded_photos" # Directory to save uploaded photos

# --- Field Worker Data ---
# Customizing this list with your actual FA and CRP names.
# This list will be used to populate the dropdown for selecting a person.
ALL_FIELD_WORKERS = [
    # CRP Names
    {"name": "Dhananjay Dewar", "role": "CRP"},
    {"name": "Mahendra Tayde", "role": "CRP"},
    {"name": "Shrihari Sontakke", "role": "CRP"},
    {"name": "Roshan Ingle", "role": "CRP"},
    {"name": "Nikhil Dhenge", "role": "CRP"},
    {"name": "Pradip Gawande", "role": "CRP"},
    {"name": "Manoj Thakre", "role": "CRP"},
    {"name": "Amol Bute", "role": "CRP"},
    {"name": "Dhananjay Gawande", "role": "CRP"},
    {"name": "Pawan Ingle", "role": "CRP"},
    {"name": "Amardip Bunde", "role": "CRP"},
    {"name": "Gopal Tarale", "role": "CRP"},
    {"name": "Shital Jalmakar", "role": "CRP"},
    {"name": "Prabhakar Wankhade", "role": "CRP"},
    {"name": "Bhagyashri Ghawat", "role": "CRP"},
    {"name": "Rangpara Shailesh", "role": "CRP"},
    {"name": "Olakiya Ramesh", "role": "CRP"},
    {"name": "Paraliya Akash", "role": "CRP"},
    {"name": "Chauhan Ajay", "role": "CRP"},
    {"name": "Bavliya Umesh", "role": "CRP"},
    {"name": "Parmar Asmita", "role": "CRP"},
    {"name": "Malkiya Amit", "role": "CRP"},
    {"name": "Malkiya Pravin", "role": "CRP"},
    {"name": "Rathod Rohit", "role": "CRP"},
    {"name": "Chauhan Vijay", "role": "CRP"},
    {"name": "Malkiya Yash", "role": "CRP"},
    {"name": "Khetariya Ravat", "role": "CRP"},
    {"name": "Olakiya Vaishali", "role": "CRP"},
    {"name": "Vaghela Hasubhai", "role": "CRP"},
    {"name": "Vaghela Bavnaben", "role": "CRP"},
    {"name": "Sarvaiya Kinjalben", "role": "CRP"},
    {"name": "Dumadiya Vipul", "role": "CRP"},
    {"name": "Jograjiya Chatur", "role": "CRP"},
    {"name": "Luni Hiruben", "role": "CRP"},
    {"name": "Kalotara Hirabhai", "role": "CRP"},
    {"name": "Malkiya Hitesh", "role": "CRP"},
    {"name": "Zampadiya Vijay", "role": "CRP"},
    {"name": "Rangapara Arvindbhai", "role": "CRP"},
    {"name": "Mkavana Sanjay", "role": "CRP"},
    {"name": "Degama Vishal", "role": "CRP"},
    {"name": "Mer Parth", "role": "CRP"},
    {"name": "Shiyaliya Vijay", "role": "CRP"},
    {"name": "Meniya Mahesh", "role": "CRP"},
    {"name": "Dholakiya Manji", "role": "CRP"},
    {"name": "Kahmani Navghan", "role": "CRP"},
    {"name": "Dhoriya Rahul", "role": "CRP"},
    {"name": "Dabhi Vasharam", "role": "CRP"},
    {"name": "Dharajiya Mukesh", "role": "CRP"},
    {"name": "Dharajiya Mehul", "role": "CRP"},
    {"name": "Dabhi Ashok", "role": "CRP"},
    {"name": "Bhusadiya Ajay", "role": "CRP"},
    {"name": "Goriya Chhagan", "role": "CRP"},
    {"name": "Dhoriya Kartik", "role": "CRP"},
    {"name": "Rathod Dinesh", "role": "CRP"},
    {"name": "Sitapara Sanjay", "role": "CRP"},
    {"name": "Vaghela Shailesh", "role": "CRP"},
    {"name": "Hadani Vishal", "role": "CRP"},
    {"name": "Rajapara Bhavesh", "role": "CRP"},
    {"name": "Chavda Jayesh", "role": "CRP"},
    {"name": "Lalabhai Sambad", "role": "CRP"},
    {"name": "Paramar Abhijit", "role": "CRP"},
    {"name": "Makvana Vijay", "role": "CRP"},
    {"name": "Sambad Sanjay", "role": "CRP"},
    {"name": "Malakiya Akshay", "role": "CRP"},
    {"name": "Sakariya Gopal", "role": "CRP"},
    {"name": "Jograjiya Haresh", "role": "CRP"},
    {"name": "Kansagara Lalji", "role": "CRP"},
    {"name": "Rathod Hirabhai", "role": "CRP"},
    {"name": "Rathod Vishal", "role": "CRP"},
    {"name": "Sambad Jethabhai", "role": "CRP"},
    {"name": "Borasaniya Jayraj", "role": "CRP"},
    {"name": "Aal Rohit", "role": "CRP"},
    {"name": "Zapadiya Hareshbhai", "role": "CRP"},
    {"name": "Khatana Gelabhai", "role": "CRP"},
    {"name": "Rabari Ramabhai", "role": "CRP"},
    {"name": "Meghwal Jyotshanaben", "role": "CRP"},
    {"name": "Vidiya Aratiben", "role": "CRP"},
    {"name": "Chavan Jaypal", "role": "CRP"},
    {"name": "Chavda Valabhai", "role": "CRP"},
    {"name": "Makwana Ramesh", "role": "CRP"},
    {"name": "Parmar Rajesh", "role": "CRP"},
    # FA Names
    {"name": "Rajan Patel", "role": "FA"},
    {"name": "Pedhadiya Dharmesh", "role": "FA"},
    {"name": "Maradiya Bhavna", "role": "FA"},
    {"name": "Khokhar Kishan", "role": "FA"},
    {"name": "Olakiya Kinjal", "role": "FA"},
    {"name": "Dabhi Divya", "role": "FA"},
    {"name": "Solanki Dharmedrabhai", "role": "FA"},
    {"name": "Dabhi Hemangi", "role": "FA"},
    {"name": "Simral Kilnake", "role": "FA"},
    {"name": "Shrikant Bajare", "role": "FA"},
]

# Create a mapping from name to role for easy lookup
NAME_TO_ROLE_MAP = {worker["name"]: worker["role"] for worker in ALL_FIELD_WORKERS}


# --- Database Functions ---
def init_db():
    """Initializes the SQLite database table if it doesn't exist and creates photo upload directory."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Timestamp TEXT,
                Person TEXT,
                Type TEXT,
                Status TEXT,
                Photo_Uploaded TEXT,
                Photo_Path TEXT,            -- New column for photo file path
                Latitude REAL,              -- Kept for potential future use or manual entry
                Longitude REAL              -- Kept for potential future or manual entry
            )
        ''')
    # Ensure the upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    st.session_state.db_initialized = True # Use session state to prevent re-initializing on every rerun


@st.cache_data(ttl=60) # Cache data for 60 seconds to improve performance
def load_attendance_data():
    """Loads all attendance data from the database into a Pandas DataFrame."""
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
        # Convert Timestamp column to datetime objects for easier manipulation
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        return df

def mark_attendance(person, person_type, status, photo_uploaded_indicator, photo_file_path, lat=None, lon=None):
    """
    Marks attendance for a person, checking if they've already marked today.
    photo_uploaded_indicator will be 'Yes' or 'No'.
    photo_file_path will be the path to the saved photo file or None.
    """
    # Clear cache to ensure fresh data is loaded after marking attendance
    st.cache_data.clear()
    df = load_attendance_data()
    today_str = datetime.now().strftime('%Y-%m-%d')

    # Check if attendance is already marked for today for this person
    if not df[(df['Timestamp'].dt.strftime('%Y-%m-%d') == today_str) & (df['Person'] == person)].empty:
        st.warning(f"Attendance already marked today for {person}.")
        return False

    # Get current time in India timezone (Automatic Timestamp)
    india_timezone = pytz.timezone('Asia/Kolkata')
    current_time_in_india = datetime.now(india_timezone)
    timestamp_str = current_time_in_india.strftime('%Y-%m-%d %H:%M:%S %Z%z')

    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute(f'''
                INSERT INTO {TABLE_NAME} (Timestamp, Person, Type, Status, Photo_Uploaded, Photo_Path, Latitude, Longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp_str, # Use the timezone-aware timestamp
                person,
                person_type,
                status,
                photo_uploaded_indicator, # 'Yes' or 'No' based on photo input
                photo_file_path,          # Store the path to the saved photo
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
    """Deletes an attendance record by ID and removes associated photo file if it exists."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # First, retrieve the photo path to delete the file
            cursor = conn.execute(f"SELECT Photo_Path FROM {TABLE_NAME} WHERE id = ?", (record_id,))
            photo_path_to_delete = cursor.fetchone()
            if photo_path_to_delete and photo_path_to_delete[0]:
                full_path = photo_path_to_delete[0]
                if os.path.exists(full_path):
                    os.remove(full_path)
                    st.info(f"Removed photo file: {full_path}")
            
            # Then, delete the record from the database
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

# --- Run DB init on load ---
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

st.markdown("---")
st.subheader("Timestamp Details")
st.info("The **Timestamp** will be automatically recorded when you submit your attendance.")


# Photo Upload
uploaded_photo = st.file_uploader(
    "Upload a photo (optional for verification):",
    type=["jpg", "jpeg", "png"],
    help="Upload a selfie or a photo of your field activity."
)

photo_uploaded_indicator = "No Photo"
photo_file_path = None # Initialize photo_file_path

if uploaded_photo is not None:
    # Generate a unique filename
    unique_filename = f"{uuid.uuid4()}_{uploaded_photo.name}"
    # Define the full path where the file will be saved
    photo_file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    # Save the uploaded file to the designated folder
    try:
        with open(photo_file_path, "wb") as f:
            f.write(uploaded_photo.getbuffer())
        photo_uploaded_indicator = "Photo Uploaded"
        st.success("Photo uploaded successfully!")
        st.image(uploaded_photo, caption="Uploaded Photo", width=150)
    except Exception as e:
        st.error(f"Error saving photo: {e}")
        photo_file_path = None # Reset path if saving failed
        photo_uploaded_indicator = "Photo Upload Failed"


# Attendance Status Radio Buttons
attendance_status = st.radio(
    "Select attendance status:",
    options=["Present", "On Leave", "Absent"],
    index=0 # Default to 'Present'
)

# Submit Button
# lat and lon are passed as None, as they are not captured automatically in this setup
if st.button("Submit Attendance"):
    if selected_person:
        mark_attendance(selected_person, person_type, attendance_status, photo_uploaded_indicator, photo_file_path, None, None)
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
        start_date = st.date_input("Start Date", value=df_attendance['Timestamp'].min().date() if not df_attendance.empty else datetime.now().date())
    with col2:
        end_date = st.date_input("End Date", value=df_attendance['Timestamp'].max().date() if not df_attendance.empty else datetime.now().date())
    with col3:
        # Filter by person
        all_persons = sorted(df_attendance['Person'].unique())
        selected_persons_filter = st.multiselect("Filter by Person(s):", options=all_persons, default=all_persons)

    # Apply filters
    filtered_df = df_attendance[
        (df_attendance['Timestamp'].dt.date >= start_date) &
        (df_attendance['Timestamp'].dt.date <= end_date) &
        (df_attendance['Person'].isin(selected_persons_filter))
    ].copy() # Use .copy() to avoid SettingWithCopyWarning

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

    # --- Photo Download Section ---
    st.header("Download Individual Photos")
    
    # Filter records that have a photo uploaded
    records_with_photos = filtered_df[filtered_df['Photo_Path'].notna() & (filtered_df['Photo_Path'] != '')]

    if not records_with_photos.empty:
        photo_record_ids = records_with_photos['id'].tolist()
        selected_photo_record_id = st.selectbox(
            "Select a record ID to download its photo:",
            options=photo_record_ids,
            key="photo_download_selector"
        )

        if selected_photo_record_id:
            selected_photo_record = records_with_photos[records_with_photos['id'] == selected_photo_record_id].iloc[0]
            photo_path = selected_photo_record['Photo_Path']
            person_name = selected_photo_record['Person']

            if os.path.exists(photo_path):
                st.write(f"Photo for **{person_name}** (Record ID: {selected_photo_record_id}):")
                st.image(photo_path, caption=f"{person_name}'s photo from {selected_photo_record['Timestamp'].strftime('%Y-%m-%d')}", width=200)
                
                with open(photo_path, "rb") as file:
                    st.download_button(
                        label="Download Photo",
                        data=file.read(),
                        file_name=os.path.basename(photo_path),
                        mime="image/png" if photo_path.lower().endswith('.png') else "image/jpeg"
                    )
            else:
                st.warning(f"Photo file not found for Record ID {selected_photo_record_id} at {photo_path}. It might have been manually deleted from the server.")
    else:
        st.info("No records with uploaded photos found in the filtered data.")

    st.markdown("---")


    # --- Manage Records Section (Update/Delete) ---
    st.header("Manage Records (Admin Only)")
    st.write("Enter the ID of the record you wish to update or delete.")

    record_ids = df_attendance['id'].tolist()
    if record_ids:
        selected_record_id_manage = st.selectbox("Select Record ID:", options=record_ids, key="manage_record_selector")

        if selected_record_id_manage:
            record_to_edit = df_attendance[df_attendance['id'] == selected_record_id_manage].iloc[0]
            st.write(f"**Editing Record ID:** {record_to_edit['id']}")

            # Display current values for editing
            edit_person = st.text_input("Person:", value=record_to_edit['Person'], key=f"edit_person_{selected_record_id_manage}")
            edit_type = st.selectbox("Type:", options=["FA", "CRP", "Unknown"], index=["FA", "CRP", "Unknown"].index(record_to_edit['Type']) if record_to_edit['Type'] in ["FA", "CRP", "Unknown"] else 2, key=f"edit_type_{selected_record_id_manage}")
            edit_status = st.selectbox("Status:", options=["Present", "On Leave", "Absent"], index=["Present", "On Leave", "Absent"].index(record_to_edit['Status']) if record_to_edit['Status'] in ["Present", "On Leave", "Absent"] else 0, key=f"edit_status_{selected_record_id_manage}")
            edit_photo_uploaded = st.selectbox("Photo Uploaded Status:", options=["Yes", "No", "Photo Uploaded", "No Photo"], index=["Yes", "No", "Photo Uploaded", "No Photo"].index(record_to_edit['Photo_Uploaded']) if record_to_edit['Photo_Uploaded'] in ["Yes", "No", "Photo Uploaded", "No Photo"] else 1, key=f"edit_photo_status_{selected_record_id_manage}")
            
            # Display Photo_Path for reference, but not directly editable via file upload here
            st.text_input("Photo Path (for reference):", value=record_to_edit['Photo_Path'] if pd.notna(record_to_edit['Photo_Path']) else '', disabled=True, key=f"edit_photo_path_{selected_record_id_manage}")

            # Lat/Lon fields are still present for manual correction if needed, but not automatically filled
            edit_lat = st.number_input("Latitude:", value=float(record_to_edit['Latitude']) if pd.notna(record_to_edit['Latitude']) else 0.0, format="%.6f", key=f"edit_lat_{selected_record_id_manage}")
            edit_lon = st.number_input("Longitude:", value=float(record_to_edit['Longitude']) if pd.notna(record_to_edit['Longitude']) else 0.0, format="%.6f", key=f"edit_lon_{selected_record_id_manage}")

            col_u1, col_u2 = st.columns(2)
            with col_u1:
                if st.button(f"Update Record {selected_record_id_manage}"):
                    fields_to_update = {
                        "Person": edit_person,
                        "Type": edit_type,
                        "Status": edit_status,
                        "Photo_Uploaded": edit_photo_uploaded,
                        "Latitude": edit_lat,
                        "Longitude": edit_lon
                        # Photo_Path is not updated via this form as it's handled on upload
                    }
                    update_record(selected_record_id_manage, fields_to_update)
            with col_u2:
                if st.button(f"Delete Record {selected_record_id_manage}"):
                    delete_record(selected_record_id_manage)
    else:
        st.info("No records to manage yet.")

else:
    st.info("No attendance records found. Mark attendance to see them here.")
