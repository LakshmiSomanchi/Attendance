import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from io import BytesIO
import pytz 
import os 
import uuid 
import zipfile 


DB_PATH = "attendance.db"
TABLE_NAME = "attendance"
UPLOAD_FOLDER = "uploaded_photos" 

ALL_FIELD_WORKERS = [
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


NAME_TO_ROLE_MAP = {worker["name"]: worker["role"] for worker in ALL_FIELD_WORKERS}
NAME_TO_STATE_MAP = {worker["name"]: worker["state"] for worker in ALL_FIELD_WORKERS}



def init_db():
    """
    Initializes the SQLite database table if it doesn't exist.
    Also, adds missing columns (Photo_Path, Latitude, Longitude, State) if they are not present,
    and creates the photo upload directory.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Timestamp TEXT,
                Person TEXT,
                Type TEXT,
                Status TEXT,
                Photo_Uploaded TEXT,
                Photo_Path TEXT,
                Latitude REAL,
                Longitude REAL,
                State TEXT -- Added State column
            )
        ''')
        conn.commit()

        
        existing_columns = [col[1] for col in cursor.execute(f"PRAGMA table_info({TABLE_NAME})").fetchall()]

        if 'Photo_Path' not in existing_columns:
            cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN Photo_Path TEXT")
            conn.commit()
            st.info("Added 'Photo_Path' column to the database.")

        if 'Latitude' not in existing_columns:
            cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN Latitude REAL")
            conn.commit()
            st.info("Added 'Latitude' column to the database.")

        if 'Longitude' not in existing_columns:
            cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN Longitude REAL")
            conn.commit()
            st.info("Added 'Longitude' column to the database.")

        if 'State' not in existing_columns:
            
            cursor.execute(f"ALTER TABLE {TABLE_NAME} ADD COLUMN State TEXT DEFAULT 'Unknown'")
            conn.commit()
            st.info("Added 'State' column to the database and backfilled existing records with 'Unknown'.")

    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    st.session_state.db_initialized = True


@st.cache_data(ttl=60) 
def load_attendance_data():
    """Loads all attendance data from the database into a Pandas DataFrame."""
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
        
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        
        if 'State' not in df.columns:
            df['State'] = 'Unknown'
        df['State'] = df['State'].fillna('Unknown')
        return df

def mark_attendance(person, person_type, status, photo_uploaded_indicator, photo_file_path, lat, lon, state):
    """
    Marks attendance for a person, checking if they've already marked today.
    photo_uploaded_indicator will be 'Yes' or 'No'.
    photo_file_path will be the path to the saved photo file or None.
    """
    df = load_attendance_data()
    
    
    
    df_valid_timestamps = df.dropna(subset=['Timestamp'])
    today_str = datetime.now().strftime('%Y-%m-%d')

    
    if not df_valid_timestamps[(df_valid_timestamps['Timestamp'].dt.strftime('%Y-%m-%d') == today_str) & (df_valid_timestamps['Person'] == person)].empty:
        st.warning(f"Attendance already marked today for **{person}**.")
        return False

    
    india_timezone = pytz.timezone('Asia/Kolkata')
    current_time_in_india = datetime.now(india_timezone)
    timestamp_str = current_time_in_india.strftime('%Y-%m-%d %H:%M:%S %Z%z')

    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute(f'''
                INSERT INTO {TABLE_NAME} (Timestamp, Person, Type, Status, Photo_Uploaded, Photo_Path, Latitude, Longitude, State)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp_str, 
                person,
                person_type,
                status,
                photo_uploaded_indicator, 
                photo_file_path,          
                lat,
                lon,
                state 
            ))
            conn.commit()
            st.success(f"Attendance marked for **{person}** as **{status}**.")
            st.cache_data.clear() 
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
            st.success(f"Record **{record_id}** updated successfully.")
            st.cache_data.clear() 
            return True
    except Exception as e:
        st.error(f"Error updating record **{record_id}**: {e}")
        return False

def delete_record(record_id):
    """Deletes an attendance record by ID and removes associated photo file if it exists."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            
            cursor = conn.execute(f"SELECT Photo_Path FROM {TABLE_NAME} WHERE id = ?", (record_id,))
            photo_path_to_delete = cursor.fetchone()
            if photo_path_to_delete and photo_path_to_delete[0]:
                full_path = photo_path_to_delete[0]
                if os.path.exists(full_path):
                    os.remove(full_path)
                    st.info(f"Removed photo file: **{os.path.basename(full_path)}**")
            
            
            conn.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (record_id,))
            conn.commit()
            st.success(f"Record **{record_id}** deleted successfully.")
            st.cache_data.clear() 
            return True
    except Exception as e:
        st.error(f"Error deleting record **{record_id}**: {e}")
        return False

