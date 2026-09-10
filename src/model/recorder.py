from .drone import Drone
from .hub import Hub
from .replay import (
    DroneReplayState,
    HubReplayState,
    ReplayFrame,
)


class Recorder:

    """Collecte les états des drones et hubs pour le replay."""
    def __init__(self) -> None:
        """Prépare une liste vide de frames enregistrées."""
        self.frames: list[ReplayFrame] = []

    def record(
        self,
        turn: int,
        drones: list[Drone],
        hubs: dict[str, Hub],
    ) -> None:
        """Ajoute une frame du tour avec les états courants des drones et
        hubs.

        Les valeurs sont copiées dans des états de replay indépendants des
        objets métier. Le graphe et les drones ne sont pas modifiés.
        """
        drone_states: dict[int, DroneReplayState] = {}

        for drone in drones:
            state = self._drone_state(drone)

            drone_states[drone.drone_id] = state

        hub_states: dict[str, HubReplayState] = {}

        for hub_id, hub in hubs.items():
            hub_states[hub_id] = HubReplayState(
                nb_drones=hub.nb_drone,
                capacity=hub.capacity,
            )

        frame = ReplayFrame(
            turn=turn,
            drones=drone_states,
            hubs=hub_states,
        )

        self.frames.append(frame)

    def _drone_state(
        self,
        drone: Drone,
    ) -> DroneReplayState:

        """Retourne l’état de replay du drone sur un hub ou en transit.

        Lève RuntimeError si le drone n’a ni transit actif ni hub courant.
        """
        if drone.in_transit:
            return self._transit_state(drone)

        if drone.current_zone is None:
            raise RuntimeError(
                f"{drone.drone_id} has no current zone."
            )

        zone_name = drone.current_zone.name

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

        """Retourne les extrémités et la progression du transit entre 0 et 1.

        Lève RuntimeError si le hub précédent ou la connexion est absent.
        """
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
            source=source.name,
            target=target.name,
            progress=progress,
            status=drone.status,
        )
