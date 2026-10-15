from .hub import Hub
from .connection import Connection


class Drone:
    """Drone position, remaining path and transit state. Simulation manages
    hub and connection occupancy.
    """
    def __init__(
        self,
        drone_id: int,
        current_position: Hub
    ) -> None:
        """Place the drone in a hub with no path or active transit."""
        self.drone_id = drone_id

        self.current_position: Hub | Connection = current_position
        self.previous_zone: Hub | None = None

        self.path: list[Hub] = []
        self.status: str = "idle"

    def move_to_zone(
        self,
        zone: Hub,
    ) -> None:
        """Move to zone, consume the next path step and set the status to
        moving. Store the previous hub; raise RuntimeError if the drone
        is not in a hub.
        """
        if isinstance(self.current_position, Connection):
            raise RuntimeError(
                f"Drone {self.drone_id} is not currently in any hub."
            )
        self.previous_zone = self.current_position
        self.current_position = zone

        self.path.pop(0)

        self.status = "moving"

    def begin_transit(
        self,
        connection: Connection,
    ) -> None:
        """Start a two-turn move to a restricted hub on connection. Store
        the departure hub; arrival occurs on the next simulation turn.
        Raise RuntimeError without a departure hub. Simulation manages
        reservations and capacity.
        """
        if isinstance(self.current_position, Connection):
            raise RuntimeError(
                f"Drone {self.drone_id} is already in transit."
            )
        self.previous_zone = self.current_position
        self.current_position = connection
        self.status = "in_transit"

    def advance_transit(self) -> Hub | None:
        """Complete a restricted move on the turn after departure.

        Return the destination, or None when there is no active transit.
        Consume the path step and raise RuntimeError if departure is missing.
        """
        if not isinstance(self.current_position, Connection):
            return None

        if self.previous_zone is None:
            raise RuntimeError(
                f"Drone {self.drone_id}: missing connection or departure hub."
            )

        destination = self.current_position.get_other_hub(
            self.previous_zone)
        self.current_position = destination
        self.path.pop(0)
        self.status = "moving"

        return destination

    def wait(self) -> None:
        """Mark the drone as waiting without changing its position."""
        self.status = "waiting"

    def deliver(self) -> None:
        """Mark the drone as delivered without changing its position."""
        self.status = "delivered"

    def path_turns(self) -> int:
        """Sum the travel durations of the remaining path. Time already
        spent in transit is not subtracted.
        """
        return sum(
            zone.transit_duration()
            for zone in self.path
        )

    def set_path(self, path: list[Hub]) -> None:
        """Replace the remaining path with a copy of path."""
        self.path = path.copy()
