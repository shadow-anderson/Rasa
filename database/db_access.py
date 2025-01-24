import sqlite3
from typing import List, Tuple, Optional, Dict
import json

DATABASE_PATH = 'cdb.db'

def connect_db() -> sqlite3.Connection:
    """Connect to the SQLite database."""
    return sqlite3.connect(DATABASE_PATH)

def fetch_clinics_by_type(clinic_type: str) -> List[Tuple]:
    """Fetch all clinics matching a given type."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM clinics WHERE type = ?", (clinic_type,))
        clinics = cursor.fetchall()
        return clinics
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        conn.close()

def fetch_available_slots(clinic_id: int) -> List[Tuple]:
    """Fetch available slots for a specific clinic."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM slots
            WHERE clinic_id = ? AND available = 1
        """, (clinic_id,))
        slots = cursor.fetchall()
        return slots
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        conn.close()

def insert_booking(clinic_id: int, date: str, time: str, patient_name: str) -> Optional[int]:
    """Insert a new booking into the database."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO bookings (clinic_id, date, time, patient_name)
            VALUES (?, ?, ?, ?)
        """, (clinic_id, date, time, patient_name))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        conn.close()

def fetch_clinics_by_problem_and_location(problem: str, location: str) -> List[Tuple]:
    """Fetch top clinic recommendations based on problem and location."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM clinics
            WHERE problem = ? AND location = ?
            ORDER BY rating DESC
            LIMIT 5
        """, (problem, location))
        clinics = cursor.fetchall()
        return clinics
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        conn.close()

def fetch_clinic_slots(clinic_id: int, opening_hour: int, closing_hour: int) -> Dict[str, str]:
    """Fetch slots for a clinic and return their availability."""
    conn = connect_db()
    cursor = conn.cursor()
    slots = {}
    try:
        for hour in range(opening_hour, closing_hour + 1):
            time = f"{hour}:00"
            cursor.execute("""
                SELECT available FROM slots
                WHERE clinic_id = ? AND time = ?
            """, (clinic_id, time))
            result = cursor.fetchone()
            if result:
                slots[time] = 'free' if result[0] == 1 else 'busy'
            else:
                slots[time] = 'free'
        return slots
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return {}
    finally:
        conn.close()

def fetch_slots_for_clinic_and_date(clinic_id: int, date: str) -> str:
    """Fetch slots for a given clinic and date from the bookings table and return as JSON."""
    conn = connect_db()
    cursor = conn.cursor()
    slots = {}
    try:
        cursor.execute("""
            SELECT time, available FROM bookings
            WHERE clinic_id = ? AND date = ?
        """, (clinic_id, date))
        results = cursor.fetchall()
        for result in results:
            time, available = result
            slots[time] = 'free' if available == 1 else 'busy'
        return json.dumps(slots)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return json.dumps({})
    finally:
        conn.close()

def update_slot_status(clinic_id: int, date: str, time: str, status: str) -> bool:
    """Update a slot's status to 'busy' or 'free' in the bookings table for a specific clinic, date, and time."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        available = 1 if status == 'free' else 0
        cursor.execute("""
            UPDATE bookings
            SET available = ?
            WHERE clinic_id = ? AND date = ? AND time = ?
        """, (available, clinic_id, date, time))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        conn.close()

# Example usage
if __name__ == "__main__":
    # Fetch clinics of type 'dental'
    dental_clinics = fetch_clinics_by_type('dental')
    print("Dental Clinics:", dental_clinics)

    # Fetch available slots for a specific clinic
    if dental_clinics:
        clinic_id = dental_clinics[0][0]  # Assuming the first clinic's ID
        available_slots = fetch_available_slots(clinic_id)
        print("Available Slots:", available_slots)

        # Insert a new booking
        if available_slots:
            slot = available_slots[0]
            booking_id = insert_booking(clinic_id, slot[1], slot[2], 'John Doe')
            print("New Booking ID:", booking_id)

    # Fetch clinic slots with availability
    if dental_clinics:
        clinic_id = dental_clinics[0][0]  # Assuming the first clinic's ID
        clinic_slots = fetch_clinic_slots(clinic_id, 9, 17)  # Assuming clinic is open from 9 AM to 5 PM
        print("Clinic Slots:", clinic_slots)

    # Fetch slots for a given clinic and date
    if dental_clinics:
        clinic_id = dental_clinics[0][0]  # Assuming the first clinic's ID
        slots_json = fetch_slots_for_clinic_and_date(clinic_id, "2023-11-05")
        print("Slots for Clinic on 2023-11-05:", slots_json)

    # Update slot status
    if dental_clinics:
        clinic_id = dental_clinics[0][0]  # Assuming the first clinic's ID
        updated = update_slot_status(clinic_id, "2023-11-05", "16:00", "busy")
        print("Slot status updated:", updated)