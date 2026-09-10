from dataclasses import dataclass


@dataclass
class DroneReplayState:
    """Position et statut enregistrés d’un drone.

    source et target sont des noms de hubs ; ils sont identiques à l’arrêt.
    progress décrit la fraction de la connexion parcourue, entre 0 et 1.
    """
    source: str
    target: str
    progress: float
    status: str


@dataclass
class HubReplayState:
    """Occupation et capacité d’un hub à un tour donné."""
    nb_drones: int
    capacity: int | float


@dataclass
class ReplayFrame:
    """Instantané d’un tour, avec états indexés par drone et nom de hub."""
    turn: int
    drones: dict[int, DroneReplayState]
    hubs: dict[str, HubReplayState]
