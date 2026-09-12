from .hub import Hub
from .connection import Connection


class Drone:
    """Drone avec position, chemin restant et état de transit.

    Les compteurs de hubs et de connexions sont gérés par Simulation.
    """
    def __init__(
        self,
        drone_id: int,
        current_position: Hub
    ) -> None:
        """Place le drone dans un hub, sans chemin ni transit."""
        self.drone_id = drone_id

        self.current_position: Hub | Connection = current_position
        self.previous_zone: Hub | None = None

        self.path: list[Hub] = []
        self.status: str = "idle"

        self.transit_duration = 0
        self.transit_turns = 0

    def move_to_zone(
        self,
        zone: Hub,
    ) -> None:
        """Déplace le drone vers zone et retire cette étape de son chemin.

        Mémorise le hub précédent et passe le statut à moving. Lève
        RuntimeError si le drone n’est pas actuellement dans un hub.
        """
        if isinstance(self.current_position, Connection):
            raise RuntimeError(
                f"Drone {self.drone_id} is not currently in any hub."
            )
        self.previous_zone = self.current_position
        self.current_position = zone

        self.path.pop(0)

        self.status = "moving"

    def begin_transit(
        self,
        connection: Connection,
        duration: int,
    ) -> None:
        """Commence le premier des duration tours sur connection.

        Le hub actuel devient le hub précédent et la connexion devient
        la position courante. Lève RuntimeError sans hub de départ.
        Les réservations et capacités sont gérées par Simulation.
        """
        if isinstance(self.current_position, Connection):
            raise RuntimeError(
                f"Drone {self.drone_id} is already in transit."
            )
        self.previous_zone = self.current_position
        self.current_position = connection
        self.transit_duration = duration
        # Le tour de départ compte comme premier tour de transit.
        self.transit_turns = 1
        self.status = "in_transit"

    def advance_transit(self) -> Hub | None:
        """Avance le transit d’un tour et retourne le hub atteint.

        Retourne None si le drone n’est pas en transit ou si le trajet
        n’est pas terminé.
        """
        if not isinstance(self.current_position, Connection):
            return None

        self.transit_turns += 1

        if self.transit_turns < self.transit_duration:
            return None

        return self.finish_transit()

    def finish_transit(self) -> Hub:
        """Place le drone à destination et réinitialise son état de transit.

        Retourne le hub atteint après avoir consommé l’étape du chemin.
        Lève RuntimeError si la connexion ou le hub de départ manque.
        """
        if not isinstance(self.current_position,
                          Connection) or self.previous_zone is None:

            raise RuntimeError(
                f"Drone {self.drone_id}: missing connection or departure hub."
            )

        destination = self.current_position.get_extremities(
            self.previous_zone)
        self.current_position = destination
        self.path.pop(0)
        self.status = "moving"

        self.transit_duration = 0
        self.transit_turns = 0
        return destination

    def wait(self) -> None:
        """Marque le drone en attente sans changer sa position."""
        self.status = "waiting"

    def moving(self) -> None:
        """Marque le drone comme mobile sans effectuer de déplacement."""
        self.status = "moving"

    def deliver(self) -> None:
        """Marque le drone comme livré sans modifier sa position."""
        self.status = "delivered"

    def path_turns(self) -> int:
        """Additionne les durées des hubs restant dans le chemin.

        Le temps déjà passé en transit n’est pas retranché de cette
        estimation.
        """
        return sum(
            zone.transit_duration()
            for zone in self.path
        )

    def set_path(self, path: list[Hub]) -> None:
        """Remplace le chemin restant par une copie de path."""
        self.path = path.copy()
