import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json # For handling potential JSON from JS

# --- Configuration ---
ATTENDANCE_FILE = 'attendance_log.xlsx'

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

ALL_PERSONS = sorted(CRP_NAMES + FA_NAMES) # Combine and sort for display

# --- Functions for Attendance Management (Local File System) ---

def load_attendance_data():
    """Loads attendance data from the Excel file or creates a new DataFrame if it doesn't exist."""
    # This data will NOT persist across app restarts on Streamlit Cloud.
    # It's primarily for a demonstration or single-session use.
    if os.path.exists(ATTENDANCE_FILE):
        try:
            return pd.read_excel(ATTENDANCE_FILE)
        except Exception as e:
            st.warning(f"Could not load attendance file: {e}. Starting with an empty log.")
            return pd.DataFrame(columns=['Timestamp', 'Person', 'Type', 'Status', 'Photo_Uploaded', 'Latitude', 'Longitude'])
    else:
        return pd.DataFrame(columns=['Timestamp', 'Person', 'Type', 'Status', 'Photo_Uploaded', 'Latitude', 'Longitude'])

def save_attendance_data(df):
    """Saves the DataFrame to the Excel file.
    WARNING: This data will be lost on Streamlit Cloud app restarts.
    """
    try:
        df.to_excel(ATTENDANCE_FILE, index=False)
        # st.success("Attendance data saved to ephemeral storage.") # Can be too verbose
    except Exception as e:
        st.error(f"Error saving attendance data to ephemeral file: {e}")

def mark_attendance(person_name, person_type, status, photo_info="No Photo", lat=None, lon=None):
    """Marks attendance for a given person."""
    if 'df' not in st.session_state:
        st.session_state.df = load_attendance_data()

    df = st.session_state.df
    now = datetime.now()
    timestamp_str = now.strftime('%Y-%m-%d %H:%M:%S')

    # Check if attendance is already marked for today for this person
    date_today = now.strftime('%Y-%m-%d')
    if not df[(df['Timestamp'].str.startswith(date_today)) & (df['Person'] == person_name)].empty:
        st.warning(f"Attendance for **{person_name}** has already been marked today ({date_today}). Skipping.")
        return False # Indicate that it was already marked

    new_entry = pd.DataFrame([{
        'Timestamp': timestamp_str,
        'Person': person_name,
        'Type': person_type,
        'Status': status,
        'Photo_Uploaded': photo_info,
        'Latitude': lat,
        'Longitude': lon
    }])
    st.session_state.df = pd.concat([df, new_entry], ignore_index=True)
    save_attendance_data(st.session_state.df)
    st.success(f"Attendance marked for **{person_name}** as **{status}**.")
    return True # Indicate successful marking

# --- Geolocation JavaScript Component ---
# This JavaScript attempts to get the user's current location from their browser.
# It then sets query parameters in the URL, which causes Streamlit to rerun and
# allows the Python script to read those parameters.
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

st.warning("""
    **IMPORTANT: Data Persistence Warning!**\n
    This app currently stores attendance data in an **ephemeral file on the server.**
    This means **all data will be lost** when the app restarts (which happens frequently on Streamlit Cloud due to inactivity or updates).
    For persistent storage, you would need to integrate with a database like Google Sheets, Firebase, or a cloud storage service (requiring API keys/secrets).
""")
st.markdown("---")


# Initialize DataFrame in session state if not already present
if 'df' not in st.session_state:
    st.session_state.df = load_attendance_data()

# Initialize session state for logged-in user and location
if 'logged_in_person' not in st.session_state:
    st.session_state['logged_in_person'] = None
if 'current_lat' not in st.session_state:
    st.session_state['current_lat'] = None
if 'current_lon' not in st.session_state:
    st.session_state['current_lon'] = None
if 'location_status' not in st.session_state:
    st.session_state['location_status'] = "Not obtained yet."

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
        # Clear query params to prevent re-triggering on subsequent runs
        st.query_params.clear() # This will rerun the app again

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
        st.rerun() # Rerun to update the UI with the logged-in user

