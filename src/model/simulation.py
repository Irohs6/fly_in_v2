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

        self.ph = pathfinder if pathfinder is not None else Dijkstra(graph)

        self.tours: list[dict[str, str | None]] = []
        self.replay_frames: list[dict[str, object]] = []

    # ==============================================================
    # INITIALISATION
    # ==============================================================

    def load_drones(self, nb_drones: int) -> None:
        """Crée les drones dans le hub de départ."""

        if self.graph.start_zone is None:
            raise ValueError("Hub de départ introuvable.")

        path = self.ph.shortest_path()

        if not path:
            raise ValueError("Aucun chemin vers le hub final.")

        for index in range(nb_drones):
            drone = Drone(
                f"D_{index + 1}",
                current_zone=self.graph.start_zone,
            )

            drone.path = path.copy()
            self.drones.append(drone)

            self.graph.start_zone.add_nb_drone()

        self._record_tour()

    # ==============================================================
    # HUB
    # ==============================================================

    def _zone_available(self, zone: Hub) -> bool:
        """Vérifie si une zone possède encore une place."""

        if zone.zone_type == "blocked":
            return False

        return zone.nb_drone < zone.capacity

    def _zone_reserved(self, zone: Hub) -> int:
        """
        Retourne le nombre de drones actuellement en transit
        vers cette zone.
        """

        reserved = 0

        for drone in self.drones:
            if not drone.in_transit:
                continue

            if drone.destination is zone:
                reserved += 1

        return reserved

    def _zone_available_for_entry(self, zone: Hub) -> bool:
        """
        Vérifie la capacité réelle disponible.

        Les drones déjà en transit vers la zone sont considérés
        comme ayant déjà réservé une place.
        """

        if zone.zone_type == "blocked":
            return False

        occupied = zone.nb_drone
        reserved = self._zone_reserved(zone)

        return occupied + reserved < zone.capacity

    # ==============================================================
    # CONNECTION
    # ==============================================================

    def _connection_available(
        self,
        connection: Connection,
    ) -> bool:
        """Vérifie la capacité de la connexion pour ce tour."""

        return connection.nb_drones < connection.capacity

    def _connection_key(
        self,
        connection: Connection,
    ) -> tuple[str, str]:
        """Retourne une clé stable pour une connexion."""

        return tuple(
            sorted(
                (
                    connection.source.name,
                    connection.target.name,
                )
            )
        )

    # ==============================================================
    # DEPLACEMENT
    # ==============================================================

    def _step_available(
        self,
        current: Hub,
        next_zone: Hub,
    ) -> bool:
        """Vérifie si le prochain déplacement est possible."""

        connection = self.graph.get_connection(
            current.name,
            next_zone.name,
        )

        if connection is None:
            return False

        if not self._connection_available(connection):
            return False

        if next_zone.zone_type == "blocked":
            return False

        if next_zone.zone_type == "restricted":
            return self._zone_available_for_entry(next_zone)

        return self._zone_available_for_entry(next_zone)

    # ==============================================================
    # CHEMIN ACTUEL
    # ==============================================================

    def _try_current_path(
        self,
        drone: Drone,
    ) -> str | None:
        """
        Essaie le chemin que le drone possède déjà.

        Retourne le mouvement si celui-ci est possible.
        Retourne None si le prochain mouvement est bloqué.
        """

        if drone.current_zone is None:
            return None

        if len(drone.path) < 2:
            return None

        current = drone.current_zone
        next_zone = drone.path[1]

        if not self._step_available(current, next_zone):
            return None

        connection = self.graph.get_connection(
            current.name,
            next_zone.name,
        )

        if connection is None:
            return None

        if next_zone.zone_type == "restricted":
            return self._start_restricted_transit(
                drone,
                next_zone,
                connection,
            )

        return self._move_normal(
            drone,
            next_zone,
            connection,
        )

    # ==============================================================
    # CHEMINS ALTERNATIFS
    # ==============================================================

    def _find_alternative_path(
        self,
        drone: Drone,
    ) -> list[Hub]:
        """
        Cherche une alternative au chemin actuel.

        Chaque premier mouvement impossible est éliminé
        progressivement afin de laisser Dijkstra proposer
        une autre solution.
        """

        if drone.current_zone is None:
            return []

        current = drone.current_zone

        blocked_zones: set[str] = set()
        saturated_connections: set[tuple[str, str]] = set()

        attempts = 0
        max_attempts = max(
            1,
            len(self.graph.hubs),
        )

        while attempts < max_attempts:
            attempts += 1

            path = self.ph.shortest_path(
                source=current.name,
                blocked_zones=blocked_zones,
                saturated_conns=saturated_connections,
            )

            if not path:
                return []

            if len(path) < 2:
                return path

            next_zone = path[1]

            connection = self.graph.get_connection(
                current.name,
                next_zone.name,
            )

            if connection is None:
                blocked_zones.add(next_zone.name)
                continue

            if not self._connection_available(connection):
                saturated_connections.add(
                    self._connection_key(connection)
                )
                continue

            if not self._zone_available_for_entry(next_zone):
                blocked_zones.add(next_zone.name)
                continue

            return path

        return []

    # ==============================================================
    # ESSAI DU DRONE
    # ==============================================================

    def _try_move(
        self,
        drone: Drone,
    ) -> str | None:
        """
        Essaie le chemin actuel puis toutes les alternatives.

        Le drone ne passe en WAIT qu'après avoir épuisé
        toutes les solutions disponibles pour le tour.
        """

        if drone.current_zone is None:
            return None

        # ----------------------------------------------------------
        # 1. CHEMIN ACTUEL
        # ----------------------------------------------------------

        movement = self._try_current_path(drone)

        if movement is not None:
            return movement

        # ----------------------------------------------------------
        # 2. RECHERCHE DES ALTERNATIVES
        # ----------------------------------------------------------

        blocked_zones: set[str] = set()
        saturated_connections: set[tuple[str, str]] = set()

        current = drone.current_zone

        if len(drone.path) >= 2:
            old_next = drone.path[1]

            connection = self.graph.get_connection(
                current.name,
                old_next.name,
            )

            if connection is not None:
                if not self._connection_available(connection):
                    saturated_connections.add(
                        self._connection_key(connection)
                    )
                else:
                    blocked_zones.add(old_next.name)

        max_attempts = max(
            1,
            len(self.graph.hubs),
        )

        attempts = 0

        while attempts < max_attempts:
            attempts += 1

            path = self.ph.shortest_path(
                source=current.name,
                blocked_zones=blocked_zones,
                saturated_conns=saturated_connections,
            )

            if not path:
                break

            if len(path) < 2:
                drone.path = path
                return None

            next_zone = path[1]

            connection = self.graph.get_connection(
                current.name,
                next_zone.name,
            )

            # ------------------------------------------------------
            # CONNEXION INVALIDE
            # ------------------------------------------------------

            if connection is None:
                blocked_zones.add(next_zone.name)
                continue

            # ------------------------------------------------------
            # CONNEXION PLEINE
            # ------------------------------------------------------

            if not self._connection_available(connection):
                saturated_connections.add(
                    self._connection_key(connection)
                )
                continue

            # ------------------------------------------------------
            # ZONE INDISPONIBLE
            # ------------------------------------------------------

            if not self._zone_available_for_entry(next_zone):
                blocked_zones.add(next_zone.name)
                continue

            # ------------------------------------------------------
            # ALTERNATIVE VALIDE
            # ------------------------------------------------------

            drone.path = path

            if next_zone.zone_type == "restricted":
                return self._start_restricted_transit(
                    drone,
                    next_zone,
                    connection,
                )

            return self._move_normal(
                drone,
                next_zone,
                connection,
            )

        # ----------------------------------------------------------
        # PLUS AUCUNE SOLUTION
        # ----------------------------------------------------------

        return None

    # ==============================================================
    # MOUVEMENT NORMAL
    # ==============================================================

    def _move_normal(
        self,
        drone: Drone,
        next_zone: Hub,
        connection: Connection,
    ) -> str:
        """Déplace un drone vers une zone normale."""

        if drone.current_zone is None:
            return f"{drone.drone_id} WAIT"

        current = drone.current_zone

        current_name = current.name
        next_name = next_zone.name

        # La connexion est utilisée pendant ce tour.
        connection.add_drone()

        current.remove_nb_drone()

        drone.move_to_zone(
            next_zone,
            connection,
        )

        next_zone.add_nb_drone()

        drone.status = "moving"

        # Retire le premier élément du chemin.
        if len(drone.path) >= 2:
            drone.path = drone.path[1:]

        return f"{current_name} -> {next_name}"

    # ==============================================================
    # RESTRICTED
    # ==============================================================

    def _start_restricted_transit(
        self,
        drone: Drone,
        next_zone: Hub,
        connection: Connection,
    ) -> str:
        """Commence un déplacement vers une zone restricted."""

        if drone.current_zone is None:
            return f"{drone.drone_id} WAIT"

        if not self._connection_available(connection):
            return f"{drone.drone_id} WAIT"

        if not self._zone_available_for_entry(next_zone):
            return f"{drone.drone_id} WAIT"

        current_name = drone.current_zone.name

        connection.add_drone()

        drone.begin_transit(
            connection,
            1,
            next_zone,
        )

        drone.status = "in_transit"

        return (
            f"{current_name} -> "
            f"{next_zone.name} [TRANSIT]"
        )

    # ==============================================================
    # TRANSIT
    # ==============================================================

    def _continue_transit(
        self,
        drone: Drone,
    ) -> str:
        """Continue ou termine un transit."""

        connection = drone.moving_connection[1]
        destination = drone.destination

        if connection is None or destination is None:
            drone.in_transit = False
            drone.status = "waiting"
            return f"{drone.drone_id} WAIT"

        if drone.current_zone is None:
            drone.in_transit = False
            drone.status = "waiting"
            return f"{drone.drone_id} WAIT"

        drone.transit_turns += 1

        # ----------------------------------------------------------
        # TRANSIT PAS ENCORE TERMINE
        # ----------------------------------------------------------

        if drone.transit_turns < drone.transit_cost:
            return (
                f"{drone.current_zone.name} -> "
                f"{destination.name} [TRANSIT]"
            )

        # ----------------------------------------------------------
        # DESTINATION PLEINE
        # ----------------------------------------------------------

        reserved = self._zone_reserved(destination)

        # Le drone actuel fait partie des réservations.
        reserved -= 1

        if destination.nb_drone + reserved >= destination.capacity:
            drone.transit_turns -= 1

            return f"{drone.drone_id} WAIT"

        # ----------------------------------------------------------
        # ARRIVEE
        # ----------------------------------------------------------

        current_name = drone.current_zone.name
        destination_name = destination.name

        current = drone.current_zone

        current.remove_nb_drone()

        drone.finish_transit(destination)

        destination.add_nb_drone()

        drone.status = "moving"

        # La connexion sera reset à la fin du tour.
        # On ne la retire donc pas ici.

        if len(drone.path) >= 2:
            drone.path = drone.path[1:]

        return (
            f"{current_name} -> "
            f"{destination_name} [TRANSIT END]"
        )

    # ==============================================================
    # RESET DES CONNECTIONS
    # ==============================================================

    def _reset_connections(self) -> None:
        """
        Réinitialise l'utilisation des connexions.

        Une connexion représente une capacité de déplacement
        par tour, pas une occupation permanente.
        """

        for connection in self.graph.connections:
            connection.nb_drones = 0

    # ==============================================================
    # SIMULATION
    # ==============================================================

    def simulate(self) -> None:
        """Lance la simulation."""

        while not all(
            drone.status == "delivered"
            for drone in self.drones
        ):
            self.turn += 1

            movements: dict[str, str] = {}

            # ------------------------------------------------------
            # TRAITEMENT DES DRONES
            # ------------------------------------------------------

            for drone in self.drones:

                # --------------------------------------------------
                # DEJA ARRIVE
                # --------------------------------------------------

                if drone.current_zone is self.graph.end_zone:
                    drone.status = "delivered"
                    continue

                # --------------------------------------------------
                # TRANSIT
                # --------------------------------------------------

                if drone.in_transit:
                    movements[drone.drone_id] = (
                        self._continue_transit(drone)
                    )
                    continue

                # --------------------------------------------------
                # CHEMIN ACTUEL + ALTERNATIVES
                # --------------------------------------------------

                movement = self._try_move(drone)

                if movement is None:
                    drone.status = "waiting"

                    movements[drone.drone_id] = (
                        f"{drone.drone_id} WAIT"
                    )

            # ------------------------------------------------------
            # AFFICHAGE
            # ------------------------------------------------------

            self._print_turn(movements)

            # ------------------------------------------------------
            # ENREGISTREMENT
            # ------------------------------------------------------

            self._record_tour()

            # ------------------------------------------------------
            # FIN DU TOUR
            # ------------------------------------------------------

            self._reset_connections()

    # ==============================================================
    # RECORD
    # ==============================================================

    def _record_tour(self) -> None:
        """Enregistre la position des drones."""

        tour_data: dict[str, str | None] = {}

        for drone in self.drones:
            if drone.current_zone is not None:
                tour_data[drone.drone_id] = (
                    drone.current_zone.name
                )
            else:
                tour_data[drone.drone_id] = None

        self.tours.append(tour_data)

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
                    f"DELIVERED"
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
                        f"[TRANSIT]"
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