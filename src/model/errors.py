
class ConnectionError(Exception):
    """Exception for connection-related errors."""
    def __init__(self, message: str = "Connection error") -> None:
        """Initialize the exception with a connection error message."""
        super().__init__(message)


class HubError(Exception):
    """Exception for hub-related errors."""
    def __init__(self, message: str = "Hub error") -> None:
        """Initialize the exception with a hub error message."""
        super().__init__(message)
