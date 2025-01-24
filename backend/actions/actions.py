import sqlite3
import re
import json
from datetime import datetime
from typing import Any, Text, Dict, List, Optional
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FormValidationAction
from database.db_access import insert_booking, fetch_available_slots, fetch_clinics_by_type, fetch_clinics_by_problem_and_location

DATABASE_PATH = '../database/cdb.db'

def execute_query(query: str, params: tuple = ()) -> List[tuple]:
    """Execute a query on the SQLite database and return the results."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        conn.close()

class ValidateAppointmentForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_appointment_form"

    def validate_date(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Dict[Text, Any]]:
        """Validate date value."""
        try:
            datetime.strptime(slot_value, '%Y-%m-%d')
            return {"date": slot_value}
        except ValueError:
            dispatcher.utter_message(text="The date format is incorrect. Please provide the date in YYYY-MM-DD format.")
            return {"date": None}

    def validate_time(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Dict[Text, Any]]:
        """Validate time value."""
        if re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', slot_value):
            return {"time": slot_value}
        else:
            dispatcher.utter_message(text="The time format is incorrect. Please provide the time in HH:MM format.")
            return {"time": None}

    def validate_problem(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Dict[Text, Any]]:
        """Validate problem value."""
        if slot_value:
            return {"problem": slot_value}
        else:
            dispatcher.utter_message(text="Please describe the problem you are experiencing.")
            return {"problem": None}

    def validate_location(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Optional[Dict[Text, Any]]:
        """Validate location value."""
        if slot_value:
            return {"location": slot_value}
        else:
            dispatcher.utter_message(text="Please provide the location.")
            return {"location": None}
        
        
class ActionCheckAvailability(Action):

    def name(self) -> Text:
        return "action_check_availability"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract user preferences from slots
        date = tracker.get_slot('date')
        time = tracker.get_slot('time')
        doctor = tracker.get_slot('doctor')

        # Connect to the SQLite database
        conn = sqlite3.connect('clinic.db')
        cursor = conn.cursor()

        try:
            # Query the database for availability
            cursor.execute("""
                SELECT * FROM appointments
                WHERE date = ? AND time = ? AND doctor = ? AND available = 1
            """, (date, time, doctor))
            result = cursor.fetchone()

            if result:
                dispatcher.utter_message(text=f"An appointment is available with Dr. {doctor} on {date} at {time}.")
                return [SlotSet("appointment_available", True)]
            else:
                dispatcher.utter_message(text=f"Sorry, no appointments are available with Dr. {doctor} on {date} at {time}.")
                return [SlotSet("appointment_available", False)]

        except sqlite3.Error as e:
            dispatcher.utter_message(text="An error occurred while checking availability. Please try again later.")
            return [SlotSet("appointment_available", False)]

        finally:
            conn.close()

class ActionQueryClinic(Action):

    def name(self) -> Text:
        return "action_query_clinic"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract user preferences from slots
        problem = tracker.get_slot('problem')
        location = tracker.get_slot('location')
        date = tracker.get_slot('date')
        time = tracker.get_slot('time')

        # Fetch clinics based on problem and location
        clinics = fetch_clinics_by_problem_and_location(problem, location)

        if clinics:
            clinic_list = "\n".join([f"{clinic[1]} located at {clinic[2]}, Rating: {clinic[4]}" for clinic in clinics])
            dispatcher.utter_message(text=f"Here are the top clinics for {problem} in {location}:\n{clinic_list}")
        else:
            dispatcher.utter_message(text=f"Sorry, no clinics found for {problem} in {location}.")

        return []

class ActionBookAppointment(Action):

    def name(self) -> Text:
        return "action_book_appointment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract user inputs from slots
        clinic_id = tracker.get_slot('clinic_id')
        date = tracker.get_slot('date')
        time = tracker.get_slot('time')
        patient_name = tracker.get_slot('patient_name')

        # Validate inputs
        if not clinic_id or not date or not time or not patient_name:
            dispatcher.utter_message(text="Please provide all the required information to book an appointment.")
            return []

        # Check if the slot is available
        available_slots = fetch_available_slots(clinic_id)
        slot_available = any(slot[1] == date and slot[2] == time for slot in available_slots)

        if not slot_available:
            dispatcher.utter_message(text=f"Sorry, no available slots for the selected date and time at clinic ID {clinic_id}.")
            return []

        # Insert the booking into the database
        booking_id = insert_booking(clinic_id, date, time, patient_name)

        if booking_id:
            dispatcher.utter_message(text=f"Your appointment has been successfully booked with booking ID {booking_id}.")
            return [SlotSet("booking_id", booking_id)]
        else:
            dispatcher.utter_message(text="An error occurred while booking your appointment. Please try again later.")
            return []


class ActionRecommendClinic(Action):

    def name(self) -> Text:
        return "action_recommend_clinic"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract user preferences from slots
        problem = tracker.get_slot('problem')
        location = tracker.get_slot('location')

        # Fetch clinics based on problem and location
        clinics = fetch_clinics_by_problem_and_location(problem, location)

        if clinics:
            clinic_list = "\n".join([f"{clinic[1]} located at {clinic[2]}, Rating: {clinic[4]}" for clinic in clinics])
            dispatcher.utter_message(text=f"Here are the top clinics for {problem} in {location}:\n{clinic_list}")
        else:
            dispatcher.utter_message(text=f"Sorry, no clinics found for {problem} in {location}.")

        return []
    
def fetch_clinics_by_problem_location_and_time(problem: str, location: str, time: str) -> List[tuple]:
    """Fetch clinics based on problem, location, and opening hours."""
    query = """
        SELECT * FROM clinics
        WHERE Categories LIKE ? AND Municipality = ? AND ? BETWEEN OpeningHoursStart AND OpeningHoursEnd
    """
    params = (f"%{problem}%", location, time)
    return execute_query(query, params)

# Example usage
if __name__ == "__main__":
    problem = "dental"
    location = "city center"
    time = "14:00"
    clinics = fetch_clinics_by_problem_location_and_time(problem, location, time)
    print("Clinics:", clinics)

def get_slot_status(clinic_id: int, date: str, time: str) -> Dict[str, Any]:
    """Retrieve the slot status for a specific clinic on a given date and time."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT * FROM bookings
            WHERE clinic_id = ? AND date = ? AND time = ?
        """, (clinic_id, date, time))
        booking = cursor.fetchone()

        if booking:
            status = {
                "clinic_id": clinic_id,
                "date": date,
                "time": time,
                "available": False,
                "message": "Slot is already booked."
            }
        else:
            status = {
                "clinic_id": clinic_id,
                "date": date,
                "time": time,
                "available": True,
                "message": "Slot is available."
            }

        return json.dumps(status)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return json.dumps({
            "error": "An error occurred while retrieving slot status."
        })
    finally:
        conn.close()

# Example usage
if __name__ == "__main__":
    clinic_id = 1
    date = "2023-11-05"
    time = "16:00"
    slot_status = get_slot_status(clinic_id, date, time)
    print("Slot Status:", slot_status)


def mark_slot_as_busy(clinic_id: int, date: str, time: str) -> bool:
    """Mark a slot as busy for a specific clinic, date, and time."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE bookings
            SET available = 0
            WHERE clinic_id = ? AND date = ? AND time = ?
        """, (clinic_id, date, time))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        conn.close()

# Example usage
if __name__ == "__main__":
    clinic_id = 1
    date = "2023-11-05"
    time = "16:00"
    if mark_slot_as_busy(clinic_id, date, time):
        print("Slot marked as busy.")
    else:
        print("Failed to mark slot as busy.")