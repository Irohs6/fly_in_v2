from .errors import HubError


class Hub:
    def __init__(self, name: str, color: str = "white",
                 zone_type: str = "normal", capacity: int | float = 1,
                 x: int = 0, y: int = 0) -> None:

        self.name = name
        self.color = color
        self.zone_type = zone_type
        self.capacity = capacity
        self.x = x
        self.y = y
        self.nb_drone = 0
        self.reserved = 0

    def set_zone_type(self, zone_type: str) -> None:
        self.zone_type = zone_type

    def set_capacity(self, capacity: int | float) -> None:
        if not isinstance(capacity, (int, float)) or capacity < 0:
            raise HubError("Capacity must be a non-negative number")
        self.capacity = capacity

    def add_nb_drone(self) -> None:
        """Ajoute toujours 1 drone, jamais plus."""
        if self.nb_drone + 1 + self.reserved > self.capacity:
            raise HubError("Cannot add more drones than the maximum allowed")
        self.nb_drone += 1

    def remove_nb_drone(self) -> None:
        """Retire toujours 1 drone."""
        if self.nb_drone - 1 < 0:
            raise HubError("Cannot remove more drones than currently present")
        self.nb_drone -= 1

    def is_available(self) -> bool:
        return self.nb_drone + self.reserved < self.capacity

    def reserve(self) -> None:
        if (
            self.nb_drone
            + self.reserved
            + 1
            > self.capacity
        ):
            raise HubError(
                "Cannot reserve more than hub capacity"
            )

        self.reserved += 1

    def release_reservation(self) -> None:
        if self.reserved == 0:
            raise HubError(
                "No reservation to release"
            )

        self.reserved -= 1

    def move_cost(self) -> float:
        """Calculate the cost of moving to this hub based on its zone type."""
        if self.zone_type == "restricted":
            return 2.0
        elif self.zone_type == "blocked":
            return float("inf")
        elif self.zone_type == "priority":
            return 0.9
        return 1.0

    def transit_duration(self) -> int:
        if self.zone_type == "restricted":
            return 2

        return 1

    def __str__(self) -> str:
        return (
            f"Hub(name={self.name}, color={self.color}, "
            f"zone_type={self.zone_type}, capacity={self.capacity}, "
            f"nb_drone={self.nb_drone}, x={self.x}, y={self.y})"
        )

    def __repr__(self) -> str:
        return self.__str__()
