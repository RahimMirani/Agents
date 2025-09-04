import os.path
import datetime as dt
import argparse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

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
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

def main():
    """The main function to run the scheduling agent."""
    parser = argparse.ArgumentParser(description="A CLI agent to manage your Google Calendar.")
    parser.add_argument('command', choices=['list'], help='The command to execute (e.g., "list")')

    args = parser.parse_args()

    service = authenticate_google()

    if args.command == 'list':
        print("Successfully authenticated with Google Calendar API.")
        list_upcoming_events(service)

if __name__ == '__main__':
    main()
    


    

