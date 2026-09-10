
class ConnectionError(Exception):
    """Custom exception for connection-related errors."""
    def __init__(self, message: str = "Connection error") -> None:
        """Conserve le message décrivant l’erreur de connexion."""
        self.message = message
        super().__init__(self.message)


class HubError(Exception):
    """Custom exception for hub-related errors."""
    def __init__(self, message: str = "Hub error") -> None:
        """Conserve le message décrivant l’erreur de hub."""
        self.message = message
        super().__init__(self.message)
