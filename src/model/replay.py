from dataclasses import dataclass


@dataclass
class DroneReplayState:
    source: str
    target: str
    progress: float
    status: str


@dataclass
class HubReplayState:
    nb_drones: int
    capacity: int


@dataclass
class ReplayFrame:
    turn: int
    drones: dict[str, DroneReplayState]
    hubs: dict[str, HubReplayState]