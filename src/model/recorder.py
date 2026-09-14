from .drone import Drone
from .hub import Hub
from .connection import Connection
from .replay import (
    DroneReplayState,
    HubReplayState,
    ReplayFrame,
)


class Recorder:

    """Collect drone and hub states for replay."""
    def __init__(self) -> None:
        """Initialize an empty list of recorded frames."""
        self.frames: list[ReplayFrame] = []

    def record(
        self,
        turn: int,
        drones: list[Drone],
        hubs: dict[str, Hub],
    ) -> None:
        """Append a frame with the current drone and hub states. Copy values
        into independent replay states without modifying the graph or
        drones.
        """
        drone_states = {
            drone.drone_id: self._drone_state(drone)
            for drone in drones
        }
        hub_states = {
            hub_id: HubReplayState(hub.nb_drone, hub.capacity)
            for hub_id, hub in hubs.items()
        }
        self.frames.append(ReplayFrame(turn, drone_states, hub_states))

    def _drone_state(
        self,
        drone: Drone,
    ) -> DroneReplayState:

        """Return the replay state for a drone in a hub or in transit."""
        if isinstance(drone.current_position, Connection):
            return self._transit_state(drone)

        zone_name = drone.current_position.name

        return DroneReplayState(
            source=zone_name,
            target=zone_name,
            progress=1.0,
            status=drone.status,
        )

    def _transit_state(
        self,
        drone: Drone,
    ) -> DroneReplayState:

        """Return transit endpoints and progress clamped between zero and
        one. Raise RuntimeError if the departure hub or connection is
        missing.
        """
        if (
            drone.previous_zone is None
            or not isinstance(drone.current_position, Connection)
        ):
            raise RuntimeError(
                f"Invalid transit state for {drone.drone_id}."
            )

        source = drone.previous_zone

        target = drone.current_position.get_extremities(source)

        progress = 0.0

        if drone.transit_duration > 0:
            progress = (
                drone.transit_turns
                / drone.transit_duration
            )

        progress = max(
            0.0,
            min(1.0, progress),
        )

        return DroneReplayState(
            source=source.name,
            target=target.name,
            progress=progress,
            status=drone.status,
        )
