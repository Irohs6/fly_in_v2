from .hub import Hub
from .connection import Connection


class Drone:
    def __init__(
        self,
        drone_id: int,
        current_zone: Hub
    ) -> None:
        self.drone_id = drone_id

        self.current_zone: Hub = current_zone
        self.previous_zone: Hub | None = None

        self.path: list[Hub] = []
        self.status: str = "idle"

        self.in_transit = False
        self.transit_cost = 0
        self.transit_turns = 0

        self.moving_connection: Connection | None = None

        self.traveled_path: list[Hub] = []

    def move_to_zone(
        self,
        zone: Hub,
    ) -> None:
        if self.current_zone is None:
            raise RuntimeError(
                f"Drone {self.drone_id} is not currently in any hub."
            )
        old_zone = self.current_zone

        self.previous_zone = old_zone
        self.current_zone = zone

        self.traveled_path.append(zone)
        self._complete_path_step(zone)

        self.status = "moving"

    def begin_transit(
        self,
        connection: Connection,
        duration: int,
    ) -> None:
        if self.current_zone is None:
            raise RuntimeError(
                f"Drone {self.drone_id} is already in transit."
            )
        old_zone = self.current_zone

        self.previous_zone = old_zone
        self.current_zone = None
        # Drone is now in transit, so current_zone is temporarily None

        self.moving_connection = connection

        self.in_transit = True

        self.transit_cost = duration

        # le premier tour de deplqcement vien de commencer.
        self.transit_turns = 1

        self.status = "in_transit"

    def advance_transit(self) -> Hub | None:
        if not self.in_transit:
            return None

        self.transit_turns += 1

        if self.transit_turns < self.transit_cost:
            return None

        return self.finish_transit()

    def finish_transit(self) -> Hub:
        if self.moving_connection is None:
            raise RuntimeError(
                f"{self.drone_id} has no moving connection."
            )

        if self.previous_zone is None:
            raise RuntimeError(
                f"{self.drone_id} has no previous zone."
            )

        connection = self.moving_connection

        destination = connection.get_other_hub(
            self.previous_zone
        )

        self.current_zone = destination

        self.in_transit = False

        self.transit_cost = 0
        self.transit_turns = 0

        self.moving_connection = None

        self.traveled_path.append(destination)
        self._complete_path_step(destination)

        self.status = "moving"

        return destination

    def wait(self) -> None:
        self.status = "waiting"

    def reroute(self) -> None:
        self.status = "rerouting"

    def moving(self) -> None:
        self.status = "moving"

    def idle(self) -> None:
        self.status = "idle"

    def deliver(self) -> None:
        self.status = "delivered"

    def set_path(self, path: list[Hub]) -> None:
        self.path = path.copy()

    def _complete_path_step(self, zone: Hub) -> None:
        if self.path and self.path[0] is zone:
            self.path.pop(0)
