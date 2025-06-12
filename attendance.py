import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Configuration ---
ATTENDANCE_FILE = 'attendance_log.xlsx' # This file needs to be present in your GitHub repo initially
                                        # Or you'll need to handle its creation gracefully on first run.

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

# --- Functions for Attendance Management ---

@st.cache_data(show_spinner=False) # Cache data loading to prevent re-reading on every rerun
def load_attendance_data():
    """Loads attendance data from the Excel file or creates a new DataFrame if it doesn't exist."""
    # When deployed, this file might not exist initially, so create it if needed.
    if not os.path.exists(ATTENDANCE_FILE):
        df = pd.DataFrame(columns=['Date', 'Time', 'Person', 'Type', 'Status'])
        # Create an empty Excel file so subsequent runs can find it
        try:
            df.to_excel(ATTENDANCE_FILE, index=False)
        except Exception as e:
            st.error(f"Could not create initial attendance file: {e}")
        return df
    else:
        try:
            return pd.read_excel(ATTENDANCE_FILE)
        except Exception as e:
            st.error(f"Could not load attendance file: {e}. Creating a new empty one.")
            return pd.DataFrame(columns=['Date', 'Time', 'Person', 'Type', 'Status'])

def save_attendance_data(df):
    """Saves the DataFrame to the Excel file.
    NOTE: On Streamlit Cloud, this saves to an ephemeral file system,
    meaning data will be lost on app restarts. For persistence,
    consider Google Sheets, S3, or similar.
    """
    try:
        df.to_excel(ATTENDANCE_FILE, index=False)
        st.session_state['attendance_data_updated'] = True # Mark for refresh if needed
        # st.success("Attendance data saved!") # Can be too verbose
    except Exception as e:
        st.error(f"Error saving attendance data: {e}")

def mark_attendance(person_name, person_type, status):
    """Marks attendance for a given person."""
    # Ensure st.session_state.df is initialized
    if 'df' not in st.session_state:
        st.session_state.df = load_attendance_data()

    df = st.session_state.df
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')

    # Check if attendance is already marked for today for this person
    if not df[(df['Date'] == date_str) & (df['Person'] == person_name)].empty:
        st.warning(f"Attendance for **{person_name}** has already been marked today ({date_str}). Skipping.")
        return False # Indicate that it was already marked

    new_entry = pd.DataFrame([{
        'Date': date_str,
        'Time': time_str,
        'Person': person_name,
        'Type': person_type,
        'Status': status
    }])
    st.session_state.df = pd.concat([df, new_entry], ignore_index=True)
    save_attendance_data(st.session_state.df)
    st.success(f"Attendance marked for **{person_name}** as **{status}**.")
    return True # Indicate successful marking

def get_person_attendance_log(person_name):
    """Retrieves the attendance log for a specific person."""
    if 'df' not in st.session_state:
        st.session_state.df = load_attendance_data()
    df = st.session_state.df
    person_df = df[df['Person'] == person_name].sort_values(by=['Date', 'Time'], ascending=[False, False])
    return person_df

# --- Streamlit UI ---

st.set_page_config(layout="centered", page_title="CRP/FA Attendance System", page_icon="📝")

st.title("📝 CRP/FA Attendance System")
st.markdown("---")

# Initialize DataFrame in session state if not already present
if 'df' not in st.session_state:
    st.session_state.df = load_attendance_data()

# --- Tabbed Interface ---
tab1, tab2 = st.tabs(["Mark Daily Attendance", "View Attendance Log"])

with tab1:
    st.header("Mark Daily Attendance")
    st.write("Select the status for each CRP/FA for today's attendance.")

    # Container for attendance form
    attendance_form_container = st.container(height=500, border=True)
    with attendance_form_container:
        st.subheader("Select Status")
        person_statuses = {}
        for person in ALL_PERSONS:
            default_status = "Absent" # Default
            # Check if already marked today and pre-fill if possible (not robust for session state persistence)
            # This check is primarily for the mark_attendance function's prevention of duplicates.
            # For pre-filling, you'd need a more complex check on the dataframe for today.

            person_type = "CRP" if person in CRP_NAMES else "FA"
            st.write(f"**{person}** ({person_type}):")
            status_option = st.radio(
                "Status",
                ["Present", "Absent", "On Leave"],
                index=["Present", "Absent", "On Leave"].index(default_status),
                key=f"status_{person}",
                horizontal=True
            )
            person_statuses[person] = status_option
            st.markdown("---") # Separator for clarity

    if st.button("Submit All Daily Attendance", type="primary"):
        # Clear previous messages
        # st.empty() # This can clear previous output
        all_marked_successfully = True
        for person, status in person_statuses.items():
            person_type = "CRP" if person in CRP_NAMES else "FA"
            if not mark_attendance(person, person_type, status):
                all_marked_successfully = False
        if all_marked_successfully:
            st.success("All attendance records processed successfully!")
        else:
            st.info("Some attendance records were already marked for today and were skipped.")
        # Rerun to update the view, important for Streamlit when data changes
        st.rerun()


with tab2:
    st.header("View Attendance Log")
    st.write("Select a person from the dropdown to view their attendance history.")

    selected_person = st.selectbox("Select a Person", ["Select a person"] + ALL_PERSONS, key="view_person_select")

    if selected_person and selected_person != "Select a person":
        st.subheader(f"Attendance Log for {selected_person}")
        person_log_df = get_person_attendance_log(selected_person)
        if not person_log_df.empty:
            st.dataframe(person_log_df, use_container_width=True)
        else:
            st.info(f"No attendance records found for **{selected_person}** yet.")
    else:
        st.info("Please select a person from the dropdown.")

    st.markdown("---")
    st.subheader("All Attendance Records (Raw Data)")
    if st.button("Refresh All Data View"):
        st.session_state.df = load_attendance_data() # Ensure latest data is loaded
    if not st.session_state.df.empty:
        st.dataframe(st.session_state.df.sort_values(by=['Date', 'Person'], ascending=[False, True]), use_container_width=True)
    else:
        st.info("No attendance records found yet. Mark some attendance first!")

    st.markdown("---")
    st.download_button(
        label="Download Full Attendance Log (Excel)",
        data=st.session_state.df.to_excel(index=False).encode('utf-8'),
        file_name="attendance_log_full.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
