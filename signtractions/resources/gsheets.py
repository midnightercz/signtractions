from pytractions.base import Base


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]


class GSheets(Base):
    """Class for manipulation of Google Sheets."""

    sheet_id: str
    token_file: str
    client_secret_file: str

    def __post_init__(self):
        """Initialize the instance."""
        self._service = None

    @property
    def service(self):
        """Return the Google Sheets service."""
        if not self._service:
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file("client-secret.json", SCOPES)
                    creds = flow.run_local_server(port=0)
                    print("creds", creds)
                # Save the credentials for the next run
                with open(self.token_file, "w") as token:
                    token.write(creds.to_json())
            self._service = build("sheets", "v4", credentials=creds)
        return self._service

    def append_values(self, drange, values):
        """Append values to a Google Sheet."""
        values = [values]
        body = {"values": values}

        self.service.spreadsheets().values().append(
            spreadsheetId=self.sheet_id,
            range=drange,
            valueInputOption="RAW",
            body=body,
        ).execute()
