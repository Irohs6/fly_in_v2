from .hub import Hub
from .errors import ConnectionError


class Connection:
    """Bidirectional connection with capacity usage for the current turn."""
    def __init__(self, source: Hub, target: Hub, capacity: int | float):
        """Connect source and target with the given capacity and no usage.
        """
        self.source = source
        self.target = target
        self.capacity = capacity
        self.used_capacity = 0

    def use_capacity(self) -> None:
        """Use one unit of capacity for the current turn.
        Raise ConnectionError if capacity would be exceeded.
        """
        if not self.is_available():
            raise ConnectionError(
                "Cannot add more drones than the maximum allowed"
            )
        self.used_capacity += 1

    def is_available(self) -> bool:
        """Return whether another unit of capacity is available this turn."""
        return self.used_capacity < self.capacity

    def get_other_hub(self, hub: Hub) -> Hub:
        """Return the opposite hub. Raise ConnectionError if hub is not an
        endpoint.
        """
        if self.source is hub:
            return self.target

        if self.target is hub:
            return self.source

        raise ConnectionError(
            f"Hub {hub.name} is not connected by this connection."
        )

    def __repr__(self) -> str:
        """Return a detailed connection representation for debugging."""
        return (
            f"Connection(source={self.source.name}, target={self.target.name},"
            f" capacity={self.capacity}, used_capacity={self.used_capacity})"
        )
