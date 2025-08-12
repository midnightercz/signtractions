from pytractions.base import Base


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]


class FakeGSheets(Base):
    """Class for manipulation of Google Sheets."""

    def __post_init__(self):
        """Initialize the instance."""
        self._appended_values = []

    def append_values(self, drange, values):
        """Fake append values to a Google Sheet."""
        self._appended_values.append((drange, values))
