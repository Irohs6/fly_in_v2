from .drone import Drone
from .hub import Hub
from .replay import DroneReplayState, ReplayFrame


class Recorder:

    def __init__(self) -> None:
        self.frames: list[ReplayFrame] = []

    def record(
        self,
        turn: int,
        drones: list[Drone],
        hubs: dict[str, Hub],
    ) -> None:
        drone_states: dict[str, DroneReplayState] = {}

        for drone in drones:
            state = self._drone_state(drone)

            drone_states[drone.drone_id] = state

        hub_counts = {
            name: hub.nb_drone
            for name, hub in hubs.items()
        }

        frame = ReplayFrame(
            turn=turn,
            drones=drone_states,
            hub_counts=hub_counts,
        )

        self.frames.append(frame)

    def _drone_state(
        self,
        drone: Drone,
    ) -> DroneReplayState:

        if drone.in_transit:
            return self._transit_state(drone)

        if drone.current_zone is None:
            raise RuntimeError(
                f"{drone.drone_id} has no current zone."
            )

        zone_name = drone.current_zone.name

        return DroneReplayState(
            drone_id=drone.drone_id,
            source=zone_name,
            target=zone_name,
            progress=1.0,
            status=drone.status,
        )

    def _transit_state(
        self,
        drone: Drone,
    ) -> DroneReplayState:

        if (
            drone.previous_zone is None
            or drone.moving_connection is None
        ):
            raise RuntimeError(
                f"Invalid transit state for {drone.drone_id}."
            )

        source = drone.previous_zone

        target = (
            drone.moving_connection.get_other_hub(source)
        )

        progress = 0.0

        if drone.transit_cost > 0:
            progress = (
                drone.transit_turns
                / drone.transit_cost
            )

        progress = max(
            0.0,
            min(1.0, progress),
        )

        return DroneReplayState(
            drone_id=drone.drone_id,
            source=source.name,
            target=target.name,
            progress=progress,
            status=drone.status,
        )
