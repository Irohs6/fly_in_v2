from .drone import Drone
from .hub import Hub
from .connection import Connection
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
        drone_states = {
            drone.drone_id: self._drone_state(drone)
            for drone in drones
        }
        hub_states = {
            hub_id: HubReplayState(hub.nb_drone, hub.capacity)
            for hub_id, hub in hubs.items()
        }
        self.frames.append(ReplayFrame(turn, drone_states, hub_states))

    def _drone_state(
        self,
        drone: Drone,
    ) -> DroneReplayState:

        """Retourne l’état de replay du drone sur un hub ou en transit."""
        if isinstance(drone.current_position, Connection):
            return self._transit_state(drone)

        zone_name = drone.current_position.name

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
            or not isinstance(drone.current_position, Connection)
        ):
            raise RuntimeError(
                f"Invalid transit state for {drone.drone_id}."
            )

        source = drone.previous_zone

        target = drone.current_position.get_extremities(source)

        progress = 0.0

        if drone.transit_duration > 0:
            progress = (
                drone.transit_turns
                / drone.transit_duration
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
