import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json
from airtable import Airtable

# --- Configuration ---
TABLE_NAME = "Attendance Log" # This MUST match your table name in Airtable

# Lists of CRP and FA names
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
@st.cache_resource # Cache the Airtable connection to avoid re-initializing on every rerun
def get_airtable_client():
    try:
        api_key = st.secrets["airtable"]["api_key"]
        base_id = st.secrets["airtable"]["base_id"]
        return Airtable(base_id, TABLE_NAME, api_key)
    except KeyError:
        st.error("Airtable API Key or Base ID not found in Streamlit secrets. Please configure `.streamlit/secrets.toml`.")
        st.stop() # Stop the app if secrets are missing
    except Exception as e:
        st.error(f"Error connecting to Airtable: {e}")
        st.stop()

# --- Functions for Attendance Management (Airtable) ---

@st.cache_data(ttl=60) # Cache data for 60 seconds to reduce API calls
def load_attendance_data_from_airtable():
    """Loads attendance data from Airtable."""
    airtable = get_airtable_client()
    try:
        records = airtable.get_all() # Get all records from the table
        # Extract fields and the 'id' of each record
        data = []
        for record in records:
            record_data = record['fields']
            record_data['record_id'] = record['id'] # Store Airtable's unique record ID
            data.append(record_data)

        df = pd.DataFrame(data)

        # Ensure all expected columns exist, fill missing with None/empty string
        expected_cols = ['Timestamp', 'Person', 'Type', 'Status', 'Photo_Uploaded', 'Latitude', 'Longitude', 'record_id']
        for col in expected_cols:
            if col not in df.columns:
                df[col] = None # Or an appropriate default value

        # Convert Timestamp column to datetime if possible for sorting
        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Could not load attendance data from Airtable: {e}")
        return pd.DataFrame(columns=['Timestamp', 'Person', 'Type', 'Status', 'Photo_Uploaded', 'Latitude', 'Longitude', 'record_id'])

def mark_attendance(person_name, person_type, status, photo_info="No Photo", lat=None, lon=None):
    """Marks attendance for a given person in Airtable (Create operation)."""
    airtable = get_airtable_client()
    now = datetime.now()
    timestamp_str = now.strftime('%Y-%m-%d %H:%M:%S')

    # Re-load data to check for today's attendance before marking
    st.cache_data.clear() # Invalidate cache for the latest data for this check
    current_df = load_attendance_data_from_airtable()

    # Check if attendance is already marked for today for this person
    date_today = now.strftime('%Y-%m-%d')
    if 'Timestamp' in current_df.columns and not current_df[(current_df['Timestamp'].dt.strftime('%Y-%m-%d') == date_today) & (current_df['Person'] == person_name)].empty:
        st.warning(f"Attendance for **{person_name}** has already been marked today ({date_today}). Skipping.")
        return False

    # Prepare data for Airtable record
    new_record = {
        'Timestamp': timestamp_str,
        'Person': person_name,
        'Type': person_type,
        'Status': status,
        'Photo_Uploaded': photo_info,
        'Latitude': lat,
        'Longitude': lon
    }

    try:
        airtable.insert(new_record)
        st.success(f"Attendance marked for **{person_name}** as **{status}** and saved to Airtable.")
        st.cache_data.clear() # Invalidate cache so next load gets the new data
        return True
    except Exception as e:
        st.error(f"Error marking attendance in Airtable: {e}")
        return False

def update_record_in_airtable(record_id, updated_fields):
    """Updates an existing record in Airtable."""
    airtable = get_airtable_client()
    try:
        airtable.update(record_id, updated_fields)
        st.success(f"Record {record_id} updated successfully in Airtable.")
        st.cache_data.clear() # Invalidate cache
        return True
    except Exception as e:
        st.error(f"Error updating record {record_id} in Airtable: {e}")
        return False

