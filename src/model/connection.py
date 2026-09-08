from .hub import Hub
from .errors import ConnectionError


class Connection:
    def __init__(self, source: Hub, target: Hub, capacity: int | float):
        self.source = source
        self.target = target
        self.capacity = capacity
        self.nb_drones = 0

    def add_nb_drone(self) -> None:
        """Ajoute toujours 1 drone, jamais plus."""
        if self.nb_drones + 1 > self.capacity:
            raise ConnectionError(
                "Cannot add more drones than the maximum allowed"
            )
        self.nb_drones += 1

    def is_available(self) -> bool:
        return self.nb_drones < self.capacity

    def connects(self, source: Hub, target: Hub) -> bool:
        return (
            (self.source is source and self.target is target)
            or (self.source is target and self.target is source)
        )

    def get_other_hub(self, hub: Hub) -> Hub:
        if self.source is hub:
            return self.target

        if self.target is hub:
            return self.source

        raise ConnectionError(
            f"Hub {hub.name} is not connected by this connection."
        )

    def __str__(self) -> str:
        return (
            f"Connection(source={self.source.name}, target={self.target.name},"
            f" capacity={self.capacity}, nb_drones={self.nb_drones})"
        )

    def __repr__(self) -> str:
        return (
            f"Connection(source={self.source.name}, target={self.target.name},"
            f" capacity={self.capacity}, nb_drones={self.nb_drones})"
        )
