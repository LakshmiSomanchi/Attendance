import datetime
import pytz # For accurate timezones
import csv # To store data in a CSV file
import os # To check if file exists

def record_attendance():
    """Records attendance details including name, role, timestamp, and placeholders for geo/photo."""

    # --- 1. Dropdown for Names (Simulated via input) ---
    # In a real app, you'd load these from a file/database and use a UI dropdown.
    names = ["Aarav Sharma", "Priya Singh", "Rahul Verma", "Sneha Kumari", "Vikram Rathore"]
    print("\n--- Select your name ---")
    for i, name in enumerate(names):
        print(f"{i + 1}. {name}")

    selected_name = None
    while selected_name not in names:
        try:
            choice = int(input(f"Enter the number for your name (1-{len(names)}): "))
            if 1 <= choice <= len(names):
                selected_name = names[choice - 1]
            else:
                print("Invalid number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # --- 2. FA or CRP (Dropdown Simulated) ---
    roles = ["FA", "CRP"]
    selected_role = None
    while selected_role not in roles:
        role_input = input(f"Are you an FA or CRP? ({'/'.join(roles)}): ").upper()
        if role_input in roles:
            selected_role = role_input
        else:
            print("Invalid role. Please enter 'FA' or 'CRP'.")

    # --- 3. Timestamp (Automatic) ---
    # Using 'Asia/Kolkata' for Pune, Maharashtra, India
    india_timezone = pytz.timezone('Asia/Kolkata')
    current_time = datetime.datetime.now(india_timezone)
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S %Z%z") # Format: YYYY-MM-DD HH:MM:SS TZ+/-offset

    # --- 4. Geolocation (Placeholder) ---
    # In a real web/mobile app, this would be captured automatically from the device's GPS.
    # For CLI, you'd typically input it manually or integrate with a geocoding API.
    geolocation_data = input("Enter current geolocation (e.g., '28.7041, 77.1025' or 'Not Available'): ")

    # --- 5. Upload Photo (Placeholder) ---
    # In a real web/mobile app, this would be a file upload widget.
    # For CLI, you might specify a file path or just note 'Photo Captured'.
    photo_status = input("Did you upload a photo? (Yes/No): ").strip().lower()
    photo_filename = "N/A"
    if photo_status == 'yes':
        photo_filename = input("Enter photo filename/identifier (e.g., 'john_doe_20250611.jpg'): ")

    # Prepare data
    attendance_record = {
        "Timestamp": timestamp,
        "Name": selected_name,
        "Role": selected_role,
        "Geolocation": geolocation_data,
        "Photo Status": photo_filename # Storing filename or 'N/A'
    }

    # Save to CSV
    csv_file = "attendance_log.csv"
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=attendance_record.keys())
        if not file_exists:
            writer.writeheader() # Write header only if file doesn't exist
        writer.writerow(attendance_record)

    print("\n--- Attendance Recorded Successfully! ---")
    for key, value in attendance_record.items():
        print(f"{key}: {value}")
    print(f"\nRecord saved to {csv_file}")

if __name__ == "__main__":
    record_attendance()