import os.path
import datetime as dt
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain.agents import tool
from tzlocal import get_localzone_name
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google():
    """Authenticates with Google Calendar API and returns a service object."""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # IMPORTANT: Ensure 'credentials.json' is in the same directory
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

@tool
def list_upcoming_events():
    """
    Useful for listing the next 10 upcoming events from the user's primary Google Calendar.
    """
    service = authenticate_google()
    now = dt.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('--> Getting the upcoming 10 events...')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        return 'No upcoming events found.'

    event_list = []
    for event in events:
        start_str = event['start'].get('dateTime', event['start'].get('date'))
        event_list.append(f"{start_str} - {event['summary']}")
    
    return "\n".join(event_list)

@tool
def add_event(summary: str, start_time_str: str, end_time_str: str, description: str = None):
    """
    Use this to add a new event to the primary Google Calendar.

    Args:
        summary (str): The title or summary of the event.
        start_time_str (str): The start time of the event in ISO format (e.g., YYYY-MM-DDTHH:MM:SS).
        end_time_str (str): The end time of the event in ISO format (e.g., YYYY-MM-DDTHH:MM:SS).
        description (str, optional): A description for the event. Defaults to None.
    """
    service = authenticate_google()
    try:
        local_tz_name = get_localzone_name()
        start_time = dt.datetime.fromisoformat(start_time_str)
        end_time = dt.datetime.fromisoformat(end_time_str)
    except ValueError:
        return "Invalid datetime format. Please use ISO format (e.g., YYYY-MM-DDTHH:MM:SS)."

    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': local_tz_name},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': local_tz_name},
    }
    
    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created successfully! View on Google Calendar: {created_event.get('htmlLink')}"
    except Exception as e:
        return f"An error occurred: {e}"

@tool
def check_schedule_for_day(date: str):
    """
    Checks the schedule for a given day and returns a list of events.

    Args:
        date (str): The date to check in YYYY-MM-DD format.
    """
    service = authenticate_google()
    try:
        day = dt.datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD."

    local_tz = dt.datetime.now().astimezone().tzinfo
    time_min = dt.datetime.combine(day, dt.time.min, tzinfo=local_tz).isoformat()
    time_max = dt.datetime.combine(day, dt.time.max, tzinfo=local_tz).isoformat()

    print(f"--> Getting events for {day.strftime('%Y-%m-%d')}...")
    events_result = service.events().list(
        calendarId='primary', timeMin=time_min, timeMax=time_max, singleEvents=True, orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        return f"You are free on {day.strftime('%Y-%m-%d')}."

    event_list = [f"Your schedule for {day.strftime('%Y-%m-%d')}:"]
    for event in events:
        start_str = event['start'].get('dateTime', event['start'].get('date'))
        if 'T' in start_str:
            start_formatted = dt.datetime.fromisoformat(start_str).strftime('%I:%M %p')
        else:
            start_formatted = "All-day"
        event_list.append(f"- {start_formatted}: {event['summary']}")
    
    return "\n".join(event_list)

@tool
def check_availability(start_time_str: str, end_time_str: str):
    """
    Finds and returns free slots in the calendar within a given time range.

    Args:
        start_time_str (str): The start of the range in ISO format (e.g., YYYY-MM-DDTHH:MM:SS).
        end_time_str (str): The end of the range in ISO format (e.g., YYYY-MM-DDTHH:MM:SS).
    """
    service = authenticate_google()
    try:
        start_time = dt.datetime.fromisoformat(start_time_str)
        end_time = dt.datetime.fromisoformat(end_time_str)
    except ValueError:
        return "Invalid datetime format. Please use ISO format (e.g., YYYY-MM-DDTHH:MM:SS)."

    print(f"--> Checking for availability from {start_time} to {end_time}...")
    events_result = service.events().list(
        calendarId='primary', timeMin=start_time.isoformat() + 'Z', timeMax=end_time.isoformat() + 'Z',
        singleEvents=True, orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        return "You are completely free during this period."

    last_event_end = start_time
    free_slots = []
    for event in events:
        event_start_str = event['start'].get('dateTime')
        if not event_start_str: continue
        
        event_start = dt.datetime.fromisoformat(event_start_str).replace(tzinfo=None)
        if last_event_end < event_start:
            free_slots.append((last_event_end, event_start))
        
        event_end_str = event['end'].get('dateTime')
        event_end = dt.datetime.fromisoformat(event_end_str).replace(tzinfo=None)
        last_event_end = max(last_event_end, event_end)

    if last_event_end < end_time:
        free_slots.append((last_event_end, end_time))

    if not free_slots:
        return "No free slots found in the specified range."
    
    slot_list = ["You have the following free slots:"]
    for slot_start, slot_end in free_slots:
        slot_list.append(f"- From {slot_start.strftime('%I:%M %p')} to {slot_end.strftime('%I:%M %p')}")
    return "\n".join(slot_list)


def main():
    """Main entry point for the LangChain scheduling agent."""
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not found. Please create or check your .env file.")
        return

    # Authenticate once at the start to ensure credentials are valid
    print("Authenticating with Google Calendar...")
    authenticate_google()
    print("Authentication successful. Welcome to your LangChain Scheduling Agent!")
    
    tools = [list_upcoming_events, add_event, check_schedule_for_day, check_availability]
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    print("You can now ask me to manage your calendar. Type 'exit' or 'quit' to leave.")

    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue

            result = agent_executor.invoke({"input": user_input})
            print(f"\n{result.get('output')}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == '__main__':
    main()
