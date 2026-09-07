from .drone import Drone
from .graph import Graph
from .pathfinder import Dijkstra
from .hub import Hub
from .connection import Connection
from .recorder import Recorder


class Simulation:
    """Gère la simulation tour par tour des drones."""

    def __init__(
        self,
        graph: Graph,
        pathfinder: Dijkstra | None = None,
    ) -> None:
        self.graph = graph
        self.drones: list[Drone] = []
        self.turn = 0.
        self.movements_log: list[dict[str, str]] = []

        self.ph = (
            pathfinder
            if pathfinder is not None
            else Dijkstra(graph)
        )
        self.recorder = Recorder()

    def load_drones(self, nb_drones: int) -> None:
        """Crée les drones dans le hub de départ."""
        if self.drones:
            raise RuntimeError(
                "Drones have already been loaded."
            )
        path = self.ph.shortest_path()

        for index in range(nb_drones):
            drone = Drone(
                index + 1,
                current_zone=self.graph.start_zone,
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
        """Demande au drone de se déplacer vers une zone cible """

        if target_zone.zone_type == "restricted":
            drone.current_zone.remove_nb_drone()

            drone.begin_transit(
                connection,
                target_zone.transit_duration(),
            )

            connection.add_nb_drone()
            target_zone.add_nb_drone()

            return

        drone.current_zone.remove_nb_drone()
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
        """
        Cherche un autre chemin pendant le même tour.

        Dijkstra doit respecter :
        - les zones bloquées ;
        - les connexions saturées.
        """

        if drone.current_zone is None:
            return False

        path = self.ph.shortest_path(
            source=drone.current_zone,
            blocked_zones=blocked_zones,
            saturated_conns=saturated_connections,
        )

        if not path or len(path) < 2:
            return False

        # Le chemin est disponible.
        drone.set_path(path[1:])
        drone.moving()

        return True

    # TENTATIVE DE DEPLACEMENT

    def _try_drone_move(
        self,
        drone: Drone,
        movements: dict[str, str],
    ) -> None:
        """
        Essaie de faire avancer un drone.

        Si le chemin est bloqué, Dijkstra cherche immédiatement
        le prochain chemin différent disponible.
        """

        if drone.current_zone is None:
            raise RuntimeError(
                f"{drone.drone_id} has no current zone."
            )

        # Ressources bloquées uniquement pour ce tour.-
        blocked_zones: set[Hub] = set()

        saturated_connections: set[
            tuple[Hub, Hub]
        ] = set()

        # Empêche le drone de repartir immédiatement en arrière.
        if drone.previous_zone is not None:
            blocked_zones.add(drone.previous_zone)

        while True:
            if not drone.path:
                drone.wait()
                return

            target_zone = drone.path[0]

            connection = self.graph.get_connection(
                drone.current_zone,
                target_zone,
            )

            if connection is None:
                blocked_zones.add(target_zone)

                if not self._reroute_drone(
                    drone,
                    blocked_zones,
                    saturated_connections,
                ):
                    drone.wait()
                    return
                continue

            zone_available = target_zone.is_available()
            connection_available = connection.is_available()

            if not zone_available or not connection_available:
                if not zone_available:
                    blocked_zones.add(target_zone)

                if not connection_available:
                    saturated_connections.add(
                        (connection.source, connection.target)
                    )

                found = self._reroute_drone(
                    drone,
                    blocked_zones,
                    saturated_connections,
                )

                if not found:
                    drone.wait()
                    return
                continue

            old_zone = drone.current_zone

            # Tentative de déplacement.
            self.move_drone(
                drone,
                connection,
                target_zone,
            )

            # Déplacement normal terminé.
            if not drone.in_transit:

                movements[drone.drone_id] = (
                    f"{old_zone.name} -> "
                    f"{target_zone.name}"
                )

                return
            movements[drone.drone_id] = (
                f"{old_zone.name} -> "
                f"{target_zone.name} [TRANSIT]"
            )

            return

    # SIMULATION

    def _all_drones_delivered(self) -> bool:
        """Retourne True si tous les drones sont arrivés."""
        return all(
            drone.current_zone == self.graph.end_zone
            for drone in self.drones
        )

    def _process_drone(
        self,
        drone: Drone,
        movements: dict[str, str],
    ) -> None:
        """Traite un drone pendant le tour courant."""
        if drone.current_zone == self.graph.end_zone:
            drone.deliver()
            return

        if drone.in_transit:
            self._process_transit(drone, movements)
            return

        self._try_drone_move(drone, movements)

    def _process_transit(
        self,
        drone: Drone,
        movements: dict[str, str],
    ) -> None:
        """Fait progresser un drone actuellement en transit."""

        old_zone = drone.previous_zone

        destination = drone.advance_transit()

        if destination is None:
            return

        if old_zone is not None:
            movements[drone.drone_id] = (
                f"{old_zone.name} -> "
                f"{destination.name}"
            )

    def _update_connections(self) -> None:
        """Met à jour l'occupation des connexions."""
        active_transits: dict[Connection, int] = {}

        for drone in self.drones:
            if (
                drone.in_transit
                and drone.moving_connection is not None
            ):
                connection = drone.moving_connection

                active_transits[connection] = (
                    active_transits.get(connection, 0) + 1
                )
        for connection in self.graph.connections:
            connection.nb_drones = active_transits.get(connection, 0)

    def simulate(self) -> list[dict[str, str]]:
        """Simule le déplacement des drones tour par tour."""
        while not self._all_drones_delivered():
            movements: dict[str, str] = {}
            self.movements_log.append(movements)

            for drone in self.drones:
                self._process_drone(drone, movements)
            self._update_connections()

            self.turn += 1
            self._record_tour()
        return self.movements_log

    # ==============================================================
    # RECORD
    # ==============================================================

    def _record_tour(self) -> None:
        """Enregistre l'état courant pour le replay."""

        self.recorder.record(
            self.turn,
            self.drones,
            self.graph.hubs,
        )
