
class ConnectionError(Exception):
    """Custom exception for connection-related errors."""
    def __init__(self, message: str = "Connection error") -> None:
        """Conserve le message décrivant l’erreur de connexion."""
        super().__init__(message)


class HubError(Exception):
    """Custom exception for hub-related errors."""
    def __init__(self, message: str = "Hub error") -> None:
        """Conserve le message décrivant l’erreur de hub."""
        super().__init__(message)
