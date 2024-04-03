class FetchDataError(Exception):
    """Exception raised when there is an error fetching data from an external API."""

    def __init__(self, message="Error fetching data from the API"):
        self.message = message
        super().__init__(self.message)


class SaveDataError(Exception):
    """Exception raised when there is an error saving data."""

    def __init__(self, message="Error saving data"):
        self.message = message
        super().__init__(self.message)
