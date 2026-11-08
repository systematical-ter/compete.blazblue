import configparser
import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

creds = service_account.Credentials.from_service_account_file(
    "../service_credentials.json", scopes=SCOPES
)
config = configparser.ConfigParser()
config.read("config.env")
calendar_id = config['DEFAULT']['calendar_id']

def get_events(minDate, maxDate):
    try:
        service = build("calendar", "v3", credentials=creds)

        # add a day so we definitely get events through the last day being displayed
        maxDate = maxDate + datetime.timedelta(days=1)

        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=minDate.isoformat(),
                timeMax=maxDate.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        return events

    except HttpError as error:
        print(f"An error occurred: {error}")