@st.cache_data
def convert_df_to_csv_bytes(df):
    """Converts a Pandas DataFrame to a CSV byte stream for download."""
    
    df_copy = df.copy() 
    for col in df_copy.columns:
        
        df_copy[col] = df_copy[col].apply(lambda x: str(x) if pd.notna(x) else '')
    return df_copy.to_csv(index=False).encode("utf-8")

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


st.set_page_config(layout="centered", page_title="Field Staff Attendance App")


if 'db_initialized' not in st.session_state:
    init_db()

st.title("👨‍🌾 Field Staff Attendance App")
st.markdown("---")


st.header("Mark Your Attendance")


states = sorted(list(set([worker["state"] for worker in ALL_FIELD_WORKERS])))
selected_state = st.selectbox(
    "Select your State:",
    options=states,
    index=0 if states else None 
)


filtered_persons = [worker for worker in ALL_FIELD_WORKERS if worker["state"] == selected_state]
person_names = sorted([worker["name"] for worker in filtered_persons])


selected_person = st.selectbox(
    "Select your name:",
    options=person_names,
    index=0 if person_names else None 
)


if selected_person:
    person_type = NAME_TO_ROLE_MAP.get(selected_person, "Unknown")
    person_state = NAME_TO_STATE_MAP.get(selected_person, "Unknown")
    st.info(f"**Role:** {person_type} | **State:** {person_state}")
else:
    person_type = "Unknown"
    person_state = "Unknown" 

st.markdown("---")
st.subheader("Timestamp Details")
st.info("The **Timestamp** will be automatically recorded when you submit your attendance.")



uploaded_photo = st.file_uploader(
    "Upload a photo (optional for verification):",
    type=["jpg", "jpeg", "png"],
    help="Upload a selfie or a photo of your field activity."
)

photo_uploaded_indicator = "No Photo"
photo_file_path = None 

if uploaded_photo is not None:
    
    unique_filename = f"{uuid.uuid4()}_{uploaded_photo.name}"
    
    photo_file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    
    try:
        with open(photo_file_path, "wb") as f:
            f.write(uploaded_photo.getbuffer())
        photo_uploaded_indicator = "Photo Uploaded"
        st.success("Photo uploaded successfully!")
        st.image(uploaded_photo, caption="Uploaded Photo", width=150)
    except Exception as e:
        st.error(f"Error saving photo: {e}")
        photo_file_path = None 
        photo_uploaded_indicator = "Photo Upload Failed"



attendance_status = st.radio(
    "Select attendance status:",
    options=["Present", "On Leave", "Absent"],
    index=0 
)


if st.button("Submit Attendance"):
    if selected_person:
        
        mark_attendance(selected_person, person_type, attendance_status, photo_uploaded_indicator, photo_file_path, None, None, person_state)
    else:
        st.error("Please select your name to mark attendance.")

st.markdown("---")


st.header("View Attendance Records")

df_attendance = load_attendance_data()

