from collections import Counter

from .connection import Connection
from .drone import Drone
from .graph import Graph
from .state import ConnectionState, DroneState, HubState, TurnState


class Recorder:
    """Store complete, independent turn states for every output view."""

    def __init__(self) -> None:
        """Initialize the shared simulation history."""
        self.frames: list[TurnState] = []

    def record(
        self,
        turn: int,
        graph: Graph,
        drones: list[Drone],
        moved_drones: tuple[int, ...] = (),
    ) -> None:
        """Copy the full model state before turn capacity counters reset."""
        drone_states: dict[int, DroneState] = {}
        transits: Counter[tuple[str, str]] = Counter()
        for drone in drones:
            position = drone.current_position
            current_position: str | tuple[str, str]
            if isinstance(position, Connection):
                current_position = (position.source.name, position.target.name)
                transits[current_position] += 1
            else:
                current_position = position.name
            drone_states[drone.drone_id] = DroneState(
                current_position=current_position,
                previous_zone=drone.previous_zone.name
                if drone.previous_zone is not None else None,
                path=tuple(hub.name for hub in drone.path),
                status=drone.status,
            )

        hub_states = {
            hub.name: HubState(
                name=hub.name, x=hub.x, y=hub.y, color=hub.color,
                zone_type=hub.zone_type, capacity=hub.capacity,
                nb_drones=hub.nb_drones, reserved=hub.reserved,
            )
            for hub in graph.hubs.values()
        }
        connection_states = {
            (connection.source.name, connection.target.name): ConnectionState(
                source=connection.source.name, target=connection.target.name,
                capacity=connection.capacity,
                used_capacity=connection.used_capacity,
                in_transit=transits[
                    (connection.source.name, connection.target.name)
                ],
            )
            for connection in graph.connections
        }

        self.frames.append(TurnState(
            turn=turn,
            start_hub=graph.start_hub.name,
            end_hub=graph.end_hub.name,
            drones=drone_states,
            hubs=hub_states,
            connections=connection_states,
            moved_drones=moved_drones,
        ))
