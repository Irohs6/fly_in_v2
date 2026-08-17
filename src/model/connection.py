from .hub import Hub
from .errors import ConnectionError


class Connection:
    __slots__ = [
        "source",
        "target",
        "capacity",
        "nb_drones",
    ]

    def __init__(
        self,
        source: Hub,
        target: Hub,
        capacity: int | float = 1
    ) -> None:

        if capacity < 0:
            raise ConnectionError(
                "Capacity must be a non-negative number"
            )

        self.source = source
        self.target = target
        self.capacity = capacity
        self.nb_drones = 0

    def set_capacity(
        self,
        capacity: int | float
    ) -> None:

        if capacity < 0:
            raise ConnectionError(
                "Capacity must be a non-negative number"
            )

        self.capacity = capacity

    def add_drone(self) -> None:
        """Ajoute un drone sur la connexion."""

        if self.nb_drones >= self.capacity:
            raise ConnectionError(
                "Cannot add more drones than the "
                "maximum capacity"
            )

        self.nb_drones += 1

    def remove_drone(self) -> None:
        """Retire un drone de la connexion."""

        if self.nb_drones <= 0:
            raise ConnectionError(
                "Cannot remove more drones than "
                "currently present"
            )

        self.nb_drones -= 1

    def __str__(self) -> str:
        return (
            f"Connection("
            f"source={self.source.name}, "
            f"target={self.target.name}, "
            f"capacity={self.capacity}, "
            f"nb_drones={self.nb_drones})"
        )

    def __repr__(self) -> str:
        return self.__str__()