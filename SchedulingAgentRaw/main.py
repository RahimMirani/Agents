import os.path
import datetime as dt
import argparse
import os
import json
from tzlocal import get_localzone_name
from dotenv import load_dotenv
import google.generativeai as genai
import dateparser


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
        # Get the local timezone name
        local_tz_name = get_localzone_name()
        
        # Parse start and end times from isoformat string
        start_time = dt.datetime.fromisoformat(start_time_str)
        end_time = dt.datetime.fromisoformat(end_time_str)

    except ValueError:
        print("Invalid datetime format. Please use ISO format (e.g., YYYY-MM-DDTHH:MM:SS).")
        return

    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': local_tz_name,
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': local_tz_name,
        },
    }

    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created successfully!")
        print(f"View on Google Calendar: {created_event.get('htmlLink')}")
    except Exception as e:
        print(f"An error occurred: {e}")

def handle_natural_language_command(service, user_input):
    """Uses an LLM to parse a natural language command and execute the corresponding function."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found. Please create a .env file with your key.")
        return
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # We provide the current time to give the LLM context for relative dates like "tomorrow".
    current_time = dt.datetime.now().isoformat()

    prompt = f"""
    You are a helpful assistant that translates natural language commands into structured JSON function calls for a Google Calendar agent.
    The current time is {current_time}.
    Analyze the user's request and determine which of the available functions should be called and what parameters to use.

    Available functions:
    1. add_event(summary, start_time, end_time, description): Used to create a new event.
       - 'summary' is the event title.
       - 'start_time' and 'end_time' must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
       - 'description' is an optional text field.
    2. check_schedule_for_day(date): Used to see all events on a specific day.
       - 'date' must be in YYYY-MM-DD format.
    3. check_availability(start_time, end_time): Used to find free slots within a time range.
       - 'start_time' and 'end_time' must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
    4. list_upcoming_events(): Used to see the next 10 events. Requires no parameters.

    User's request: "{user_input}"

    Based on the request, output a single JSON object with two keys:
    - "function_name": The name of the function to call (e.g., "add_event").
    - "parameters": A dictionary of the arguments for that function.

    Example for "add meeting tomorrow at 2pm for 1 hour":
    {{
        "function_name": "add_event",
        "parameters": {{
            "summary": "meeting",
            "start_time": "YYYY-MM-DDTHH:14:00:00",
            "end_time": "YYYY-MM-DDTHH:15:00:00",
            "description": null
        }}
    }}
    (Note: The date YYYY-MM-DD would be calculated based on the current time provided.)

    Now, generate the JSON for the user's request above.
    """

    try:
        response = model.generate_content(prompt)
        # Clean up the response from the LLM, which might be wrapped in ```json ... ```
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()
        
        parsed_command = json.loads(cleaned_response)
        function_name = parsed_command.get("function_name")
        parameters = parsed_command.get("parameters", {})

        print(f"LLM interpretation: Calling function '{function_name}' with parameters: {parameters}")

        if function_name == "add_event":
            add_event(service, **parameters)
        elif function_name == "check_schedule_for_day":
            # dateparser is more robust for the LLM's potential output
            parsed_date = dateparser.parse(parameters.get("date")).strftime('%Y-%m-%d')
            check_schedule_for_day(service, parsed_date)
        elif function_name == "check_availability":
            check_availability(service, parameters.get("start_time"), parameters.get("end_time"))
        elif function_name == "list_upcoming_events":
            list_upcoming_events(service)
        else:
            print(f"Unknown command: {function_name}")

    except (json.JSONDecodeError, AttributeError, KeyError) as e:
        print(f"Could not understand the command. Please try rephrasing. Error: {e}")
        print(f"LLM Response was: {response.text}")


def check_availability(service, start_str, end_str):
    """Finds and prints free slots in the calendar within a given time range."""
    try:
        local_tz_name = get_localzone_name()
        start_time = dt.datetime.fromisoformat(start_str)
        end_time = dt.datetime.fromisoformat(end_str)
    except ValueError:
        print("Invalid datetime format. Please use ISO format (e.g., YYYY-MM-DDTHH:MM:SS).")
        return

    print(f"Checking for availability from {start_time} to {end_time}...")

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_time.isoformat() + 'Z',
        timeMax=end_time.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        print("You are completely free during this period.")
        return

    last_event_end = start_time
    free_slots = []

    for event in events:
        event_start_str = event['start'].get('dateTime')
        if not event_start_str:  # Skip all-day events
            continue
        
        event_start = dt.datetime.fromisoformat(event_start_str).replace(tzinfo=None)

        if last_event_end < event_start:
            free_slots.append((last_event_end, event_start))
        
        event_end_str = event['end'].get('dateTime')
        event_end = dt.datetime.fromisoformat(event_end_str).replace(tzinfo=None)
        last_event_end = max(last_event_end, event_end)

    if last_event_end < end_time:
        free_slots.append((last_event_end, end_time))

    if not free_slots:
        print("No free slots found in the specified range.")
    else:
        print("You have the following free slots:")
        for slot_start, slot_end in free_slots:
            print(f"- From {slot_start.strftime('%Y-%m-%d %I:%M %p')} to {slot_end.strftime('%Y-%m-%d %I:%M %p')}")


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

    # 'availability' command
    parser_avail = subparsers.add_parser('availability', help='Check for free slots in a given time range.')
    parser_avail.add_argument('--start', type=str, required=True, help='The start of the range in ISO format (YYYY-MM-DDTHH:MM:SS).')
    parser_avail.add_argument('--end', type=str, required=True, help='The end of the range in ISO format (YYYY-MM-DDTHH:MM:SS).')

    # 'ask' command
    parser_ask = subparsers.add_parser('ask', help='Use natural language to interact with the calendar.')
    parser_ask.add_argument('query', type=str, help='Your request in plain English, enclosed in quotes.')

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
    elif args.command == 'availability':
        check_availability(service, args.start, args.end)
    elif args.command == 'ask':
        handle_natural_language_command(service, args.query)


if __name__ == '__main__':
    main()
    


    

