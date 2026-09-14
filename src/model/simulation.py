from .drone import Drone
from .graph import Graph
from .pathfinder import Dijkstra
from .hub import Hub
from .connection import Connection
from .recorder import Recorder


class Simulation:
    """Manage the drone simulation one turn at a time."""

    def __init__(
        self,
        graph: Graph,
        pathfinder: Dijkstra | None = None,
        *,
        record_replay: bool = True,
    ) -> None:
        """Initialize the simulation without loading drones. Use the
        supplied pathfinder or create Dijkstra. record_replay controls
        frame recording; movement logs are always retained.
        """
        self.graph = graph
        self.drones: list[Drone] = []
        self.turn = 0
        # Hub atteint ou connexion occupée, sans formatage terminal.
        self.movements_log: list[dict[int, Hub | Connection]] = []

        self.pathfinder = (
            pathfinder
            if pathfinder is not None
            else Dijkstra(graph)
        )
        self.recorder = Recorder()
        self.record_replay = record_replay

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
                current_position=self.graph.start_zone,
            )
            drone.set_path(path[1:])
            self.drones.append(drone)
            self.graph.start_zone.add_nb_drone()
        self._record_tour()

    # ==============================================================
    # DEPLACEMENT
    # ==============================================================

    def move_drone(
        self,
        drone: Drone,
        connection: Connection,
        target_zone: Hub,
    ) -> None:
        """Apply a move after capacity checks. Free the departure hub. For
        restricted hubs, start transit and reserve the destination;
        otherwise occupy the destination immediately. Raise RuntimeError
        if the drone is not in a hub.
        """
        current_zone = drone.current_position

        if isinstance(current_zone, Connection):
            raise RuntimeError(
                f"{drone.drone_id} has no current zone."
            )

        current_zone.remove_nb_drone()
        if target_zone.zone_type == "restricted":
            drone.begin_transit(
                connection,
                target_zone.transit_duration(),
            )

            target_zone.reserve()
        else:
            drone.move_to_zone(target_zone)
            target_zone.add_nb_drone()

        connection.add_nb_drone()

    # REROUTAGE

    def _reroute_drone(
        self,
        drone: Drone,
        blocked_zones: set[Hub],
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
            blocked_zones=blocked_zones,
            saturated_conns=saturated_connections,
        )

        if len(path) < 2:
            return False

        # Le chemin est disponible.
        drone.set_path(path[1:])
        drone.moving()

        return True

    # TENTATIVE DE DEPLACEMENT

    def _try_drone_move(
        self,
        drone: Drone,
        movements: dict[int, Hub | Connection],
    ) -> None:
        """Try to move a drone, rerouting immediately if the next passage is
        blocked. Wait if no alternative remains. Raise RuntimeError if
        the drone is in transit or has no path before arrival.
        """

        if isinstance(drone.current_position, Connection):
            raise RuntimeError(
                f"{drone.drone_id} has no current zone."
            )

        if not drone.path:
            raise RuntimeError(
                f"Drone {drone.drone_id}: empty path before arrival."
            )

        blocked_zones: set[Hub] = set()
        saturated_connections: set[tuple[Hub, Hub]] = set()
        # Le reroutage ne doit pas revenir au hub précédent.
        if drone.previous_zone is not None:
            blocked_zones.add(drone.previous_zone)

        while True:
            target_zone = drone.path[0]
            connection = self.graph.get_connection(
                drone.current_position, target_zone,
            )

            if connection is None:
                blocked_zones.add(target_zone)
            else:
                zone_available = target_zone.is_available()
                connection_available = connection.is_available()
                if zone_available and connection_available:
                    self.move_drone(drone, connection, target_zone)
                    movements[drone.drone_id] = drone.current_position
                    return

                if not zone_available:
                    blocked_zones.add(target_zone)
                if not connection_available:
                    saturated_connections.add(
                        (connection.source, connection.target)
                    )

            if not self._reroute_drone(
                drone, blocked_zones, saturated_connections,
            ):
                drone.wait()
                return

    # SIMULATION

    def _all_drones_delivered(self) -> bool:
        """Return whether all drones have reached the destination."""
        return all(
            drone.current_position == self.graph.end_zone
            for drone in self.drones
        )

    def _process_drone(
        self,
        drone: Drone,
        movements: dict[int, Hub | Connection],
    ) -> None:
        """Process a drone during the current turn."""
        if drone.current_position == self.graph.end_zone:
            drone.deliver()
            return

        if isinstance(drone.current_position, Connection):
            self._process_transit(drone, movements)
        else:
            self._try_drone_move(drone, movements)

        if drone.current_position == self.graph.end_zone:
            drone.deliver()

    def _process_transit(
        self,
        drone: Drone,
        movements: dict[int, Hub | Connection],
    ) -> None:
        """Advance a drone currently in transit."""

        destination = drone.advance_transit()

        if destination is None:
            return

        destination.release_reservation()
        destination.add_nb_drone()

        movements[drone.drone_id] = destination

    def _update_connections(self) -> None:
        """Retain only connection occupancy from ongoing transits."""
        for connection in self.graph.connections:
            connection.nb_drones = 0
        for drone in self.drones:
            if isinstance(drone.current_position, Connection):
                drone.current_position.add_nb_drone()

    def simulate(self) -> list[dict[int, Hub | Connection]]:
        """Simulate drone movements one turn at a time."""
        while not self._all_drones_delivered():
            movements: dict[int, Hub | Connection] = {}
            self.movements_log.append(movements)

            for drone in sorted(
                self.drones,
                key=lambda drone: drone.path_turns()
            ):
                self._process_drone(
                    drone,
                    movements
                )
            self._update_connections()

            self.turn += 1
            self._record_tour()
        return self.movements_log

    # ==============================================================
    # RECORD
    # ==============================================================

    def _record_tour(self) -> None:
        """Record the current turn when record_replay is enabled."""

        if not self.record_replay:
            return
        self.recorder.record(
            self.turn,
            self.drones,
            self.graph.hubs,
        )
