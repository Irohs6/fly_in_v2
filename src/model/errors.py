
class ConnectionError(Exception):
    """Custom exception for connection-related errors."""
    def __init__(self, message: str = "Connection error") -> None:
        self.message = message
        super().__init__(self.message)


class HubError(Exception):
    """Custom exception for hub-related errors."""
    def __init__(self, message: str = "Hub error") -> None:
        self.message = message
        super().__init__(self.message)


class GraphError(Exception):
    """Custom exception for graph-related errors."""
    def __init__(self, message: str = "Graph error") -> None:
        self.message = message
        super().__init__(self.message)
