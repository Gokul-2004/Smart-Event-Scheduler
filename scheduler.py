from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import datetime
import os.path
import pickle

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/calendar.events']

def authenticate():
    """Handles Google Calendar authentication."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

def create_test_event(service):
    """Creates a test event in the user's calendar."""
    # Create an event starting in 1 hour, lasting 1 hour
    start_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    end_time = start_time + datetime.timedelta(hours=1)

    event = {
        'summary': 'Test Event - Smart Scheduler',
        'description': 'This is a test event created by Smart Event Scheduler',
        'start': {
            'dateTime': start_time.isoformat() + 'Z',
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time.isoformat() + 'Z',
            'timeZone': 'UTC',
        },
        'reminders': {
            'useDefault': True,
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    return event

def list_upcoming_events(service):
    """Lists the user's next 5 upcoming events."""
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    print('Getting upcoming 5 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=5, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"- {event['summary']} ({start})")

def main():
    print("Starting Smart Event Scheduler...")
    print("\n1. Authenticating with Google Calendar...")
    service = authenticate()
    print("✓ Authentication successful!")

    print("\n2. Creating a test event...")
    event = create_test_event(service)
    print(f"✓ Test event created successfully!")
    print(f"Event link: {event.get('htmlLink')}")

    print("\n3. Listing your upcoming events:")
    list_upcoming_events(service)

if __name__ == '__main__':
    main()
