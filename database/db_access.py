import sqlite3
from typing import List, Tuple, Optional

def connect_db(db_name: str = 'cdb.db') -> sqlite3.Connection:
    """Connect to the SQLite database."""
    return sqlite3.connect(db_name)

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