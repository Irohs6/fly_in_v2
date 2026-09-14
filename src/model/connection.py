from .hub import Hub
from .errors import ConnectionError


class Connection:
    """Bidirectional connection with capacity and current occupancy."""
    def __init__(self, source: Hub, target: Hub, capacity: int | float):
        """Connect source and target with the given capacity and no
        occupants.
        """
        self.source = source
        self.target = target
        self.capacity = capacity
        self.nb_drones = 0

    def add_nb_drone(self) -> None:
        """Add one drone, raising ConnectionError if capacity would be
        exceeded.
        """
        if self.nb_drones + 1 > self.capacity:
            raise ConnectionError(
                "Cannot add more drones than the maximum allowed"
            )
        self.nb_drones += 1

    def is_available(self) -> bool:
        """Return whether the connection can accommodate one more drone."""
        return self.nb_drones < self.capacity

    def get_extremities(self, hub: Hub) -> Hub:
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
            f" capacity={self.capacity}, nb_drones={self.nb_drones})"
        )
