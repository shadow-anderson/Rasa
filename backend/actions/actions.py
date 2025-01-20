import sqlite3
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from database.db_access import insert_booking, fetch_available_slots, fetch_clinics_by_type

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

class ActionFetchClinics(Action):

    def name(self) -> Text:
        return "action_fetch_clinics"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract user preferences from slots
        clinic_type = tracker.get_slot('clinic_type')
        location = tracker.get_slot('location')

        # Fetch clinics based on type
        clinics = fetch_clinics_by_type(clinic_type)

        if clinics:
            clinic_list = "\n".join([f"{clinic[1]} located at {clinic[2]}" for clinic in clinics if clinic[3] == location])
            dispatcher.utter_message(text=f"Here are the {clinic_type} clinics in {location}:\n{clinic_list}")
        else:
            dispatcher.utter_message(text=f"Sorry, no {clinic_type} clinics found in {location}.")

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
