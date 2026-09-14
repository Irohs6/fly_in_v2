from dataclasses import dataclass


@dataclass
class DroneReplayState:
    """Recorded drone position and status. source and target are hub names
    and match when the drone is in a hub. progress is the fraction of the
    connection traversed, between zero and one.
    """
    source: str
    target: str
    progress: float
    status: str


@dataclass
class HubReplayState:
    """Hub occupancy and capacity at a given turn."""
    nb_drones: int
    capacity: int | float


@dataclass
class ReplayFrame:
    """Turn snapshot with states indexed by drone ID and hub name."""
    turn: int
    drones: dict[int, DroneReplayState]
    hubs: dict[str, HubReplayState]
