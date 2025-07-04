import datetime
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import streamlit as st
import json
# Load credentials from the service account file
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), '../creds/service_account.json')
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = "anshumansinghs044@gmail.com"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build('calendar', 'v3', credentials=credentials)

# Load credentials from Streamlit secrets
service_account_info = st.secrets["google"]
credentials = service_account.Credentials.from_service_account_info(service_account_info)

def get_availability(start_time: datetime.datetime, end_time: datetime.datetime):
    """Returns busy slots from Google Calendar between start_time and end_time"""
    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start_time.isoformat() + 'Z',
        timeMax=end_time.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    busy_slots = []

    for event in events:
        start = event['start'].get('dateTime')
        end = event['end'].get('dateTime')
        busy_slots.append((start, end))

    return busy_slots


def book_event(summary: str, start_time: datetime.datetime, duration_minutes: int):
    """Books an event on Google Calendar"""
    end_time = start_time + datetime.timedelta(minutes=duration_minutes)

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
    }
    print(f"📤 Sending to calendar ID: {CALENDAR_ID}")
    print(f"📝 Event Details: {event}")

    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return created_event.get('htmlLink')


# ✅ Wrappers for LangChain agent tools

def create_event(summary: str = "Meeting", date: str = None, time: str = None, duration: int = 60):
    """
    Wrapper function that creates a calendar event from summary, date, time.
    Example input: "summary='Meeting with Kriti', date='2024-07-05', time='15:00'"
    """
    try:
        start_datetime = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        link = book_event(summary, start_datetime, duration)
        return f"✅ Event created: {link}"
    except Exception as e:
        return f"❌ Failed to create event: {e}"


def get_events_for_today():
    """Returns all events scheduled for today"""
    now = datetime.datetime.now()
    start = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
    end = start + datetime.timedelta(days=1)

    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start.isoformat() + 'Z',
        timeMax=end.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    if not events:
        return "📅 No events found for today."

    schedule = "📅 Today's Schedule:\n"
    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', 'No title')
        schedule += f"- {start_time}: {summary}\n"

    return schedule

def get_today_range():
    """Returns start and end datetime for today"""
    now = datetime.datetime.now(datetime.timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + datetime.timedelta(days=1)
    return start, end
