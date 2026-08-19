from .hub import Hub
from .connection import Connection


class Drone:
    def __init__(
        self,
        drone_id: str,
        current_zone: Hub | None = None
    ) -> None:
        self.drone_id = drone_id
        self.current_zone = current_zone
        self.previous_zone: Hub | None = None

        self.path: list[Hub] = []
        self.status: str = "idle"

        self.destination: Hub | None = None
        self.in_transit = False
        self.transit_cost = 0
        self.traveled_path: list[Hub] = []
        if current_zone is not None:
            self.traveled_path.append(current_zone)
        self.moving_connection: Connection | None = None

    def begin_transit(
        self,
        connection: Connection,
        cost: int,
        destination: Hub
    ) -> None:
        self.in_transit = True
        self.transit_cost = cost
        self.previous_zone = self.current_zone
        self.destination = destination
        self.current_zone = destination
        self.moving_connection = connection
        self.status = "in_transit"

    def finish_transit(
        self,
        zone: Hub
    ) -> None:
        self.in_transit = False
        self.transit_cost = 0
        self.destination = None
        self.moving_connection = None
        self.traveled_path.append(zone)
        self.status = "moving"

    def move_to_zone(
        self,
        zone: Hub,
    ) -> None:
        self.previous_zone = self.current_zone
        self.current_zone = zone
        self.traveled_path.append(zone)
        self.status = "moving"
