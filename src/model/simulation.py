from .drone import Drone
from .graph import Graph
from .pathfinder import Dijkstra
from .hub import Hub
from .connection import Connection


class Simulation:
    """Gère la simulation tour par tour des drones."""

    def __init__(
        self,
        graph: Graph,
        debug: bool,
        pathfinder: Dijkstra | None = None,
    ) -> None:
        self.graph = graph
        self.drones: list[Drone] = []
        self.turn = 0
        self.debug = debug

        self.ph = (
            pathfinder
            if pathfinder is not None
            else Dijkstra(graph)
        )

        self.tours: list[dict[str, str | None]] = []
        self.replay_frames: list[dict[str, object]] = []

        # Connexions restricted encore occupées.
        # Valeur = nombre de tours restants avant libération.
        self.restricted_connections: dict[Connection, int] = {}

    def load_drones(self, nb_drones: int) -> None:
        """Crée les drones dans le hub de départ."""

        if self.graph.start_zone is None:
            raise ValueError("Hub de départ introuvable.")

        path = self.ph.shortest_path()

        if not path:
            raise ValueError(
                "Aucun chemin vers le hub final."
            )

        for index in range(nb_drones):
            drone = Drone(
                f"D_{index + 1}",
                current_zone=self.graph.start_zone,
            )

            drone.path = path[1:].copy()

            self.drones.append(drone)
            self.graph.start_zone.add_nb_drone()

        self._record_tour()

    # ==============================================================
    # DEPLACEMENT
    # ==============================================================

    def move_to_restricted_zone(
        self,
        drone: Drone,
        connection: Connection,
        target_zone: Hub,
    ) -> None:
        """Gère l'entrée et la sortie d'une zone restricted."""

        if target_zone.zone_type != "restricted":
            raise ValueError(
                "The target zone is not restricted."
            )

        # Le drone termine son transit.
        if drone.in_transit:
            drone.finish_transit(target_zone)
            return

        # Vérification de la connexion ET de la zone.
        conn_ok = (
            connection.nb_drones
            < connection.capacity
        )

        zone_ok = (
            target_zone.nb_drone
            < target_zone.capacity
        )

        # Les deux doivent être disponibles.
        if not conn_ok or not zone_ok:
            drone.status = "rerouting"
            return

        old_zone = drone.current_zone

        # Réservation immédiate de la connexion et de la zone.
        connection.add_nb_drone()
        target_zone.add_nb_drone()

        # La connexion restricted reste occupée pendant 2 tours.
        self.restricted_connections[connection] = 2

        if old_zone is not None:
            old_zone.remove_nb_drone()

        drone.begin_transit(
            connection,
            target_zone.move_cost(),
            target_zone,
        )

    def move_drone(
        self,
        drone: Drone,
        connection: Connection,
        target_zone: Hub,
    ) -> None:
        """Déplace un drone vers une zone."""

        if target_zone.zone_type == "restricted":
            self.move_to_restricted_zone(
                drone,
                connection,
                target_zone,
            )
            return

        if target_zone.zone_type == "blocked":
            raise ValueError(
                "Cannot move to a blocked zone."
            )
        # Zone normale pleine.
        if target_zone.nb_drone >= target_zone.capacity:
            drone.status = "rerouting"
            return
        # connexion pleine.
        if connection.nb_drones >= connection.capacity:
            drone.status = "rerouting"
            return

        old_zone = drone.current_zone

        if old_zone is not None:
            old_zone.remove_nb_drone()

        target_zone.add_nb_drone()
        connection.add_nb_drone()
        drone.move_to_zone(target_zone)

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

        while True:
            path = self.ph.shortest_path(
                source=drone.current_zone,
                blocked_zones=blocked_zones,
                saturated_conns=saturated_connections,
            )

            if not path or len(path) < 2:
                drone.status = "waiting"
                return False

            next_zone = path[1]

            connection = self.graph.get_connection(
                drone.current_zone,
                next_zone,
            )

            if connection is None:
                blocked_zones.add(next_zone)
                continue

            # Vérification de la zone.
            zone_ok = (
                next_zone.nb_drone
                < next_zone.capacity
            )

            # Vérification de la connexion.
            conn_ok = (
                connection.nb_drones
                < connection.capacity
            )

            # La zone est pleine.
            if not zone_ok:
                blocked_zones.add(next_zone)
                continue

            # La connexion est pleine.
            # Ici on bloque LA CONNEXION, pas seulement la zone.
            if not conn_ok:
                saturated_connections.add(
                    (
                        connection.source,
                        connection.target,
                    )
                )
                continue

            # Le chemin est disponible.
            drone.path = path[1:].copy()
            drone.status = "idle"

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
            # Aucun chemin restant.
            if not drone.path:
                drone.status = "waiting"
                return

            target_zone = drone.path[0]

            connection = self.graph.get_connection(
                drone.current_zone,
                target_zone,
            )

            if connection is None:
                blocked_zones.add(target_zone)

                found = self._reroute_drone(
                    drone,
                    blocked_zones,
                    saturated_connections,
                )

                if not found:
                    drone.status = "waiting"

                continue

            old_zone = drone.current_zone

            # Tentative de déplacement.
            self.move_drone(
                drone,
                connection,
                target_zone,
            )

            # Déplacement impossible.
            if drone.status == "rerouting":

                # On regarde POURQUOI le déplacement est impossible.

                zone_ok = (
                    target_zone.nb_drone
                    < target_zone.capacity
                )

                conn_ok = (
                    connection.nb_drones
                    < connection.capacity
                )

                # Zone pleine.
                if not zone_ok:
                    blocked_zones.add(target_zone)

                # Connexion pleine.
                if not conn_ok:
                    saturated_connections.add(
                        (
                            connection.source,
                            connection.target,
                        )
                    )

                # Recherche d'un autre chemin.
                found = self._reroute_drone(
                    drone,
                    blocked_zones,
                    saturated_connections,
                )

                if not found:
                    drone.status = "waiting"
                    return

                # Nouveau chemin.
                continue
            # Déplacement normal terminé.
            if not drone.in_transit:

                if drone.current_zone == target_zone:
                    drone.path.pop(0)

                    movements[drone.drone_id] = (
                        f"{old_zone.name} -> "
                        f"{target_zone.name}"
                    )

                return

            # ------------------------------------------------------
            # Entrée dans une zone restricted.
            #
            # La zone est déjà réservée.
            # La connexion est déjà réservée.
            # ------------------------------------------------------
            movements[drone.drone_id] = (
                f"{old_zone.name} -> "
                f"{target_zone.name} [TRANSIT]"
            )

            return

    # SIMULATION

    def simulate(self) -> None:
        """Simule le déplacement des drones tour par tour."""

        while any(
            drone.current_zone != self.graph.end_zone
            for drone in self.drones
        ):
            movements: dict[str, str] = {}

            for drone in self.drones:
                # Drone arrivé.
                if drone.current_zone == self.graph.end_zone:
                    drone.status = "delivered"
                    continue
                # Drone déjà en transit.
                if drone.in_transit:

                    if drone.destination is None:
                        raise RuntimeError(
                            "Drone in transit without destination."
                        )

                    if drone.moving_connection is None:
                        raise RuntimeError(
                            "Drone in transit without connection."
                        )

                    target_zone = drone.destination
                    connection = drone.moving_connection
                    old_zone = drone.previous_zone

                    # Termine le transit.
                    self.move_drone(
                        drone,
                        connection,
                        target_zone,
                    )

                    if (
                        not drone.in_transit
                        and drone.current_zone == target_zone
                    ):
                        if drone.path:
                            drone.path.pop(0)

                        if old_zone is not None:
                            movements[drone.drone_id] = (
                                f"{old_zone.name} -> "
                                f"{target_zone.name}"
                            )

                    continue
                # Drone normal.
                self._try_drone_move(
                    drone,
                    movements,
                )
            # Fin du tour :
            # décrémente les connexions restricted occupées.

            for connection in list(
                self.restricted_connections
            ):
                self.restricted_connections[connection] -= 1

                if (
                    self.restricted_connections[connection]
                    <= 0
                ):
                    connection.remove_nb_drone()
                    del self.restricted_connections[
                        connection
                    ]
            # ------------------------------------------------------
            # Libère les connexions normales à la fin du tour.
            # ------------------------------------------------------
            for connection in self.graph.connections:
                if connection not in self.restricted_connections:
                    connection.nb_drones = 0
            # ------------------------------------------------------
            # Fin du tour.
            # ------------------------------------------------------
            self._print_turn(movements)
            self._record_tour()
            self.turn += 1

    # ==============================================================
    # RECORD
    # ==============================================================

    def _record_tour(self) -> None:
        """Enregistre l'état de la simulation pour le replay."""

        tour_data: dict[str, str | None] = {}
        drone_states: dict[str, dict[str, object]] = {}

        for drone in self.drones:

            if drone.current_zone is not None:
                tour_data[drone.drone_id] = (
                    drone.current_zone.name
                )
            else:
                tour_data[drone.drone_id] = None

            connection = drone.moving_connection

            drone_states[drone.drone_id] = {
                "zone": (
                    drone.current_zone.name
                    if drone.current_zone is not None
                    else None
                ),
                "status": drone.status,
                "destination": (
                    drone.destination.name
                    if drone.destination is not None
                    else None
                ),
                "connection": (
                    {
                        "source": connection.source.name,
                        "target": connection.target.name,
                    }
                    if connection is not None
                    else None
                ),
                "traveled_path": [
                    zone.name
                    for zone in drone.traveled_path
                ],
            }

        self.tours.append(tour_data)

        self.replay_frames.append(
            {
                "turn": self.turn,
                "drones": drone_states,
                "zones": {
                    name: {
                        "count": zone.nb_drone,
                        "max": zone.capacity,
                    }
                    for name, zone in self.graph.hubs.items()
                },
                "connections": {
                    (
                        f"{connection.source.name}"
                        f"->{connection.target.name}"
                    ): {
                        "source": connection.source.name,
                        "target": connection.target.name,
                        "count": connection.nb_drones,
                        "max": connection.capacity,
                    }
                    for connection in self.graph.connections
                },
            }
        )

    # ==============================================================
    # AFFICHAGE
    # ==============================================================

    def _print_turn(
        self,
        movements: dict[str, str],
    ) -> None:
        """Affiche l'état de chaque drone."""

        print()
        print("╔" + "═" * 62 + "╗")
        print(f"║ TURN {self.turn:<55}║")
        print("╠" + "═" * 62 + "╣")
        print("║ DRONES" + " " * 55 + "║")

        for drone in self.drones:

            if drone.status == "delivered":
                text = (
                    f"{drone.drone_id:<8} "
                    "DELIVERED"
                )

            else:
                movement = movements.get(
                    drone.drone_id
                )

                if movement:
                    text = (
                        f"{drone.drone_id:<8} "
                        f"{movement}"
                    )

                elif drone.in_transit:
                    text = (
                        f"{drone.drone_id:<8} "
                        "[TRANSIT]"
                    )

                else:
                    zone_name = (
                        drone.current_zone.name
                        if drone.current_zone is not None
                        else "UNKNOWN"
                    )

                    text = (
                        f"{drone.drone_id:<8} "
                        f"{zone_name} [WAIT]"
                    )

            print(f"║ {text:<60}║")

        print("╚" + "═" * 62 + "╝")