def delete_record_from_airtable(record_id):
    """Deletes a record from Airtable."""
    airtable = get_airtable_client()
    try:
        airtable.delete(record_id)
        st.success(f"Record {record_id} deleted successfully from Airtable.")
        st.cache_data.clear() # Invalidate cache
        return True
    except Exception as e:
        st.error(f"Error deleting record {record_id} from Airtable: {e}")
        return False


# --- Geolocation JavaScript Component ---
GET_LOCATION_JS = """
<script>
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(showPosition, showError, {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            });
        } else {
            alert("Geolocation is not supported by this browser.");
            updateStreamlitLocation(null, null, "Geolocation not supported.");
        }
    }

    function showPosition(position) {
        var latitude = position.coords.latitude;
        var longitude = position.coords.longitude;
        updateStreamlitLocation(latitude, longitude, "Location obtained.");
    }

    function showError(error) {
        let message = "";
        switch(error.code) {
            case error.PERMISSION_DENIED:
                message = "User denied the request for Geolocation. Please allow location access in your browser settings.";
                break;
            case error.POSITION_UNAVAILABLE:
                message = "Location information is unavailable.";
                break;
            case error.TIMEOUT:
                message = "The request to get user location timed out.";
                break;
            case error.UNKNOWN_ERROR:
                message = "An unknown error occurred.";
                break;
        }
        alert("Location error: " + message);
        updateStreamlitLocation(null, null, message);
    }

    function updateStreamlitLocation(lat, lon, status) {
        // Use Streamlit's query parameters to send data back
        const url = new URL(window.location);
        url.searchParams.set('lat', lat !== null ? lat : 'null');
        url.searchParams.set('lon', lon !== null ? lon : 'null');
        url.searchParams.set('loc_status', status);
        window.location.href = url.toString(); // Reruns the Streamlit app
    }
</script>
<button onclick="getLocation()">Get My Location</button>
"""

# --- Streamlit UI ---

st.set_page_config(layout="centered", page_title="CRP/FA Attendance System", page_icon="📝")

st.title("📝 CRP/FA Attendance System")
st.markdown("---")

st.info("""
    **Data Persistence:** This app uses **Airtable** for persistent data storage.
    Your attendance records will be saved and will not be lost when the app restarts.
    Ensure your Airtable Base and `secrets.toml` are correctly configured.
""")
st.markdown("---")


# Initialize session state for logged-in user and location
if 'logged_in_person' not in st.session_state:
    st.session_state['logged_in_person'] = None
if 'current_lat' not in st.session_state:
    st.session_state['current_lat'] = None
if 'current_lon' not in st.session_state:
    st.session_state['current_lon'] = None
if 'location_status' not in st.session_state:
    st.session_state['location_status'] = "Not obtained yet."
if 'selected_record_id' not in st.session_state:
    st.session_state['selected_record_id'] = None
if 'selected_record_data' not in st.session_state:
    st.session_state['selected_record_data'] = None

# --- Check for location data from URL query parameters ---
query_params = st.query_params
if 'lat' in query_params and 'lon' in query_params:
    try:
        lat = float(query_params['lat']) if query_params['lat'] != 'null' else None
        lon = float(query_params['lon']) if query_params['lon'] != 'null' else None
        loc_status = query_params.get('loc_status', "Location obtained.")

        st.session_state['current_lat'] = lat
        st.session_state['current_lon'] = lon
        st.session_state['location_status'] = loc_status

        if query_params.get('lat') is not None:
             st.query_params.clear()


    except ValueError:
        st.session_state['location_status'] = "Error parsing location data."
        st.session_state['current_lat'] = None
        st.session_state['current_lon'] = None
        st.query_params.clear()


# --- User Login / Selection ---
if st.session_state['logged_in_person'] is None:
    st.header("Select Your Name to Proceed")
    selected_name = st.selectbox(
        "Who are you?",
        options=["Select your name"] + ALL_PERSONS,
        key="user_selector"
    )
    if selected_name != "Select your name":
        st.session_state['logged_in_person'] = selected_name
        st.rerun()

