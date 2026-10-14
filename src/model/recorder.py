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
            if isinstance(position, Connection):
                transits[(position.source.name, position.target.name)] += 1
            drone_states[drone.drone_id] = DroneState(
                current_position=(position.source.name, position.target.name)
                if isinstance(position, Connection) else position.name,
                previous_zone=drone.previous_zone.name
                if drone.previous_zone is not None else None,
                path=tuple(hub.name for hub in drone.path),
                status=drone.status,
                transit_duration=drone.transit_duration,
                transit_turns=drone.transit_turns,
            )

        self.frames.append(TurnState(
            turn=turn,
            start_hub=graph.start_hub.name,
            end_hub=graph.end_hub.name,
            drones=drone_states,
            hubs={
                hub.name: HubState(
                    name=hub.name, x=hub.x, y=hub.y, color=hub.color,
                    zone_type=hub.zone_type, capacity=hub.capacity,
                    nb_drones=hub.nb_drones, reserved=hub.reserved,
                )
                for hub in graph.hubs.values()
            },
            connections={
                (conn.source.name, conn.target.name): ConnectionState(
                    source=conn.source.name, target=conn.target.name,
                    capacity=conn.capacity, used_capacity=conn.used_capacity,
                    in_transit=transits[(conn.source.name, conn.target.name)],
                )
                for conn in graph.connections
            },
            moved_drones=moved_drones,
        ))