if not df_attendance.empty:
    st.subheader("Filter Records")
    col1, col2, col3, col4 = st.columns(4) 

    
    with col1:
        
        
        valid_timestamps = df_attendance['Timestamp'].dropna()
        min_date_available = valid_timestamps.min().date() if not valid_timestamps.empty else datetime.now().date()
        default_start_date = max(min_date_available, (datetime.now().date() - timedelta(days=30)))
        start_date = st.date_input("Start Date", value=default_start_date)
    with col2:
        
        max_date_available = valid_timestamps.max().date() if not valid_timestamps.empty else datetime.now().date()
        end_date = st.date_input("End Date", value=max_date_available)
    with col3:
        
        all_persons_filter = sorted(df_attendance['Person'].unique())
        
        selected_persons_filter = st.multiselect("Filter by Person(s):", options=all_persons_filter, default=all_persons_filter if all_persons_filter else [])
    with col4:
        
        all_states_filter = sorted(df_attendance['State'].unique())
        
        selected_states_filter = st.multiselect("Filter by State(s):", options=all_states_filter, default=all_states_filter if all_states_filter else [])


    
    
    filtered_df = df_attendance.dropna(subset=['Timestamp']).copy() 
    
    
    filtered_df = filtered_df[
        (filtered_df['Timestamp'].dt.date >= start_date) &
        (filtered_df['Timestamp'].dt.date <= end_date) &
        (filtered_df['Person'].isin(selected_persons_filter)) &
        (filtered_df['State'].isin(selected_states_filter))
    ].copy() 

    st.markdown("### Filtered Attendance Data")
    st.dataframe(filtered_df.sort_values(by="Timestamp", ascending=False), use_container_width=True)

    csv_data = convert_df_to_csv_bytes(filtered_df)
    st.download_button(
        label="Download Filtered Attendance Data as CSV",
        data=csv_data,
        file_name=f"attendance_records_{start_date}_to_{end_date}.csv",
        mime="text/csv"
    )

    st.markdown("---")

    
    st.header("Download Associated Photos")
    
    
    records_with_photos = filtered_df[filtered_df['Photo_Path'].notna() & (filtered_df['Photo_Path'] != '')]

    if not records_with_photos.empty:
        
        photo_paths_to_zip = [path for path in records_with_photos['Photo_Path'].tolist() if os.path.exists(path)]
        if photo_paths_to_zip:
            zip_file_bytes = create_zip_of_photos(photo_paths_to_zip)
            st.download_button(
                label="Download All Filtered Photos as ZIP",
                data=zip_file_bytes,
                file_name=f"filtered_photos_{start_date}_to_{end_date}.zip",
                mime="application/zip",
                help="Downloads all photos associated with the currently filtered attendance records."
            )
            st.markdown("---") 

        
        st.subheader("Download Individual Photo")
        
        photo_options = []
        for index, row in records_with_photos.iterrows():
            
            timestamp_str_for_label = row['Timestamp'].strftime('%Y-%m-%d %H:%M') if pd.notna(row['Timestamp']) else "Invalid Date"
            option_label = f"ID: {row['id']} - {row['Person']} ({timestamp_str_for_label})"
            photo_options.append({"id": row['id'], "label": option_label, "path": row['Photo_Path'], "person": row['Person'], "timestamp": row['Timestamp']})

        if photo_options:
            selected_photo_option = st.selectbox(
                "Select a record to view/download its photo:",
                options=photo_options,
                format_func=lambda x: x['label'],
                key="photo_download_selector"
            )

            if selected_photo_option:
                photo_path = selected_photo_option['path']
                person_name = selected_photo_option['person']
                record_timestamp = selected_photo_option['timestamp']
                record_id = selected_photo_option['id']

                if os.path.exists(photo_path):
                    
                    timestamp_display = record_timestamp.strftime('%Y-%m-%d %H:%M') if pd.notna(record_timestamp) else "Invalid Date"
                    st.write(f"Photo for **{person_name}** (Record ID: {record_id}, Date: {timestamp_display}):")
                    st.image(photo_path, caption=f"{person_name}'s photo from {timestamp_display}", width=300)
                    
                    with open(photo_path, "rb") as file:
                        st.download_button(
                            label="Download Photo",
                            data=file.read(),
                            file_name=os.path.basename(photo_path),
                            mime="image/png" if photo_path.lower().endswith('.png') else "image/jpeg",
                            key=f"download_single_photo_{record_id}"
                        )
                else:
                    st.warning(f"Photo file not found for Record ID {record_id} (Path: `{photo_path}`). It might have been manually deleted from the server.")
        else:
            st.info("No records with uploaded photos found in the filtered data that can be individually downloaded.")

    else:
        st.info("No records with uploaded photos found in the filtered data.")

    st.markdown("---")


    
    st.header("Manage Records (Admin Only)")
    st.write("Use this section to update or delete existing attendance records.")

    record_ids = df_attendance['id'].tolist()
    if record_ids:
        selected_record_id_manage = st.selectbox("Select Record ID:", options=record_ids, key="manage_record_selector")

        if selected_record_id_manage:
            record_to_edit = df_attendance[df_attendance['id'] == selected_record_id_manage].iloc[0]
            st.write(f"**Currently Editing Record ID:** {record_to_edit['id']}")

            
            edit_person = st.text_input("Person:", value=record_to_edit['Person'], key=f"edit_person_{selected_record_id_manage}")
            edit_type = st.selectbox("Type:", options=["FA", "CRP", "Unknown"], index=["FA", "CRP", "Unknown"].index(record_to_edit['Type']) if record_to_edit['Type'] in ["FA", "CRP", "Unknown"] else 2, key=f"edit_type_{selected_record_id_manage}")
            edit_status = st.selectbox("Status:", options=["Present", "On Leave", "Absent"], index=["Present", "On Leave", "Absent"].index(record_to_edit['Status']) if record_to_edit['Status'] in ["Present", "On Leave", "Absent"] else 0, key=f"edit_status_{selected_record_id_manage}")
            
            
            
            state_options_for_edit = sorted(list(set(states + ([record_to_edit['State']] if pd.notna(record_to_edit['State']) else ["Unknown"]))))
            edit_state = st.selectbox("State:", options=state_options_for_edit, index=state_options_for_edit.index(record_to_edit['State']) if pd.notna(record_to_edit['State']) and record_to_edit['State'] in state_options_for_edit else (len(state_options_for_edit) -1 if "Unknown" in state_options_for_edit else 0), key=f"edit_state_{selected_record_id_manage}")
            
            
            edit_photo_uploaded = st.selectbox(
                "Photo Uploaded Status:",
                options=["Photo Uploaded", "No Photo", "Photo Upload Failed"],
                index=["Photo Uploaded", "No Photo", "Photo Upload Failed"].index(record_to_edit['Photo_Uploaded']) if record_to_edit['Photo_Uploaded'] in ["Photo Uploaded", "No Photo", "Photo Upload Failed"] else 1,
                key=f"edit_photo_status_{selected_record_id_manage}"
            )
            
            
            st.text_input("Photo Path (for reference):", value=record_to_edit['Photo_Path'] if pd.notna(record_to_edit['Photo_Path']) else '', disabled=True, help="This path is for reference and cannot be directly edited here. To change a photo, you'd need to delete and re-submit the attendance.", key=f"edit_photo_path_{selected_record_id_manage}")

            
            edit_lat = st.number_input("Latitude:", value=float(record_to_edit['Latitude']) if pd.notna(record_to_edit['Latitude']) else 0.0, format="%.6f", key=f"edit_lat_{selected_record_id_manage}")
            edit_lon = st.number_input("Longitude:", value=float(record_to_edit['Longitude']) if pd.notna(record_to_edit['Longitude']) else 0.0, format="%.6f", key=f"edit_lon_{selected_record_id_manage}")

            col_u1, col_u2 = st.columns(2)
            with col_u1:
                if st.button(f"Update Record {selected_record_id_manage}", use_container_width=True):
                    fields_to_update = {
                        "Person": edit_person,
                        "Type": edit_type,
                        "Status": edit_status,
                        "Photo_Uploaded": edit_photo_uploaded,
                        "Latitude": edit_lat,
                        "Longitude": edit_lon,
                        "State": edit_state 
                    }
                    update_record(selected_record_id_manage, fields_to_update)
            with col_u2:
                if st.button(f"Delete Record {selected_record_id_manage}", use_container_width=True):
                    delete_record(selected_record_id_manage)
    else:
        st.info("No records to manage yet.")

else:
    st.info("No attendance records found. Mark attendance to see them here.")
