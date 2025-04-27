class ProzorroAPIError(Exception):
    """Base exception for Prozorro API errors."""
    pass


class ProzorroConnectionError(ProzorroAPIError):
    """Exception raised when connection to Prozorro API fails."""
    pass


class ProzorroResponseError(ProzorroAPIError):
    """Exception raised when Prozorro API returns an error response."""
    
    def __init__(self, status_code: int, response_text: str):
        self.status_code = status_code
        self.response_text = response_text
        message = f"API returned error with status code {status_code}: {response_text}"
        super().__init__(message)


class ProzorroParsingError(ProzorroAPIError):
    """Exception raised when parsing the API response fails."""
    pass 