else:
    st.sidebar.header(f"Logged in as: {st.session_state['logged_in_person']}")
    if st.sidebar.button("Log Out"):
        st.session_state['logged_in_person'] = None
        st.session_state['current_lat'] = None
        st.session_state['current_lon'] = None
        st.session_state['location_status'] = "Not obtained yet."
        st.session_state['selected_record_id'] = None
        st.session_state['selected_record_data'] = None
        st.rerun()

    # --- Tabbed Interface ---
    tab1, tab2 = st.tabs(["Mark My Attendance", "Manage Attendance Log"])

    with tab1:
        st.header(f"Mark Attendance for {st.session_state['logged_in_person']}")
        person_type = "CRP" if st.session_state['logged_in_person'] in CRP_NAMES else "FA"
        st.write(f"You are a **{person_type}**.")

        st.subheader("1. Upload Photo (Optional)")
        uploaded_file = st.file_uploader("Choose a photo...", type=["jpg", "jpeg", "png"], key="photo_uploader")
        photo_info_for_log = "No Photo Uploaded"
        if uploaded_file is not None:
            st.success("Photo uploaded successfully! (Note: Actual photo not stored persistently in this demo).")
            photo_info_for_log = f"Photo uploaded at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            st.image(uploaded_file, caption='Uploaded Photo', width=200)

        st.subheader("2. Get Your Location")
        st.html(GET_LOCATION_JS)

        if st.session_state['current_lat'] is not None and st.session_state['current_lon'] is not None:
            st.info(f"Location: Latitude {st.session_state['current_lat']:.4f}, Longitude {st.session_state['current_lon']:.4f}")
            st.text(f"Status: {st.session_state['location_status']}")
        else:
            st.warning(f"Location not obtained yet. Status: {st.session_state['location_status']}\n(Please ensure your browser allows location access).")

        st.subheader("3. Select Attendance Status")
        status_option = st.radio(
            "What is your attendance status?",
            ["Present", "Absent", "On Leave"],
            index=0,
            key="my_status_radio",
            horizontal=True
        )

        if st.button("Mark My Attendance", type="primary"):
            mark_attendance(
                st.session_state['logged_in_person'],
                person_type,
                status_option,
                photo_info_for_log,
                st.session_state['current_lat'],
                st.session_state['current_lon']
            )
            st.session_state['current_lat'] = None
            st.session_state['current_lon'] = None
            st.session_state['location_status'] = "Not obtained yet."
            st.rerun()


    with tab2:
        st.header("Manage Attendance Log")
        st.write("View, edit, or delete attendance records from Airtable.")
        st.markdown("---")

        if st.button("Refresh Attendance Data from Airtable", key="refresh_button"):
            st.cache_data.clear()
            st.session_state['selected_record_id'] = None
            st.session_state['selected_record_data'] = None
            st.info("Data refreshed from Airtable.")
            st.rerun()

        df_display = load_attendance_data_from_airtable()

        log_filter_options = ["All Records", st.session_state['logged_in_person']]
        selected_log_view = st.selectbox(
            "Show records for:",
            options=log_filter_options,
            key="log_view_selector"
        )

        df_to_display = df_display
        if selected_log_view != "All Records" and not df_display.empty:
            df_to_display = df_display[df_display['Person'] == selected_log_view]

        st.subheader("Current Records:")
        if not df_to_display.empty:
            if 'Timestamp' in df_to_display.columns:
                 df_to_display_sorted = df_to_display.sort_values(by='Timestamp', ascending=False)
            else:
                 df_to_display_sorted = df_to_display

            df_for_display = df_to_display_sorted.drop(columns=['record_id'], errors='ignore')
            selected_rows = st.dataframe(
                df_for_display,
                use_container_width=True,
                hide_index=True,
                selection_mode='single-row'
            )

            if selected_rows and selected_rows['selection']['rows']:
                selected_index_in_df = selected_rows['selection']['rows'][0]
                st.session_state['selected_record_data'] = df_to_display_sorted.iloc[selected_index_in_df].to_dict()
                st.session_state['selected_record_id'] = st.session_state['selected_record_data']['record_id']

                st.subheader(f"Selected Record (ID: {st.session_state['selected_record_id']})")
                st.json(st.session_state['selected_record_data'])

                st.markdown("---")
                st.subheader("Edit Selected Record")
                with st.form("edit_record_form"):
                    current_status = st.session_state['selected_record_data'].get('Status', 'Absent')
                    current_photo_info = st.session_state['selected_record_data'].get('Photo_Uploaded', 'No Photo Uploaded')
                    current_lat = st.session_state['selected_record_data'].get('Latitude')
                    current_lon = st.session_state['selected_record_data'].get('Longitude')

                    new_status = st.radio(
                        "Update Status:",
                        ["Present", "Absent", "On Leave"],
                        index=["Present", "Absent", "On Leave"].index(current_status) if current_status in ["Present", "Absent", "On Leave"] else 0,
                        key="edit_status"
                    )
                    new_photo_info = st.text_input("Update Photo Info (e.g., 'Photo Updated' or 'Link'):", value=current_photo_info, key="edit_photo_info")
                    new_lat = st.text_input("Update Latitude:", value=str(current_lat) if current_lat is not None else "", key="edit_lat")
                    new_lon = st.text_input("Update Longitude:", value=str(current_lon) if current_lon is not None else "", key="edit_lon")

                    col1, col2 = st.columns(2)
                    with col1:
                        update_button = st.form_submit_button("Update Record", type="primary")
                    with col2:
                        cancel_edit_button = st.form_submit_button("Cancel Edit")

                    if update_button:
                        try:
                            lat_val = float(new_lat) if new_lat else None
                            lon_val = float(new_lon) if new_lon else None
                        except ValueError:
                            st.error("Latitude and Longitude must be numbers.")
                            st.stop()

                        updated_fields = {
                            'Status': new_status,
                            'Photo_Uploaded': new_photo_info,
                            'Latitude': lat_val,
                            'Longitude': lon_val
                        }
                        if update_record_in_airtable(st.session_state['selected_record_id'], updated_fields):
                            st.session_state['selected_record_id'] = None
                            st.session_state['selected_record_data'] = None
                            st.rerun()
                    if cancel_edit_button:
                        st.session_state['selected_record_id'] = None
                        st.session_state['selected_record_data'] = None
                        st.rerun()

                st.markdown("---")
                st.subheader("Delete Selected Record")
                if st.button("Delete Record", type="secondary"):
                    confirm_delete = st.warning(f"Are you sure you want to delete record {st.session_state['selected_record_id']} for {st.session_state['selected_record_data'].get('Person')}?")
                    if st.button("Yes, Delete Permanently", key="confirm_delete_btn"):
                        if delete_record_from_airtable(st.session_state['selected_record_id']):
                            st.session_state['selected_record_id'] = None
                            st.session_state['selected_record_data'] = None
                            st.rerun()
                    elif st.button("No, Cancel Delete", key="cancel_delete_btn"):
                        st.info("Delete operation cancelled.")
                        st.session_state['selected_record_id'] = None
                        st.session_state['selected_record_data'] = None
                        st.rerun()

            else:
                st.info("Select a row in the table above to edit or delete a record.")
        else:
            st.info("No attendance records found yet. Mark some attendance first!")

        st.markdown("---")
        st.subheader("Download Full Attendance Log")

        @st.cache_data
        def convert_df_to_excel_bytes(df):
            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Attendance')
            processed_data = output.getvalue()
            return processed_data

        if not df_display.empty:
            excel_data = convert_df_to_excel_bytes(df_display)
            st.download_button(
                label="Download Full Attendance Log (Excel)",
                data=excel_data,
                file_name="attendance_log_full.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No data to download yet.")