else:
    st.sidebar.header(f"Logged in as: {st.session_state['logged_in_person']}")
    if st.sidebar.button("Log Out"):
        st.session_state['logged_in_person'] = None
        st.session_state['current_lat'] = None # Clear location on logout
        st.session_state['current_lon'] = None
        st.session_state['location_status'] = "Not obtained yet."
        st.rerun()

    # --- Tabbed Interface ---
    tab1, tab2 = st.tabs(["Mark My Attendance", "View Attendance Log"])

    with tab1:
        st.header(f"Mark Attendance for {st.session_state['logged_in_person']}")
        person_type = "CRP" if st.session_state['logged_in_person'] in CRP_NAMES else "FA"
        st.write(f"You are a **{person_type}**.")

        st.subheader("1. Upload Photo (Optional)")
        uploaded_file = st.file_uploader("Choose a photo...", type=["jpg", "jpeg", "png"], key="photo_uploader")
        photo_info_for_log = "No Photo Uploaded"
        if uploaded_file is not None:
            st.success("Photo uploaded successfully! (Note: Actual photo not stored persistently in this demo).")
            # For a real app, you would upload `uploaded_file` to cloud storage (e.g., S3, Google Drive) here
            # and store its public URL in the sheet.
            photo_info_for_log = f"Photo uploaded at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            st.image(uploaded_file, caption='Uploaded Photo', width=200)

        st.subheader("2. Get Your Location")
        st.html(GET_LOCATION_JS) # Embed the JavaScript to get location

        if st.session_state['current_lat'] is not None and st.session_state['current_lon'] is not None:
            st.info(f"Location: Latitude {st.session_state['current_lat']:.4f}, Longitude {st.session_state['current_lon']:.4f}")
            st.text(f"Status: {st.session_state['location_status']}")
        else:
            st.warning(f"Location not obtained yet. Status: {st.session_state['location_status']}\n(Please ensure your browser allows location access).")

        st.subheader("3. Select Attendance Status")
        status_option = st.radio(
            "What is your attendance status?",
            ["Present", "Absent", "On Leave"],
            index=0, # Default to Present
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
            # Clear photo and location inputs after marking attendance
            # Note: This might not fully clear the file_uploader visually
            # To truly clear, you'd need to re-render the widget with a new key,
            # which is complex with state management.
            st.session_state['current_lat'] = None
            st.session_state['current_lon'] = None
            st.session_state['location_status'] = "Not obtained yet."
            st.rerun() # Rerun to clear location and photo

    with tab2:
        st.header("View Attendance Log")
        st.write("View the attendance history. **Remember, this data is not persistent across app restarts.**")

        # Filter option for viewing log
        log_filter_options = ["All Records", st.session_state['logged_in_person']]
        selected_log_view = st.selectbox(
            "Show records for:",
            options=log_filter_options,
            key="log_view_selector"
        )

        df_to_display = st.session_state.df
        if selected_log_view != "All Records":
            df_to_display = st.session_state.df[st.session_state.df['Person'] == selected_log_view]

        if not df_to_display.empty:
            # Sort by Timestamp descending
            df_to_display_sorted = df_to_display.sort_values(by='Timestamp', ascending=False)
            st.dataframe(df_to_display_sorted, use_container_width=True)
        else:
            st.info("No attendance records found yet for the selected view.")

        st.markdown("---")
        st.subheader("Download Current Attendance Log")

        @st.cache_data
        def convert_df_to_excel_bytes(df):
            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Attendance')
            processed_data = output.getvalue()
            return processed_data

        if 'df' in st.session_state and not st.session_state.df.empty:
            excel_data = convert_df_to_excel_bytes(st.session_state.df)
            st.download_button(
                label="Download Full Attendance Log (Excel)",
                data=excel_data,
                file_name="attendance_log_full.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No data to download yet.")
