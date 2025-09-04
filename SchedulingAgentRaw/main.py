import os.path
import datetime as dt
import argparse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.

    if os.path.exists('SchedulingAgentRaw/token.json'):
        creds = Credentials.from_authorized_user_file('SchedulingAgentRaw/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'SchedulingAgentRaw/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('SchedulingAgentRaw/token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

def list_upcoming_events(service):
    """Lists the next 10 upcoming events from the user's primary calendar."""
    now = dt.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return

    # Prints the start and name of the next 10 events
    for event in events:
        start_str = event['start'].get('dateTime', event['start'].get('date'))
        
        if 'T' in start_str:  # It's a dateTime
            event_dt = dt.datetime.fromisoformat(start_str)
            start_formatted = event_dt.strftime('%Y-%m-%d %I:%M %p')
        else:  # It's an all-day event
            start_formatted = start_str

        print(f"{start_formatted} - {event['summary']}")

def check_schedule_for_day(service, date_str=None):
    """Checks the schedule for a given day and prints the events."""
    if date_str:
        try:
            day = dt.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return
    else:
        day = dt.date.today()

    local_tz = dt.datetime.now().astimezone().tzinfo
    time_min = dt.datetime.combine(day, dt.time.min, tzinfo=local_tz).isoformat()
    time_max = dt.datetime.combine(day, dt.time.max, tzinfo=local_tz).isoformat()

    print(f"Getting events for {day.strftime('%Y-%m-%d')}...")
    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        print(f"You are free on {day.strftime('%Y-%m-%d')}.")
        return

    print(f"Your schedule for {day.strftime('%Y-%m-%d')}:")
    for event in events:
        start_str = event['start'].get('dateTime', event['start'].get('date'))
        
        if 'T' in start_str:  # It's a dateTime
            event_time = dt.datetime.fromisoformat(start_str)
            start_formatted = event_time.strftime('%I:%M %p')
        else:  # It's an all-day event
            start_formatted = "All-day"

        print(f"- {start_formatted}: {event['summary']}")

def add_event(service, summary, start_time_str, end_time_str, description=None):
    """Adds a new event to the primary calendar."""
    try:
        # Get the local timezone
        local_tz = dt.datetime.now().astimezone().tzinfo
        
        # Parse start and end times
        start_time = dt.datetime.fromisoformat(start_time_str).astimezone(local_tz)
        end_time = dt.datetime.fromisoformat(end_time_str).astimezone(local_tz)

    except ValueError:
        print("Invalid datetime format. Please use ISO format (e.g., YYYY-MM-DDTHH:MM:SS).")
        return

    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': str(local_tz),
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': str(local_tz),
        },
    }

    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created successfully!")
        print(f"View on Google Calendar: {created_event.get('htmlLink')}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    """The main function to run the scheduling agent."""
    parser = argparse.ArgumentParser(description="A CLI agent to manage your Google Calendar.")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # 'list' command
    subparsers.add_parser('list', help='List the next 10 upcoming events.')

    # 'check' command
    parser_check = subparsers.add_parser('check', help='Check the schedule for a specific day.')
    parser_check.add_argument('--date', type=str, help='The date to check in YYYY-MM-DD format. Defaults to today.')

    # 'add' command
    parser_add = subparsers.add_parser('add', help='Add a new event to the calendar.')
    parser_add.add_argument('--summary', type=str, required=True, help='The title of the event.')
    parser_add.add_argument('--start', type=str, required=True, help='The start time in ISO format (YYYY-MM-DDTHH:MM:SS).')
    parser_add.add_argument('--end', type=str, required=True, help='The end time in ISO format (YYYY-MM-DDTHH:MM:SS).')
    parser_add.add_argument('--desc', type=str, help='An optional description for the event.')

    args = parser.parse_args()

    service = authenticate_google()
    print("Successfully authenticated with Google Calendar API.")

    if args.command == 'list':
        list_upcoming_events(service)
    elif args.command == 'check':
        check_schedule_for_day(service, args.date)
    elif args.command == 'add':
        print("Attempting to add a new event...")
        add_event(service, args.summary, args.start, args.end, args.desc)


if __name__ == '__main__':
    main()
    


    

