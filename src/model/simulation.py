from .drone import Drone
from .graph import Graph
from .pathfinder import Dijkstra
from .hub import Hub
from .connection import Connection
from .recorder import Recorder
from .state import TurnState


class Simulation:
    """Manage the drone simulation one turn at a time."""

    def __init__(
        self,
        graph: Graph,
        pathfinder: Dijkstra | None = None,
    ) -> None:
        """Initialize the simulation without loading drones. Use the
        supplied pathfinder or create Dijkstra. The recorder stores the
        initial state and every completed turn for all views.
        """
        self.graph = graph
        self.drones: list[Drone] = []
        self.turn = 0
        self.pathfinder = (
            pathfinder
            if pathfinder is not None
            else Dijkstra(graph)
        )
        self.recorder = Recorder()

    def load_drones(self, nb_drones: int) -> None:
        """Create drones in the starting hub."""
        if self.drones:
            raise RuntimeError(
                "Drones have already been loaded."
            )
        path = self.pathfinder.shortest_path()

        for index in range(nb_drones):
            drone = Drone(
                index + 1,
                current_position=self.graph.start_hub,
            )
            drone.set_path(path[1:])
            self.drones.append(drone)
            self.graph.start_hub.add_drone()
        self.recorder.record(self.turn, self.graph, self.drones)

    # ==============================================================
    # MOVEMENT
    # ==============================================================

    def move_drone(
        self,
        drone: Drone,
        connection: Connection,
        target_hub: Hub,
    ) -> None:
        """Apply a move after capacity checks. Free the departure hub. For
        restricted hubs, start transit and reserve the destination;
        otherwise occupy the destination immediately. Raise RuntimeError
        if the drone is not in a hub.
        """
        current_hub = drone.current_position

        if isinstance(current_hub, Connection):
            raise RuntimeError(
                f"{drone.drone_id} has no current zone."
            )

        current_hub.remove_drone()
        if target_hub.zone_type == "restricted":
            drone.begin_transit(connection)

            target_hub.reserve()
        else:
            drone.move_to_zone(target_hub)
            target_hub.add_drone()

        connection.use_capacity()

    # REROUTING

    def _reroute_drone(
        self,
        drone: Drone,
        blocked_hubs: set[Hub],
        saturated_connections: set[
            tuple[Hub, Hub]
        ],
    ) -> bool:
        """Find an alternative path during the same turn, excluding blocked
        hubs and saturated connections.
        """

        if isinstance(drone.current_position, Connection):
            return False

        path = self.pathfinder.shortest_path(
            source=drone.current_position,
            blocked_hubs=blocked_hubs,
            saturated_connections=saturated_connections,
        )

        if len(path) < 2:
            return False

        # An alternative path was found.
        drone.set_path(path[1:])

        return True

    # MOVE OR WAIT

    def _move_or_wait(
        self,
        drone: Drone,
    ) -> bool:
        """Try to move a drone, rerouting immediately if the next passage is
        blocked. Return whether a move occurred; wait if no alternative
        remains. Raise RuntimeError if the drone is in transit or has no
        path before arrival.
        """

        if isinstance(drone.current_position, Connection):
            raise RuntimeError(
                f"{drone.drone_id} has no current zone."
            )

        if not drone.path:
            raise RuntimeError(
                f"Drone {drone.drone_id}: empty path before arrival."
            )

        original_path = drone.path.copy()
        original_cost = drone.path_turns()

        blocked_hubs: set[Hub] = set()
        saturated_connections: set[tuple[Hub, Hub]] = set()
        # Rerouting must not return to the previous hub.
        if drone.previous_zone is not None:
            blocked_hubs.add(drone.previous_zone)

        while True:
            target_hub = drone.path[0]
            connection = self.graph.get_connection(
                drone.current_position, target_hub,
            )

            if connection is None:
                blocked_hubs.add(target_hub)
            else:
                zone_available = target_hub.is_available()
                connection_available = connection.is_available()
                if zone_available and connection_available:
                    self.move_drone(drone, connection, target_hub)
                    return True

                if not zone_available:
                    blocked_hubs.add(target_hub)
                if not connection_available:
                    saturated_connections.add(
                        (connection.source, connection.target)
                    )

            if not self._reroute_drone(
                drone, blocked_hubs, saturated_connections,
            ):
                drone.wait()
                return False

            # Waiting is preferable to an excessively long detour.
            if drone.path_turns() > original_cost + 2:
                drone.set_path(original_path)
                drone.wait()
                return False

    # SIMULATION

    def _all_drones_delivered(self) -> bool:
        """Return whether all drones have reached the destination."""
        return all(
            drone.current_position == self.graph.end_hub
            for drone in self.drones
        )

    def _advance_drone(
        self,
        drone: Drone,
    ) -> bool:
        """Advance a drone for one turn and report whether it moved."""
        if drone.current_position == self.graph.end_hub:
            drone.deliver()
            return False

        if isinstance(drone.current_position, Connection):
            destination = drone.advance_transit()
            if destination is not None:
                destination.release_reservation()
                destination.add_drone()
            moved = True
        else:
            moved = self._move_or_wait(drone)

        if drone.current_position == self.graph.end_hub:
            drone.deliver()
        return moved

    def _prepare_connections_for_turn(self) -> None:
        """Prepare a new turn, retaining only ongoing transit occupancy."""
        for connection in self.graph.connections:
            connection.used_capacity = 0
        for drone in self.drones:
            if isinstance(drone.current_position, Connection):
                drone.current_position.use_capacity()

    def simulate(self) -> list[TurnState]:
        """Run to completion and return the initial and completed states."""
        while not self._all_drones_delivered():
            self._prepare_connections_for_turn()
            moved_drones = []
            for drone in sorted(
                self.drones, key=lambda drone: drone.path_turns(),
            ):
                if self._advance_drone(drone):
                    moved_drones.append(drone.drone_id)
            self.turn += 1
            self.recorder.record(
                self.turn, self.graph, self.drones, tuple(moved_drones),
            )
        return self.recorder.frames
